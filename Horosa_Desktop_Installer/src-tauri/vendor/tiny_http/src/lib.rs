//! # Simple usage
//!
//! ## Creating the server
//!
//! The easiest way to create a server is to call `Server::http()`.
//!
//! The `http()` function returns an `IoResult<Server>` which will return an error
//! in the case where the server creation fails (for example if the listening port is already
//! occupied).
//!
//! ```no_run
//! let server = tiny_http::Server::http("0.0.0.0:0").unwrap();
//! ```
//!
//! A newly-created `Server` will immediately start listening for incoming connections and HTTP
//! requests.
//!
//! ## Receiving requests
//!
//! Calling `server.recv()` will block until the next request is available.
//! This function returns an `IoResult<Request>`, so you need to handle the possible errors.
//!
//! ```no_run
//! # let server = tiny_http::Server::http("0.0.0.0:0").unwrap();
//!
//! loop {
//!     // blocks until the next request is received
//!     let request = match server.recv() {
//!         Ok(rq) => rq,
//!         Err(e) => { println!("error: {}", e); break }
//!     };
//!
//!     // do something with the request
//!     // ...
//! }
//! ```
//!
//! In a real-case scenario, you will probably want to spawn multiple worker tasks and call
//! `server.recv()` on all of them. Like this:
//!
//! ```no_run
//! # use std::sync::Arc;
//! # use std::thread;
//! # let server = tiny_http::Server::http("0.0.0.0:0").unwrap();
//! let server = Arc::new(server);
//! let mut guards = Vec::with_capacity(4);
//!
//! for _ in (0 .. 4) {
//!     let server = server.clone();
//!
//!     let guard = thread::spawn(move || {
//!         loop {
//!             let rq = server.recv().unwrap();
//!
//!             // ...
//!         }
//!     });
//!
//!     guards.push(guard);
//! }
//! ```
//!
//! If you don't want to block, you can call `server.try_recv()` instead.
//!
//! ## Handling requests
//!
//! The `Request` object returned by `server.recv()` contains informations about the client's request.
//! The most useful methods are probably `request.method()` and `request.url()` which return
//! the requested method (`GET`, `POST`, etc.) and url.
//!
//! To handle a request, you need to create a `Response` object. See the docs of this object for
//! more infos. Here is an example of creating a `Response` from a file:
//!
//! ```no_run
//! # use std::fs::File;
//! # use std::path::Path;
//! let response = tiny_http::Response::from_file(File::open(&Path::new("image.png")).unwrap());
//! ```
//!
//! All that remains to do is call `request.respond()`:
//!
//! ```no_run
//! # use std::fs::File;
//! # use std::path::Path;
//! # let server = tiny_http::Server::http("0.0.0.0:0").unwrap();
//! # let request = server.recv().unwrap();
//! # let response = tiny_http::Response::from_file(File::open(&Path::new("image.png")).unwrap());
//! let _ = request.respond(response);
//! ```
#![forbid(unsafe_code)]
#![deny(rust_2018_idioms)]
#![allow(clippy::match_like_matches_macro)]

#[cfg(any(feature = "ssl-openssl", feature = "ssl-rustls"))]
use zeroize::Zeroizing;

use std::error::Error;
use std::io::Error as IoError;
use std::io::ErrorKind as IoErrorKind;
use std::io::Result as IoResult;
use std::net::{Shutdown, TcpStream, ToSocketAddrs};
use std::sync::atomic::Ordering::{Relaxed, SeqCst};
use std::sync::atomic::{AtomicBool, AtomicUsize};
use std::collections::HashMap;
use std::sync::mpsc;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use client::ClientConnection;
use connection::Connection;
use util::MessagesQueue;

pub use common::{HTTPVersion, Header, HeaderField, Method, StatusCode};
pub use connection::{ConfigListenAddr, ListenAddr, Listener};
pub use request::{ReadWrite, Request};
pub use response::{Response, ResponseBox};
pub use test::TestRequest;

/// 已接受连接的读 / 写超时。
const CONNECTION_IO_TIMEOUT: Duration = Duration::from_secs(30);
/// 同时在服的连接上限(每条连接占一个线程、两个文件描述符)。
const MAX_CONNECTIONS: usize = 64;
/// accept 出错 / 起不了线程时的退避区间(指数递增,成功一次即复位)。
const ACCEPT_BACKOFF_MIN: Duration = Duration::from_millis(10);
const ACCEPT_BACKOFF_MAX: Duration = Duration::from_secs(1);

/// 在服连接登记表:每条连接留一份套接字句柄,服务关闭时用它把读方向关掉。
/// 关闭后再登记的连接(与关闭擦肩而过)当场关读方向,不进表。
#[derive(Default)]
struct ConnectionRegistry {
    closed: bool,
    next_id: u64,
    handles: HashMap<u64, Connection>,
}

impl ConnectionRegistry {
    fn register(registry: &Mutex<ConnectionRegistry>, handle: Option<Connection>) -> Option<u64> {
        let handle = handle?;
        let mut guard = registry.lock().unwrap_or_else(|e| e.into_inner());
        if guard.closed {
            let _ = handle.shutdown(Shutdown::Read);
            return None;
        }
        let id = guard.next_id;
        guard.next_id += 1;
        guard.handles.insert(id, handle);
        Some(id)
    }

    /// 服务关闭:关掉所有在服连接的读方向。正在等下一条请求的空闲长连接,其连接线程随即读到结束、退出,
    /// 套接字关闭,客户端收到 FIN —— 不会再拿这条旧连接发请求,也就不会收到「服务已停」的 503
    /// (浏览器对 503 不重试;同一端口上已经起了新服务时,导航正好落在旧连接上就是白页)。
    /// 已经被 recv() 交出去、还没回应的请求不受影响:写方向照旧,回应照常送达。
    fn close_all(registry: &Mutex<ConnectionRegistry>) {
        let mut guard = registry.lock().unwrap_or_else(|e| e.into_inner());
        guard.closed = true;
        for handle in guard.handles.values() {
            let _ = handle.shutdown(Shutdown::Read);
        }
    }
}

/// 在服连接计数的占位:连接任务结束(或没起来)时随之释放,并从登记表里撤掉这条连接的句柄。
struct ConnectionSlot {
    active: Arc<AtomicUsize>,
    registry: Arc<Mutex<ConnectionRegistry>>,
    id: Option<u64>,
}

impl ConnectionSlot {
    fn take(
        active: &Arc<AtomicUsize>,
        registry: &Arc<Mutex<ConnectionRegistry>>,
        handle: Option<Connection>,
    ) -> ConnectionSlot {
        active.fetch_add(1, SeqCst);
        ConnectionSlot {
            active: Arc::clone(active),
            registry: Arc::clone(registry),
            id: ConnectionRegistry::register(registry, handle),
        }
    }
}

impl Drop for ConnectionSlot {
    fn drop(&mut self) {
        self.active.fetch_sub(1, SeqCst);
        if let Some(id) = self.id {
            let mut guard = self.registry.lock().unwrap_or_else(|e| e.into_inner());
            guard.handles.remove(&id);
        }
    }
}

/// 服务已停(队列已关):没交出去的请求直接回 503 并关连接,不让客户端对着一条没人收的队列干等。
fn reject_after_close(msg: Message) {
    if let Message::NewRequest(rq) = msg {
        rq.close_connection_after();
        let mut response = Response::empty(StatusCode(503));
        if let Ok(h) = Header::from_bytes(&b"Connection"[..], &b"close"[..]) {
            response = response.with_header(h);
        }
        let _ = rq.respond(response);
    }
}

mod client;
mod common;
mod connection;
mod request;
mod response;
mod ssl;
mod test;
mod util;

/// The main class of this library.
///
/// Destroying this object will immediately close the listening socket and the reading
///  part of all the client's connections. Requests that have already been returned by
///  the `recv()` function will not close and the responses will be transferred to the client.
pub struct Server {
    // should be false as long as the server exists
    // when set to true, all the subtasks will close within a few hundreds ms
    close: Arc<AtomicBool>,

    // queue for messages received by child threads
    messages: Arc<MessagesQueue<Message>>,

    // result of TcpListener::local_addr()
    listening_addr: ListenAddr,

    // 在服连接登记表(关闭时关读方向,见 ConnectionRegistry::close_all)
    connections: Arc<Mutex<ConnectionRegistry>>,
}

enum Message {
    Error(IoError),
    NewRequest(Request),
}

impl From<IoError> for Message {
    fn from(e: IoError) -> Message {
        Message::Error(e)
    }
}

impl From<Request> for Message {
    fn from(rq: Request) -> Message {
        Message::NewRequest(rq)
    }
}

// this trait is to make sure that Server implements Share and Send
#[doc(hidden)]
#[allow(dead_code)]
trait MustBeShareDummy: Sync + Send {}
#[doc(hidden)]
impl MustBeShareDummy for Server {}

pub struct IncomingRequests<'a> {
    server: &'a Server,
}

/// Represents the parameters required to create a server.
#[derive(Debug, Clone)]
pub struct ServerConfig {
    /// The addresses to try to listen to.
    pub addr: ConfigListenAddr,

    /// If `Some`, then the server will use SSL to encode the communications.
    pub ssl: Option<SslConfig>,
}

/// Configuration of the server for SSL.
#[derive(Debug, Clone)]
pub struct SslConfig {
    /// Contains the public certificate to send to clients.
    pub certificate: Vec<u8>,
    /// Contains the ultra-secret private key used to decode communications.
    pub private_key: Vec<u8>,
}

impl Server {
    /// Shortcut for a simple server on a specific address.
    #[inline]
    pub fn http<A>(addr: A) -> Result<Server, Box<dyn Error + Send + Sync + 'static>>
    where
        A: ToSocketAddrs,
    {
        Server::new(ServerConfig {
            addr: ConfigListenAddr::from_socket_addrs(addr)?,
            ssl: None,
        })
    }

    /// Shortcut for an HTTPS server on a specific address.
    #[cfg(any(feature = "ssl-openssl", feature = "ssl-rustls"))]
    #[inline]
    pub fn https<A>(
        addr: A,
        config: SslConfig,
    ) -> Result<Server, Box<dyn Error + Send + Sync + 'static>>
    where
        A: ToSocketAddrs,
    {
        Server::new(ServerConfig {
            addr: ConfigListenAddr::from_socket_addrs(addr)?,
            ssl: Some(config),
        })
    }

    #[cfg(unix)]
    #[inline]
    /// Shortcut for a UNIX socket server at a specific path
    pub fn http_unix(
        path: &std::path::Path,
    ) -> Result<Server, Box<dyn Error + Send + Sync + 'static>> {
        Server::new(ServerConfig {
            addr: ConfigListenAddr::unix_from_path(path),
            ssl: None,
        })
    }

    /// Builds a new server that listens on the specified address.
    pub fn new(config: ServerConfig) -> Result<Server, Box<dyn Error + Send + Sync + 'static>> {
        let listener = config.addr.bind()?;
        Self::from_listener(listener, config.ssl)
    }

    /// Builds a new server using the specified TCP listener.
    ///
    /// This is useful if you've constructed TcpListener using some less usual method
    /// such as from systemd. For other cases, you probably want the `new()` function.
    pub fn from_listener<L: Into<Listener>>(
        listener: L,
        ssl_config: Option<SslConfig>,
    ) -> Result<Server, Box<dyn Error + Send + Sync + 'static>> {
        let listener = listener.into();
        // building the "close" variable
        let close_trigger = Arc::new(AtomicBool::new(false));

        // building the TcpListener
        let (server, local_addr) = {
            let local_addr = listener.local_addr()?;
            log::debug!("Server listening on {}", local_addr);
            (listener, local_addr)
        };

        // building the SSL capabilities
        #[cfg(all(feature = "ssl-openssl", feature = "ssl-rustls"))]
        compile_error!(
            "Features 'ssl-openssl' and 'ssl-rustls' must not be enabled at the same time"
        );
        #[cfg(not(any(feature = "ssl-openssl", feature = "ssl-rustls")))]
        type SslContext = ();
        #[cfg(any(feature = "ssl-openssl", feature = "ssl-rustls"))]
        type SslContext = crate::ssl::SslContextImpl;
        let ssl: Option<SslContext> = {
            match ssl_config {
                #[cfg(any(feature = "ssl-openssl", feature = "ssl-rustls"))]
                Some(config) => Some(SslContext::from_pem(
                    config.certificate,
                    Zeroizing::new(config.private_key),
                )?),
                #[cfg(not(any(feature = "ssl-openssl", feature = "ssl-rustls")))]
                Some(_) => return Err(
                    "Building a server with SSL requires enabling the `ssl` feature in tiny-http"
                        .into(),
                ),
                None => None,
            }
        };

        // creating a task where server.accept() is continuously called
        // and ClientConnection objects are pushed in the messages queue
        let messages = MessagesQueue::with_capacity(8);

        let inside_close_trigger = close_trigger.clone();
        let inside_messages = messages.clone();
        let connections = Arc::new(Mutex::new(ConnectionRegistry::default()));
        let inside_connections = Arc::clone(&connections);
        let accept_thread = thread::Builder::new().spawn(move || {
            // a tasks pool is used to dispatch the connections into threads
            let tasks_pool = util::TaskPool::new();
            let active = Arc::new(AtomicUsize::new(0));
            let mut backoff = ACCEPT_BACKOFF_MIN;
            let mut error_reported = false;

            log::debug!("Running accept thread");
            while !inside_close_trigger.load(Relaxed) {
                // 在服连接到顶:先不接新连接(留在内核队列里),等有连接收尾再接
                if active.load(SeqCst) >= MAX_CONNECTIONS {
                    thread::sleep(ACCEPT_BACKOFF_MIN);
                    continue;
                }
                // 本条连接留给登记表的句柄(复制失败 = 文件描述符紧张:连接照常服务,只是关闭时不能提前关读方向)
                let mut registry_handle: Option<Connection> = None;
                let new_client = match server.accept() {
                    Ok((sock, _)) => {
                        // 读 / 写超时:慢客户端、只发头不发体、半开连接都不再无限期占住线程
                        let _ = sock.set_io_timeouts(Some(CONNECTION_IO_TIMEOUT));
                        registry_handle = sock.try_clone().ok();
                        use util::RefinedTcpStream;
                        let halves = match ssl {
                            None => RefinedTcpStream::new(sock),
                            #[cfg(any(feature = "ssl-openssl", feature = "ssl-rustls"))]
                            Some(ref ssl) => {
                                // trying to apply SSL over the connection
                                // if an error occurs, we just close the socket and resume listening
                                let sock = match ssl.accept(sock) {
                                    Ok(s) => s,
                                    Err(_) => continue,
                                };

                                RefinedTcpStream::new(sock)
                            }
                            #[cfg(not(any(feature = "ssl-openssl", feature = "ssl-rustls")))]
                            Some(ref _ssl) => unreachable!(),
                        };

                        halves.map(|(read_closable, write_closable)| {
                            ClientConnection::new(write_closable, read_closable)
                        })
                    }
                    Err(e) => Err(e),
                };

                match new_client {
                    Ok(client) => {
                        backoff = ACCEPT_BACKOFF_MIN;
                        error_reported = false;
                        let slot =
                            ConnectionSlot::take(&active, &inside_connections, registry_handle.take());
                        let messages = inside_messages.clone();
                        let mut client = Some(client);
                        let started = tasks_pool.spawn(Box::new(move || {
                            let _slot = &slot;
                            if let Some(client) = client.take() {
                                // Synchronization is needed for HTTPS requests to avoid a deadlock
                                if client.secure() {
                                    let (sender, receiver) = mpsc::channel();
                                    for rq in client {
                                        let rq = rq.with_notify_sender(sender.clone());
                                        if let Err(msg) = messages.push_if_open(rq.into()) {
                                            reject_after_close(msg);
                                            break;
                                        }
                                        if receiver.recv().is_err() {
                                            break;
                                        }
                                    }
                                } else {
                                    for rq in client {
                                        if let Err(msg) = messages.push_if_open(rq.into()) {
                                            reject_after_close(msg);
                                            break;
                                        }
                                    }
                                }
                            }
                        }));
                        if !started {
                            // 系统起不了新线程:这条连接已随任务丢弃(关闭),退避后继续接
                            log::error!("Cannot spawn a thread for a new client");
                            thread::sleep(backoff);
                            backoff = (backoff * 2).min(ACCEPT_BACKOFF_MAX);
                        }
                    }

                    Err(e) => {
                        if inside_close_trigger.load(Relaxed) {
                            break;
                        }
                        // 文件描述符耗尽(EMFILE / ENFILE)、内存不足、对端在 accept 前就断开等都是暂时性的:
                        // 退避后继续接,接受线程绝不因此退出(否则服务从此不再响应却无人察觉)。
                        // 一串连续错误只报一次给 recv() 的调用方。
                        log::error!("Error accepting new client: {}", e);
                        if !error_reported {
                            inside_messages.push(e.into());
                            error_reported = true;
                        }
                        thread::sleep(backoff);
                        backoff = (backoff * 2).min(ACCEPT_BACKOFF_MAX);
                    }
                }
            }
            log::debug!("Terminating accept thread");
        });
        if let Err(e) = accept_thread {
            return Err(Box::new(e));
        }

        // result
        Ok(Server {
            messages,
            close: close_trigger,
            listening_addr: local_addr,
            connections,
        })
    }

    /// Returns an iterator for all the incoming requests.
    ///
    /// The iterator will return `None` if the server socket is shutdown.
    #[inline]
    pub fn incoming_requests(&self) -> IncomingRequests<'_> {
        IncomingRequests { server: self }
    }

    /// Returns the address the server is listening to.
    #[inline]
    pub fn server_addr(&self) -> ListenAddr {
        self.listening_addr.clone()
    }

    /// Returns the number of clients currently connected to the server.
    pub fn num_connections(&self) -> usize {
        unimplemented!()
        //self.requests_receiver.lock().len()
    }

    /// Blocks until an HTTP request has been submitted and returns it.
    pub fn recv(&self) -> IoResult<Request> {
        match self.messages.pop() {
            Some(Message::Error(err)) => Err(err),
            Some(Message::NewRequest(rq)) => Ok(rq),
            None => Err(IoError::new(IoErrorKind::Other, "thread unblocked")),
        }
    }

    /// Same as `recv()` but doesn't block longer than timeout
    pub fn recv_timeout(&self, timeout: Duration) -> IoResult<Option<Request>> {
        match self.messages.pop_timeout(timeout) {
            Some(Message::Error(err)) => Err(err),
            Some(Message::NewRequest(rq)) => Ok(Some(rq)),
            None => Ok(None),
        }
    }

    /// Same as `recv()` but doesn't block.
    pub fn try_recv(&self) -> IoResult<Option<Request>> {
        match self.messages.try_pop() {
            Some(Message::Error(err)) => Err(err),
            Some(Message::NewRequest(rq)) => Ok(Some(rq)),
            None => Ok(None),
        }
    }

    /// Unblock thread stuck in recv() or incoming_requests().
    /// If there are several such threads, only one is unblocked.
    /// This method allows graceful shutdown of server.
    pub fn unblock(&self) {
        self.messages.unblock();
    }
}

impl Iterator for IncomingRequests<'_> {
    type Item = Request;
    fn next(&mut self) -> Option<Request> {
        self.server.recv().ok()
    }
}

impl Drop for Server {
    fn drop(&mut self) {
        self.close.store(true, Relaxed);
        // 关队列:还在队列里没被取走的请求、以及此后各连接才读到的请求,一律回 503 并关连接
        // (回包可能要等写超时,放到独立线程,不拖住 drop)
        let pending = self.messages.close();
        // 关掉所有在服连接的读方向:空闲长连接随即关闭,客户端不会再拿它发请求、吃到 503
        ConnectionRegistry::close_all(&self.connections);
        if !pending.is_empty() {
            let _ = thread::Builder::new().spawn(move || {
                for msg in pending {
                    reject_after_close(msg);
                }
            });
        }
        // Connect briefly to ourselves to unblock the accept thread
        let maybe_stream = match &self.listening_addr {
            ListenAddr::IP(addr) => TcpStream::connect(addr).map(Connection::from),
            #[cfg(unix)]
            ListenAddr::Unix(addr) => {
                // TODO: use connect_addr when its stabilized.
                let path = addr.as_pathname().unwrap();
                std::os::unix::net::UnixStream::connect(path).map(Connection::from)
            }
        };
        if let Ok(stream) = maybe_stream {
            let _ = stream.shutdown(Shutdown::Both);
        }

        #[cfg(unix)]
        if let ListenAddr::Unix(addr) = &self.listening_addr {
            if let Some(path) = addr.as_pathname() {
                let _ = std::fs::remove_file(path);
            }
        }
    }
}
