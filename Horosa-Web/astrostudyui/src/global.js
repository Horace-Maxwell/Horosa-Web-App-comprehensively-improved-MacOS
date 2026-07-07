// 兼容层必须最先执行(第三方产物可能裸调新 API):macOS 12.0-12.2 WebView 微填充 + :has 回退
import './utils/legacyWebkitCompat'

let _globalObj = {}
