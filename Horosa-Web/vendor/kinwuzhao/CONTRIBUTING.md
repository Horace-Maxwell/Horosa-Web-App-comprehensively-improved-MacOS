# 🤝 貢獻指南 Contributing Guide

感謝您對「堅五兆」專案的興趣！我們歡迎各種形式的貢獻。

## 📋 貢獻流程

1. **Fork** 本倉庫
2. 創建功能分支：`git checkout -b feature/your-feature`
3. 安裝開發依賴：`pip install -e ".[dev]"`
4. 進行修改並確保測試通過：`pytest`
5. 提交更改：`git commit -m "Add your feature"`
6. 推送分支：`git push origin feature/your-feature`
7. 提交 **Pull Request**

## 🧪 開發環境

```bash
# 克隆倉庫
git clone https://github.com/kentang2017/kinwuzhao.git
cd kinwuzhao

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安裝開發依賴
pip install -e ".[dev,app]"

# 執行測試
pytest
```

## 📝 程式碼風格

- 使用 `from __future__ import annotations` 進行類型標註
- 遵循 Google-style docstrings
- 文獻引用請標明出處（如 P.2859 第 X 行）

## 🔍 我們歡迎的貢獻類型

| 類型 | 說明 |
|:---|:---|
| 🐛 Bug 修復 | 修復程式錯誤 |
| ✨ 新功能 | 增加占卜功能或分析工具 |
| 📚 文獻校勘 | 校對敦煌寫本引用或歷史文獻 |
| 🌐 翻譯 | 介面或文檔翻譯 |
| 📖 文檔改進 | 改善 README、docstring 或註釋 |
| 🧪 測試 | 增加測試覆蓋率 |

## 📬 聯繫

如有任何問題，歡迎在 [GitHub Issues](https://github.com/kentang2017/kinwuzhao/issues) 中提問。
