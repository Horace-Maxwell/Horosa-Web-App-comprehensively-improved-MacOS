// 壳自带页面(启动器 / 设置 / 诊断)的报错文字。
// 壳层命令失败时回来的多是系统原文(英文、带 os error 码,如「No space left on device (os error 28)」),
// 这里换成一句看得懂的中文;原文另由诊断页列在「原始信息」里,排查用。
(function (root) {
  'use strict';

  function rawText(error) {
    if (error === null || error === undefined) return '';
    if (typeof error === 'string') return error.trim();
    if (typeof error === 'object' && typeof error.message === 'string') return error.message.trim();
    return String(error).trim();
  }

  function hasChinese(text) {
    return /[一-鿿]/.test(text);
  }

  // 常见系统原因 → 中文
  const KINDS = [
    [/no space left|disk full|os error 28\b/i, '磁盘空间不足'],
    [/read-only file system|os error 30\b/i, '磁盘或文件夹是只读的，写不进去'],
    [/permission denied|operation not permitted|not permitted|access denied|os error 1\b|os error 13\b/i,
      '没有访问权限（文件夹可能只读，或需要在「系统设置 › 隐私与安全性」里允许星阙访问）'],
    [/no such file|not found|os error 2\b/i, '找不到需要的文件或文件夹'],
    [/timed out|timeout/i, '等待超时'],
    [/connection refused|os error 61\b/i, '本机服务没有响应'],
    [/broken pipe|connection reset|os error 32\b|os error 54\b/i, '与本机服务的连接断开了'],
    [/too many open files|os error 24\b/i, '系统打开的文件太多，请稍后重试']
  ];

  // 一句看得懂的中文。已经是中文说明的原样返回;中文前缀 + 系统原文(「备份读取失败: No such file…」)换成「前缀：中文原因」。
  function plain(error) {
    const raw = rawText(error);
    if (!raw) return '操作没有完成。';
    let kind = '';
    for (let i = 0; i < KINDS.length; i += 1) {
      if (KINDS[i][0].test(raw)) {
        kind = KINDS[i][1];
        break;
      }
    }
    const cut = raw.search(/[:：]/);
    const head = cut > 0 ? raw.slice(0, cut).trim() : '';
    const prefix = head && hasChinese(head) ? head : '';
    if (kind) return prefix ? `${prefix}：${kind}` : kind;
    if (hasChinese(raw)) return raw;
    return '操作没有完成（详细信息可在诊断页查看，或导出诊断包）。';
  }

  // 诊断页:中文一句 + 原始信息(两者相同就只给一句)
  function withDetail(error) {
    const raw = rawText(error);
    const text = plain(error);
    return raw && raw !== text ? `${text}\n\n原始信息：${raw}` : text;
  }

  const api = { plain, withDetail, raw: rawText };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.HorosaShellErrors = api;
})(typeof window !== 'undefined' ? window : null);
