use std::io::Read;
use std::io::Result as IoResult;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::mpsc::channel;
use std::sync::mpsc::{Receiver, Sender};
use std::sync::Arc;

/// 请求体没读完时,最多替下一条请求跳过这么多字节(超过就不读了,直接关连接)。
/// 1 MiB 多一点:常见请求体上限之上留余量,够把「读到上限即回 413」剩下的尾巴吃掉。
pub const DRAIN_LIMIT: usize = (1 << 20) + (64 << 10);

/// 一条请求的「体收尾」状态:请求对象、体读取器与连接线程三方共享。
///
/// 体读取器被丢弃时只记下还没读的字节数(丢弃它的线程零阻塞、零分配),由连接线程在读下一条请求之前跳过;
/// 没读的量超过 [`DRAIN_LIMIT`]、长度未知的分块体没读完、或本次回应声明了关连接时置「必须关闭」,
/// 连接线程看到就直接关连接 —— 这条连接上的剩余字节永远不会被当成下一条请求解析。
#[derive(Debug, Default)]
pub struct BodyTail {
    unread: AtomicUsize,
    must_close: AtomicBool,
}

impl BodyTail {
    pub fn new() -> Arc<BodyTail> {
        Arc::new(BodyTail::default())
    }

    /// 本次回应之后关连接(不再读下一条请求)。
    pub fn close_after(&self) {
        self.must_close.store(true, Ordering::SeqCst);
    }

    pub fn must_close(&self) -> bool {
        self.must_close.load(Ordering::SeqCst)
    }

    /// 体读取器丢弃时还没读的字节数(连接线程负责跳过)。
    pub fn unread(&self) -> usize {
        self.unread.load(Ordering::SeqCst)
    }

    fn leave_unread(&self, remaining: usize) {
        if remaining > DRAIN_LIMIT {
            self.close_after();
        } else {
            self.unread.store(remaining, Ordering::SeqCst);
        }
    }
}

/// A `Reader` that reads exactly the number of bytes from a sub-reader.
///
/// If the limit is reached, it returns EOF. If the limit is not reached
/// when the destructor is called, the remaining bytes are handed over to the
/// connection (see [`BodyTail`]); without a tail they are read and thrown away,
/// up to [`DRAIN_LIMIT`] bytes, with a fixed-size buffer.
pub struct EqualReader<R>
where
    R: Read,
{
    reader: R,
    size: usize,
    last_read_signal: Sender<IoResult<()>>,
    tail: Option<Arc<BodyTail>>,
}

impl<R> EqualReader<R>
where
    R: Read,
{
    pub fn new(reader: R, size: usize) -> (EqualReader<R>, Receiver<IoResult<()>>) {
        let (tx, rx) = channel();

        let r = EqualReader {
            reader,
            size,
            last_read_signal: tx,
            tail: None,
        };

        (r, rx)
    }

    /// 挂上收尾状态:此后丢弃时不在本线程读剩余字节,改由连接线程处理。
    pub fn with_tail(mut self, tail: Arc<BodyTail>) -> Self {
        self.tail = Some(tail);
        self
    }
}

impl<R> Read for EqualReader<R>
where
    R: Read,
{
    fn read(&mut self, buf: &mut [u8]) -> IoResult<usize> {
        if self.size == 0 {
            return Ok(0);
        }

        let buf = if buf.len() < self.size {
            buf
        } else {
            &mut buf[..self.size]
        };

        match self.reader.read(buf) {
            Ok(len) => {
                self.size -= len;
                Ok(len)
            }
            err @ Err(_) => err,
        }
    }
}

impl<R> Drop for EqualReader<R>
where
    R: Read,
{
    fn drop(&mut self) {
        if self.size == 0 {
            return;
        }
        // 剩余长度来自客户端声明的 Content-Length(可以是任意大的数):绝不按它一次性申请缓冲
        if let Some(tail) = self.tail.as_ref() {
            tail.leave_unread(self.size);
            return;
        }
        if self.size > DRAIN_LIMIT {
            self.last_read_signal
                .send(Err(std::io::Error::new(
                    std::io::ErrorKind::InvalidData,
                    "request body too large to drain",
                )))
                .ok();
            return;
        }

        let mut remaining_to_read = self.size;
        let mut buf = [0u8; 8192];

        while remaining_to_read > 0 {
            let want = remaining_to_read.min(buf.len());
            match self.reader.read(&mut buf[..want]) {
                Err(e) => {
                    self.last_read_signal.send(Err(e)).ok();
                    break;
                }
                Ok(0) => {
                    self.last_read_signal.send(Ok(())).ok();
                    break;
                }
                Ok(other) => {
                    remaining_to_read -= other;
                }
            }
        }
    }
}

/// 分块请求体的收尾看守:分块体的剩余长度未知,没读到结尾就被丢弃 ⇒ 这条连接只能关闭。
pub struct ChunkedTail<R>
where
    R: Read,
{
    inner: R,
    finished: bool,
    tail: Arc<BodyTail>,
}

impl<R> ChunkedTail<R>
where
    R: Read,
{
    pub fn new(inner: R, tail: Arc<BodyTail>) -> Self {
        ChunkedTail {
            inner,
            finished: false,
            tail,
        }
    }
}

impl<R> Read for ChunkedTail<R>
where
    R: Read,
{
    fn read(&mut self, buf: &mut [u8]) -> IoResult<usize> {
        let n = self.inner.read(buf)?;
        if n == 0 && !buf.is_empty() {
            self.finished = true;
        }
        Ok(n)
    }
}

impl<R> Drop for ChunkedTail<R>
where
    R: Read,
{
    fn drop(&mut self) {
        if !self.finished {
            self.tail.close_after();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{BodyTail, EqualReader, DRAIN_LIMIT};
    use std::io::Read;

    #[test]
    fn test_limit() {
        use std::io::Cursor;

        let mut org_reader = Cursor::new("hello world".to_string().into_bytes());

        {
            let (mut equal_reader, _) = EqualReader::new(org_reader.by_ref(), 5);

            let mut string = String::new();
            equal_reader.read_to_string(&mut string).unwrap();
            assert_eq!(string, "hello");
        }

        let mut string = String::new();
        org_reader.read_to_string(&mut string).unwrap();
        assert_eq!(string, " world");
    }

    #[test]
    fn test_not_enough() {
        use std::io::Cursor;

        let mut org_reader = Cursor::new("hello world".to_string().into_bytes());

        {
            let (mut equal_reader, _) = EqualReader::new(org_reader.by_ref(), 5);

            let mut vec = [0];
            equal_reader.read_exact(&mut vec).unwrap();
            assert_eq!(vec[0], b'h');
        }

        let mut string = String::new();
        org_reader.read_to_string(&mut string).unwrap();
        assert_eq!(string, " world");
    }

    #[test]
    fn test_huge_declared_length_does_not_allocate_or_read() {
        use std::io::Cursor;

        let mut org_reader = Cursor::new("hello world".to_string().into_bytes());
        {
            let (_r, _) = EqualReader::new(org_reader.by_ref(), usize::MAX);
        }
        assert_eq!(org_reader.position(), 0);

        let tail = BodyTail::new();
        {
            let (r, _) = EqualReader::new(org_reader.by_ref(), DRAIN_LIMIT + 1);
            let _r = r.with_tail(tail.clone());
        }
        assert!(tail.must_close());
        assert_eq!(org_reader.position(), 0);
    }

    #[test]
    fn test_tail_records_unread_without_reading() {
        use std::io::Cursor;

        let mut org_reader = Cursor::new("hello world".to_string().into_bytes());
        let tail = BodyTail::new();
        {
            let (r, _) = EqualReader::new(org_reader.by_ref(), 5);
            let mut r = r.with_tail(tail.clone());
            let mut one = [0];
            r.read_exact(&mut one).unwrap();
        }
        assert_eq!(tail.unread(), 4);
        assert!(!tail.must_close());
        assert_eq!(org_reader.position(), 1);
    }
}
