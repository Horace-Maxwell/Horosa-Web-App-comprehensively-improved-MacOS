use ascii::AsciiString;

use std::io::Error as IoError;
use std::io::Result as IoResult;
use std::io::{BufReader, BufWriter, ErrorKind, Read, Write};

use std::net::SocketAddr;
use std::str::FromStr;
use std::sync::Arc;
use std::time::{Duration, Instant};

use crate::common::{HTTPVersion, Method};
use crate::request::ConnectionCloser;
use crate::util::{BodyTail, RefinedTcpStream};
use crate::util::{SequentialReader, SequentialReaderBuilder, SequentialWriterBuilder};
use crate::Request;

/// 请求行 + 全部请求头的总字节上限:超限回 431 并关连接(不再无上限地攒一行)。
const MAX_HEAD_BYTES: usize = 64 * 1024;
/// 从收到一条请求的首字节起,请求行 + 头必须在这段时间内收齐(防逐字节慢喂长期占住连接线程)。
const HEAD_DEADLINE: Duration = Duration::from_secs(30);
/// 替上一条请求跳过没读完的体,最多花这么久(超时即关连接)。
const DRAIN_DEADLINE: Duration = Duration::from_secs(30);

/// 一条请求头的读取预算:总字节上限 + 首字节起算的截止时间。
struct HeadBudget {
    left: usize,
    deadline: Option<Instant>,
}

impl HeadBudget {
    fn new() -> HeadBudget {
        HeadBudget {
            left: MAX_HEAD_BYTES,
            deadline: None,
        }
    }

    fn started(&self) -> bool {
        self.deadline.is_some()
    }

    fn take_byte(&mut self) -> Result<(), ReadError> {
        if self.left == 0 {
            return Err(ReadError::HeadTooLarge);
        }
        self.left -= 1;
        match self.deadline {
            None => self.deadline = Some(Instant::now() + HEAD_DEADLINE),
            Some(d) if Instant::now() > d => {
                return Err(ReadError::ReadIoError(IoError::new(
                    ErrorKind::TimedOut,
                    "request head not received in time",
                )))
            }
            Some(_) => {}
        }
        Ok(())
    }
}

/// 套接字读超时:macOS / Linux 回 WouldBlock,Windows 回 TimedOut。
fn is_timeout(err: &IoError) -> bool {
    matches!(err.kind(), ErrorKind::WouldBlock | ErrorKind::TimedOut)
}

/// A ClientConnection is an object that will store a socket to a client
/// and return Request objects.
pub struct ClientConnection {
    // address of the client
    remote_addr: IoResult<Option<SocketAddr>>,

    // sequence of Readers to the stream, so that the data is not read in
    //  the wrong order
    source: SequentialReaderBuilder<BufReader<RefinedTcpStream>>,

    // sequence of Writers to the stream, to avoid writing response #2 before
    //  response #1
    sink: SequentialWriterBuilder<BufWriter<RefinedTcpStream>>,

    // Reader to read the next header from
    next_header_source: SequentialReader<BufReader<RefinedTcpStream>>,

    // set to true if we know that the previous request is the last one
    no_more_requests: bool,

    // true if the connection goes through SSL
    secure: bool,

    // 上一条请求的体收尾状态:读下一条请求之前据此跳过没读完的体,或直接关连接
    prev_tail: Option<Arc<BodyTail>>,

    // 关闭本连接的钩子(交给每条请求;升级出去的流结束时调用)
    closer: ConnectionCloser,
}

/// Error that can happen when reading a request.
#[derive(Debug)]
enum ReadError {
    WrongRequestLine,
    WrongHeader(HTTPVersion),
    /// the client sent an unrecognized `Expect` header
    ExpectationFailed(HTTPVersion),
    /// 请求行 + 头超过 MAX_HEAD_BYTES
    HeadTooLarge,
    /// 空闲等下一条请求时读超时(一个字节都没收到):静默关连接,不回 408
    Idle,
    /// 上一条请求要求关连接(或它没读完的体无法跳过):静默关连接
    Closing,
    ReadIoError(IoError),
}

impl ClientConnection {
    /// Creates a new `ClientConnection` that takes ownership of the `TcpStream`.
    pub fn new(
        write_socket: RefinedTcpStream,
        mut read_socket: RefinedTcpStream,
    ) -> ClientConnection {
        let remote_addr = read_socket.peer_addr();
        let secure = read_socket.secure();

        let mut source = SequentialReaderBuilder::new(BufReader::with_capacity(1024, read_socket));
        let first_header = source.next().unwrap();
        let sink = SequentialWriterBuilder::new(BufWriter::with_capacity(1024, write_socket));
        let shared = Arc::downgrade(&sink.shared_writer());
        let closer: ConnectionCloser = Arc::new(move || {
            if let Some(writer) = shared.upgrade() {
                if let Ok(mut w) = writer.lock() {
                    let _ = w.flush();
                    w.get_mut().shutdown_both();
                }
            }
        });

        ClientConnection {
            source,
            sink,
            remote_addr,
            next_header_source: first_header,
            no_more_requests: false,
            secure,
            prev_tail: None,
            closer,
        }
    }

    /// true if the connection is HTTPS
    pub fn secure(&self) -> bool {
        self.secure
    }

    /// Reads the next line from self.next_header_source.
    ///
    /// Reads until `CRLF` is reached. The next read will start
    ///  at the first byte of the new line.
    /// 每个字节都记入本条请求头的预算(总长上限 + 截止时间)。
    fn read_next_line(&mut self, budget: &mut HeadBudget) -> Result<AsciiString, ReadError> {
        let mut buf = Vec::new();
        let mut prev_byte_was_cr = false;

        loop {
            let byte = self.next_header_source.by_ref().bytes().next();

            let byte = match byte {
                Some(Ok(b)) => b,
                Some(Err(e)) if is_timeout(&e) && !budget.started() => return Err(ReadError::Idle),
                Some(Err(e)) if is_timeout(&e) => {
                    return Err(ReadError::ReadIoError(IoError::new(ErrorKind::TimedOut, e)))
                }
                Some(Err(e)) => return Err(ReadError::ReadIoError(e)),
                None => {
                    return Err(ReadError::ReadIoError(IoError::new(
                        ErrorKind::ConnectionAborted,
                        "Unexpected EOF",
                    )))
                }
            };
            budget.take_byte()?;

            if byte == b'\n' && prev_byte_was_cr {
                buf.pop(); // removing the '\r'
                return AsciiString::from_ascii(buf).map_err(|_| {
                    ReadError::ReadIoError(IoError::new(
                        ErrorKind::InvalidInput,
                        "Header is not in ASCII",
                    ))
                });
            }

            prev_byte_was_cr = byte == b'\r';

            buf.push(byte);
        }
    }

    /// 跳过上一条请求没读完的体(固定 8 KiB 缓冲,总量不超过 DRAIN_LIMIT,限时 DRAIN_DEADLINE)。
    /// 返回 false = 没能跳完(读错 / 提前 EOF / 超时),连接已不可复用。
    fn skip_unread_body(&mut self, mut left: usize) -> bool {
        let deadline = Instant::now() + DRAIN_DEADLINE;
        let mut buf = [0u8; 8192];
        while left > 0 {
            if Instant::now() > deadline {
                return false;
            }
            let want = left.min(buf.len());
            match self.next_header_source.read(&mut buf[..want]) {
                Ok(0) | Err(_) => return false,
                Ok(n) => left -= n.min(left),
            }
        }
        true
    }

    /// 轮到本连接读下一条请求前的收尾:等上一条请求的体读取器交还连接,再按它留下的状态
    /// 跳过没读完的体,或(要求关闭 / 跳不完)直接关连接。
    fn settle_previous(&mut self) -> Result<(), ReadError> {
        if !self.next_header_source.wait_turn() {
            return Err(ReadError::Closing);
        }
        if let Some(tail) = self.prev_tail.as_ref() {
            if tail.must_close() {
                return Err(ReadError::Closing);
            }
            let unread = tail.unread();
            if unread > 0 {
                if !self.skip_unread_body(unread) {
                    return Err(ReadError::Closing);
                }
                // 已跳过;上一条请求的回应稍后仍可能声明关连接,收尾状态留着下面再看
            }
        }
        Ok(())
    }

    /// Reads a request from the stream.
    /// Blocks until the header has been read.
    fn read(&mut self) -> Result<Request, ReadError> {
        self.settle_previous()?;
        let mut budget = HeadBudget::new();
        let (method, path, version, headers) = {
            // reading the request line
            let (method, path, version) = {
                let line = self.read_next_line(&mut budget)?;

                parse_request_line(
                    line.as_str().trim(), // TODO: remove this conversion
                )?
            };

            // getting all headers
            let headers = {
                let mut headers = Vec::new();
                loop {
                    let line = self.read_next_line(&mut budget)?;

                    if line.is_empty() {
                        break;
                    };
                    headers.push(match FromStr::from_str(line.as_str().trim()) {
                        // TODO: remove this conversion
                        Ok(h) => h,
                        _ => return Err(ReadError::WrongHeader(version)),
                    });
                }

                headers
            };

            (method, path, version, headers)
        };

        // 上一条请求的回应可能在本条请求头到达之前才声明关连接(小体请求的读取器在建请求时就已交还):
        // 头读完再看一眼,声明过就不再受理本条
        if self
            .prev_tail
            .as_ref()
            .map(|t| t.must_close())
            .unwrap_or(false)
        {
            return Err(ReadError::Closing);
        }

        // building the writer for the request
        let writer = self.sink.next().unwrap();

        // follow-up for next potential request
        let mut data_source = self.source.next().unwrap();
        std::mem::swap(&mut self.next_header_source, &mut data_source);

        // building the next reader
        let request = crate::request::new_request(
            self.secure,
            method,
            path,
            version.clone(),
            headers,
            self.remote_addr.as_ref().ok().copied().flatten(),
            data_source,
            writer,
        )
        .map_err(|e| {
            use crate::request;
            match e {
                request::RequestCreationError::CreationIoError(e) => ReadError::ReadIoError(e),
                request::RequestCreationError::ExpectationFailed => {
                    ReadError::ExpectationFailed(version)
                }
            }
        })?;
        let request = request.with_connection_closer(Arc::clone(&self.closer));
        self.prev_tail = Some(request.body_tail());

        // return the request
        Ok(request)
    }
}

impl Iterator for ClientConnection {
    type Item = Request;

    /// Blocks until the next Request is available.
    /// Returns None when no new Requests will come from the client.
    fn next(&mut self) -> Option<Request> {
        use crate::{Response, StatusCode};

        // the client sent a "connection: close" header in this previous request
        //  or is using HTTP 1.0, meaning that no new request will come
        if self.no_more_requests {
            return None;
        }

        loop {
            let rq = match self.read() {
                Err(ReadError::WrongRequestLine) => {
                    let writer = self.sink.next().unwrap();
                    let response = Response::new_empty(StatusCode(400));
                    response
                        .raw_print(writer, HTTPVersion(1, 1), &[], false, None)
                        .ok();
                    return None; // we don't know where the next request would start,
                                 // se we have to close
                }

                Err(ReadError::WrongHeader(ver)) => {
                    let writer = self.sink.next().unwrap();
                    let response = Response::new_empty(StatusCode(400));
                    response.raw_print(writer, ver, &[], false, None).ok();
                    return None; // we don't know where the next request would start,
                                 // se we have to close
                }

                Err(ReadError::HeadTooLarge) => {
                    let writer = self.sink.next().unwrap();
                    let response = Response::new_empty(StatusCode(431));
                    response
                        .raw_print(writer, HTTPVersion(1, 1), &[], false, None)
                        .ok();
                    return None; // 头没读完就停了,不知道下一条请求从哪开始:只能关连接
                }

                Err(ReadError::Idle) | Err(ReadError::Closing) => return None,

                Err(ReadError::ReadIoError(ref err)) if is_timeout(err) => {
                    // request timeout
                    let writer = self.sink.next().unwrap();
                    let response = Response::new_empty(StatusCode(408));
                    response
                        .raw_print(writer, HTTPVersion(1, 1), &[], false, None)
                        .ok();
                    return None; // closing the connection
                }

                Err(ReadError::ExpectationFailed(ver)) => {
                    let writer = self.sink.next().unwrap();
                    let response = Response::new_empty(StatusCode(417));
                    response.raw_print(writer, ver, &[], true, None).ok();
                    return None; // TODO: should be recoverable, but needs handling in case of body
                }

                Err(ReadError::ReadIoError(_)) => return None,

                Ok(rq) => rq,
            };

            // checking HTTP version
            if *rq.http_version() > (1, 1) {
                let writer = self.sink.next().unwrap();
                let response = Response::from_string(
                    "This server only supports HTTP versions 1.0 and 1.1".to_owned(),
                )
                .with_status_code(StatusCode(505));
                response
                    .raw_print(writer, HTTPVersion(1, 1), &[], false, None)
                    .ok();
                continue;
            }

            // updating the status of the connection
            let connection_header = rq
                .headers()
                .iter()
                .find(|h| h.field.equiv("Connection"))
                .map(|h| h.value.as_str());

            let lowercase = connection_header.map(|h| h.to_ascii_lowercase());

            match lowercase {
                Some(ref val) if val.contains("close") => self.no_more_requests = true,
                Some(ref val) if val.contains("upgrade") => self.no_more_requests = true,
                Some(ref val)
                    if !val.contains("keep-alive") && *rq.http_version() == HTTPVersion(1, 0) =>
                {
                    self.no_more_requests = true
                }
                None if *rq.http_version() == HTTPVersion(1, 0) => self.no_more_requests = true,
                _ => (),
            };

            // returning the request
            return Some(rq);
        }
    }
}

/// Parses a "HTTP/1.1" string.
fn parse_http_version(version: &str) -> Result<HTTPVersion, ReadError> {
    let (major, minor) = match version {
        "HTTP/0.9" => (0, 9),
        "HTTP/1.0" => (1, 0),
        "HTTP/1.1" => (1, 1),
        "HTTP/2.0" => (2, 0),
        "HTTP/3.0" => (3, 0),
        _ => return Err(ReadError::WrongRequestLine),
    };

    Ok(HTTPVersion(major, minor))
}

/// Parses the request line of the request.
/// eg. GET / HTTP/1.1
fn parse_request_line(line: &str) -> Result<(Method, String, HTTPVersion), ReadError> {
    let mut parts = line.split(' ');

    let method = parts.next().and_then(|w| w.parse().ok());
    let path = parts.next().map(ToOwned::to_owned);
    let version = parts.next().and_then(|w| parse_http_version(w).ok());

    method
        .and_then(|method| Some((method, path?, version?)))
        .ok_or(ReadError::WrongRequestLine)
}

#[cfg(test)]
mod test {
    #[test]
    fn test_parse_request_line() {
        let (method, path, ver) = super::parse_request_line("GET /hello HTTP/1.1").unwrap();

        assert!(method == crate::Method::Get);
        assert!(path == "/hello");
        assert!(ver == crate::common::HTTPVersion(1, 1));

        assert!(super::parse_request_line("GET /hello").is_err());
        assert!(super::parse_request_line("qsd qsd qsd").is_err());
    }
}
