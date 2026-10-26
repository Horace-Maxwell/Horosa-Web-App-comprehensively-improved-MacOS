use std::collections::VecDeque;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::{Duration, Instant};

enum Control<T> {
    Elem(T),
    Unblock,
}

pub struct MessagesQueue<T>
where
    T: Send,
{
    queue: Mutex<VecDeque<Control<T>>>,
    condvar: Condvar,
    // 只在持 queue 锁时读写:close 与 push_if_open 互斥,关闭之后不会再有元素漏进队列
    closed: AtomicBool,
}

impl<T> MessagesQueue<T>
where
    T: Send,
{
    pub fn with_capacity(capacity: usize) -> Arc<MessagesQueue<T>> {
        Arc::new(MessagesQueue {
            queue: Mutex::new(VecDeque::with_capacity(capacity)),
            condvar: Condvar::new(),
            closed: AtomicBool::new(false),
        })
    }

    /// 推入一个元素;队列已关闭(服务已停)则原样交还给调用方处理。
    pub fn push_if_open(&self, value: T) -> Result<(), T> {
        let mut queue = self.queue.lock().unwrap();
        if self.closed.load(Ordering::Relaxed) {
            return Err(value);
        }
        queue.push_back(Control::Elem(value));
        self.condvar.notify_one();
        Ok(())
    }

    /// 关闭队列并取出还没被取走的元素;此后 `push_if_open` 一律交还。
    pub fn close(&self) -> Vec<T> {
        let mut queue = self.queue.lock().unwrap();
        self.closed.store(true, Ordering::Relaxed);
        let mut pending = Vec::new();
        for item in queue.drain(..) {
            if let Control::Elem(value) = item {
                pending.push(value);
            }
        }
        pending
    }

    /// Pushes an element to the queue.
    pub fn push(&self, value: T) {
        let mut queue = self.queue.lock().unwrap();
        queue.push_back(Control::Elem(value));
        self.condvar.notify_one();
    }

    /// Unblock one thread stuck in pop loop.
    pub fn unblock(&self) {
        let mut queue = self.queue.lock().unwrap();
        queue.push_back(Control::Unblock);
        self.condvar.notify_one();
    }

    /// Pops an element. Blocks until one is available.
    /// Returns None in case unblock() was issued.
    pub fn pop(&self) -> Option<T> {
        let mut queue = self.queue.lock().unwrap();

        loop {
            match queue.pop_front() {
                Some(Control::Elem(value)) => return Some(value),
                Some(Control::Unblock) => return None,
                None => (),
            }

            queue = self.condvar.wait(queue).unwrap();
        }
    }

    /// Tries to pop an element without blocking.
    pub fn try_pop(&self) -> Option<T> {
        let mut queue = self.queue.lock().unwrap();
        match queue.pop_front() {
            Some(Control::Elem(value)) => Some(value),
            Some(Control::Unblock) | None => None,
        }
    }

    /// Tries to pop an element without blocking
    /// more than the specified timeout duration
    /// or unblock() was issued
    pub fn pop_timeout(&self, timeout: Duration) -> Option<T> {
        let mut queue = self.queue.lock().unwrap();
        let mut duration = timeout;
        loop {
            match queue.pop_front() {
                Some(Control::Elem(value)) => return Some(value),
                Some(Control::Unblock) => return None,
                None => (),
            }
            let now = Instant::now();
            let (_queue, result) = self.condvar.wait_timeout(queue, timeout).unwrap();
            queue = _queue;
            let sleep_time = now.elapsed();
            duration = if duration > sleep_time {
                duration - sleep_time
            } else {
                Duration::from_millis(0)
            };
            if result.timed_out()
                || (duration.as_secs() == 0 && duration.subsec_nanos() < 1_000_000)
            {
                return None;
            }
        }
    }
}
