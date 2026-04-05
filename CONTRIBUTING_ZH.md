# 为 Horosa 贡献

English guide: [CONTRIBUTING.md](CONTRIBUTING.md)

感谢你帮助改进 Horosa。这个仓库正在按“正式开源发布”的标准整理，但它本身已经是一个真实产品仓库：共用的 web/app 前端、本地 Java/Python 服务、桌面壳、AIAnalysis、本地优先存储、发布自动化和回归脚本都在这里共同工作。

好的贡献，应该让这套系统更容易理解、更容易验证，也更安全地交付。

## 可以怎么参与

- 提交可复现的 bug
- 改进文档、架构说明或发布说明
- 补测试或稳定已有流程
- 改进 AIAnalysis、provider 兼容或恢复能力
- 在不削弱用户安全性的前提下改进构建、打包或诊断链路

## 工作原则

- 除非产品明确需要远端依赖，否则优先坚持本地优先 / 文件优先。
- 优先做可 review、可解释、可回退的增量修改，不做大而模糊的重写。
- Web 和 App 的行为应尽量保持一致；如果必须分叉，必须说明原因并写进文档。
- 如果改动影响 AI 提示词、Schema、provider 协议、导出、备份、存储或迁移，必须在 PR 中明确写出契约变化。
- 不夸大版本状态、性能、兼容性或安全保证。

## 建议先读

- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [README_EN.md](README_EN.md)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)

## 本地环境

### 前端

```bash
cd Horosa-Web/astrostudyui
npm ci
npm test -- --runInBand
npm run build
npm run build:file
```

### 后端

```bash
cd Horosa-Web/astrostudysrv/boundless
mvn test -DskipTests=false

cd ../astrostudy
mvn test -DskipTests=false
```

如果你在全新环境里缺少内部 Maven 依赖，可以先按依赖链安装：

```bash
cd Horosa-Web/astrostudysrv/boundless && mvn -DskipTests install
cd ../basecomm && mvn -DskipTests install
cd ../image && mvn -DskipTests install
cd ../astrostudy && mvn test -DskipTests=false
```

### 整体运行态

```bash
cd Horosa-Web
./start_horosa_local.sh
./verify_horosa_local.sh
./stop_horosa_local.sh
```

### 桌面端

```bash
cd Horosa_Desktop_Installer
cargo check --manifest-path src-tauri/Cargo.toml
cargo test --manifest-path src-tauri/Cargo.toml
./scripts/verify_desktop_packaging.sh
```

## 开始做较大改动前

请先读对应产品面：

- 如果是 AIAnalysis UI 或行为：
  - `Horosa-Web/astrostudyui/src/components/aianalysis/`
  - `Horosa-Web/astrostudyui/src/utils/aiAnalysis*.js`
- 如果是 AI provider 或资料抽取：
  - `Horosa-Web/astrostudyui/src/services/aianalysis.js`
  - `Horosa-Web/astrostudyui/src/utils/aiAnalysis*.js`
  - `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysis*.java`
- 如果是 runtime / 打包：
  - `Horosa_Desktop_Installer/`
  - `Horosa_Desktop_Installer/README.md`

## 改动预期

### 对代码改动

- 要写清楚用户侧影响，而不只是“改了哪些文件”
- 新逻辑尽量带测试
- 错误提示尽量可操作
- 如果涉及存储、导出格式、provider id 等，尽量保持兼容

### 对 UI 改动

- 能带截图就带截图
- 检查滚动、空状态、modal overflow
- 确认 web 和 app 关键流程没有跑偏

### 对 AIAnalysis 改动

请明确说明是否影响这些部分：

- 布局与滚动
- provider 预设或协议族映射
- 流式事件处理
- IndexedDB store 或 schema 版本
- prompt 分层与裁剪
- RAG 阈值、切块或 embedding 行为
- 导出 / 备份格式
- 桌面端导入 / 导出桥接

## PR 检查清单

- [ ] 本地跑过相关测试
- [ ] `git diff --check` 通过
- [ ] 已清理 secrets、本地路径和临时文件
- [ ] 如果流程、契约或开发入口有变化，已同步更新文档
- [ ] 重要 UI 变化已附截图
- [ ] 涉及 AIAnalysis 契约变化时，已明确写出

## 敏感区域

这些位置改动时需要格外谨慎：

- `Horosa-Web/astrostudyui/src/components/aianalysis/`
- `Horosa-Web/astrostudyui/src/utils/aiAnalysis*`
- `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysis*`
- `Horosa-Web/astrostudysrv/boundless/`
- `Horosa_Desktop_Installer/src-tauri/`

这些区域至少应补其中一类验证：

- 自动化测试
- 浏览器流程验证
- 桌面端验证
- 迁移说明

## 安全与隐私

- 不提交 API Key、内部 token 或机器专属凭据。
- 不提交本地 runtime、生成安装包、私人截图或诊断日志。
- 不要把私人盘例、可识别用户数据放进测试、fixture、截图或 bug 报告里。
- 涉及敏感安全问题时，请走 [SECURITY_ZH.md](SECURITY_ZH.md)，不要直接发公开 Issue。

## 许可证说明

Horosa 已明确采用 [MIT](LICENSE) 作为源码许可证。若未来品牌资产、截图、bundled runtime 或其他非代码资产需要单独政策，请把规则明确写成文档，而不是靠模糊表述去改变源码许可证的含义。
