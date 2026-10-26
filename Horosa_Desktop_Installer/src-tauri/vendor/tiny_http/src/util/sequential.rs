use std::io::Result as IoResult;
use std::io::{Read, Write};

use std::sync::mpsc::channel;
use std::sync::mpsc::{Receiver, Sender};
use std::sync::{Arc, Mutex};

use std::mem;

pub struct SequentialReaderBuilder<R>
where
    R: Read + Send,
{
    inner: SequentialReaderBuilderInner<R>,
}

enum SequentialReaderBuilderInner<R>
where
    R: Read + Send,
{
    First(R),
    NotFirst(Receiver<R>),
}

pub struct SequentialReader<R>
where
    R: Read + Send,
{
    inner: SequentialReaderInner<R>,
    next: Sender<R>,
}

enum SequentialReaderInner<R>
where
    R: Read + Send,
{
    MyTurn(R),
    Waiting(Receiver<R>),
    Empty,
}

pub struct SequentialWriterBuilder<W>
where
    W: Write + Send,
{
    writer: Arc<Mutex<W>>,
    next_trigger: Option<Receiver<()>>,
}

pub struct SequentialWriter<W>
where
    W: Write + Send,
{
    trigger: Option<Receiver<()>>,
    writer: Arc<Mutex<W>>,
    on_finish: Sender<()>,
}

impl<R: Read + Send> SequentialReaderBuilder<R> {
    pub fn new(reader: R) -> SequentialReaderBuilder<R> {
        SequentialReaderBuilder {
            inner: SequentialReaderBuilderInner::First(reader),
        }
    }
}

impl<W: Write + Send> SequentialWriterBuilder<W> {
    pub fn new(writer: W) -> SequentialWriterBuilder<W> {
        SequentialWriterBuilder {
            writer: Arc::new(Mutex::new(writer)),
            next_trigger: None,
        }
    }

    /// 共享的底层写口(连接级「关连接」钩子按它找到 socket)。
    pub fn shared_writer(&self) -> Arc<Mutex<W>> {
        self.writer.clone()
    }
}

impl<R: Read + Send> SequentialReader<R> {
    /// 阻塞到轮到本读取器为止(上一个读取器被丢弃、把底层流交过来)。
    /// 返回 false = 上一个读取器没交接就没了,底层流已不可用。
    pub fn wait_turn(&mut self) -> bool {
        let reader = match self.inner {
            SequentialReaderInner::MyTurn(_) => return true,
            SequentialReaderInner::Waiting(ref mut recv) => match recv.recv() {
                Ok(reader) => reader,
                Err(_) => return false,
            },
            SequentialReaderInner::Empty => return false,
        };
        self.inner = SequentialReaderInner::MyTurn(reader);
        true
    }
}

impl<R: Read + Send> Iterator for SequentialReaderBuilder<R> {
    type Item = SequentialReader<R>;

    fn next(&mut self) -> Option<SequentialReader<R>> {
        let (tx, rx) = channel();

        let inner = mem::replace(&mut self.inner, SequentialReaderBuilderInner::NotFirst(rx));

        match inner {
            SequentialReaderBuilderInner::First(reader) => Some(SequentialReader {
                inner: SequentialReaderInner::MyTurn(reader),
                next: tx,
            }),

            SequentialReaderBuilderInner::NotFirst(previous) => Some(SequentialReader {
                inner: SequentialReaderInner::Waiting(previous),
                next: tx,
            }),
        }
    }
}

impl<W: Write + Send> Iterator for SequentialWriterBuilder<W> {
    type Item = SequentialWriter<W>;
    fn next(&mut self) -> Option<SequentialWriter<W>> {
        let (tx, rx) = channel();
        let mut next_next_trigger = Some(rx);
        ::std::mem::swap(&mut next_next_trigger, &mut self.next_trigger);

        Some(SequentialWriter {
            trigger: next_next_trigger,
            writer: self.writer.clone(),
            on_finish: tx,
        })
    }
}

impl<R: Read + Send> Read for SequentialReader<R> {
    fn read(&mut self, buf: &mut [u8]) -> IoResult<usize> {
        let mut reader = match self.inner {
            SequentialReaderInner::MyTurn(ref mut reader) => return reader.read(buf),
            SequentialReaderInner::Waiting(ref mut recv) => match recv.recv() {
                Ok(reader) => reader,
                Err(_) => {
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::ConnectionAborted,
                        "previous reader dropped without handing over the stream",
                    ))
                }
            },
            SequentialReaderInner::Empty => {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::ConnectionAborted,
                    "reader already released",
                ))
            }
        };

        let result = reader.read(buf);
        self.inner = SequentialReaderInner::MyTurn(reader);
        result
    }
}

impl<W: Write + Send> Write for SequentialWriter<W> {
    fn write(&mut self, buf: &[u8]) -> IoResult<usize> {
        if let Some(v) = self.trigger.as_mut() {
            // 上一个写口丢弃即放行;它若没发信号就没了,同样放行(不 panic)
            let _ = v.recv();
        }
        self.trigger = None;

        self.writer.lock().unwrap().write(buf)
    }

    fn flush(&mut self) -> IoResult<()> {
        if let Some(v) = self.trigger.as_mut() {
            // 上一个写口丢弃即放行;它若没发信号就没了,同样放行(不 panic)
            let _ = v.recv();
        }
        self.trigger = None;

        self.writer.lock().unwrap().flush()
    }
}

impl<R> Drop for SequentialReader<R>
where
    R: Read + Send,
{
    fn drop(&mut self) {
        let inner = mem::replace(&mut self.inner, SequentialReaderInner::Empty);

        match inner {
            SequentialReaderInner::MyTurn(reader) => {
                self.next.send(reader).ok();
            }
            SequentialReaderInner::Waiting(recv) => {
                if let Ok(reader) = recv.recv() {
                    self.next.send(reader).ok();
                }
            }
            SequentialReaderInner::Empty => (),
        }
    }
}

impl<W> Drop for SequentialWriter<W>
where
    W: Write + Send,
{
    fn drop(&mut self) {
        self.on_finish.send(()).ok();
    }
}
