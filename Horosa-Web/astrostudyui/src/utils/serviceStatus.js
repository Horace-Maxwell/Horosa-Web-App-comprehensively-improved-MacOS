// 修法6:全局「本地服务在线/离线」状态 + 订阅。
// 由 request.js(签名 Java 面)与 chartFetch.js(裸 fetch 排盘面)在收到任何响应时置在线、
// 在确认「后端不可达」时置离线;由顶栏重连横幅(ServiceStatusBanner)订阅显示。
//
// 严格只反映「网络层不可达」,绝不掺杂业务错误——这是红队 H2 的关键约束:
//   · 超时(TimeoutError / request.timeout):请求其实已到、后端在世只是慢 → 不算离线;
//   · signature.error 等业务错误(带 HTTP 响应头 / ResultCode):#10 是「可达但错乱」→ 绝不算离线;
//   · 仅 fetch 在网络层 reject 抛出的 TypeError(连接被拒/断网/DNS)才算离线。

let online = true;
const listeners = new Set();

function emit() {
  listeners.forEach((fn) => {
    try {
      fn(online);
    } catch (e) {
      // 单个订阅者抛错不应影响其它订阅者
    }
  });
}

export function isServiceOnline() {
  return online;
}

// 订阅状态变化;注册即回调一次当前值;返回取消订阅函数。
export function subscribeServiceStatus(fn) {
  if (typeof fn !== 'function') {
    return () => {};
  }
  listeners.add(fn);
  try {
    fn(online);
  } catch (e) {
    // ignore
  }
  return () => {
    listeners.delete(fn);
  };
}

export function markServiceOnline() {
  if (!online) {
    online = true;
    emit();
  }
}

export function markServiceOffline() {
  if (online) {
    online = false;
    emit();
  }
}

// 严格的「后端不可达」判定(见文件头注释)。
export function isBackendUnreachableError(err) {
  if (!err) {
    return false;
  }
  // 带响应头 = 后端可达(业务 / HTTP 错误,含 signature.error、need.login 等)。
  if (err.headers) {
    return false;
  }
  // 超时 / 主动中断:后端在世只是慢或被取消,不算离线。
  if (err.name === 'TimeoutError' || err.name === 'AbortError') {
    return false;
  }
  const msg = `${err.message || ''}`.toLowerCase();
  if (msg.indexOf('request.timeout') >= 0) {
    return false;
  }
  // fetch 网络层失败统一抛 TypeError(connection refused / network error / failed to fetch)。
  return err instanceof TypeError;
}
