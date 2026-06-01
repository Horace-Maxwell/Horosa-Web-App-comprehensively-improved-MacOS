import React from 'react';
import { subscribeServiceStatus } from '../../utils/serviceStatus';

// 修法6:非阻塞的「本地服务连接中断」重连横幅。
//
// 纯增量 UI——在线时渲染 null(零 DOM、对正常路径零影响);仅在确认「后端不可达」时,
// 于顶部居中显示一条**不拦截任何点击/交互**(pointerEvents:none)的细横幅。
// 离线 / 在线状态由 utils/serviceStatus 驱动:request.js / chartFetch.js 在确认后端不可达时置离线、
// 在收到任何后端响应时置在线。不做主动心跳定时器(见方案 v4 修法6):下一次成功的后端请求
// (用户重试或排盘的自动重试)即会把状态置回在线,本横幅随之自动消失。
//
// 配色取中性告警色(琥珀),非术数语义色,明暗主题下均可读。
export default function ServiceStatusBanner() {
  const [online, setOnline] = React.useState(true);

  React.useEffect(() => {
    const unsub = subscribeServiceStatus((v) => setOnline(v));
    return unsub;
  }, []);

  if (online) {
    return null;
  }

  const wrapStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 2000,
    display: 'flex',
    justifyContent: 'center',
    pointerEvents: 'none',
  };
  const barStyle = {
    marginTop: 8,
    maxWidth: '92%',
    padding: '6px 16px',
    borderRadius: 8,
    fontSize: 13,
    lineHeight: 1.4,
    color: '#7a4f01',
    background: 'rgba(255, 244, 222, 0.97)',
    border: '1px solid rgba(214, 158, 46, 0.55)',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.12)',
    pointerEvents: 'none',
  };

  return (
    <div style={wrapStyle} aria-live="polite">
      <div style={barStyle}>本地服务连接中断，操作将自动重试…若持续，请重启 星阙。</div>
    </div>
  );
}
