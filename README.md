# 🧸 UNION 玩具集運分析工具 (Toy Shipping Optimizer)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

這是一個專為玩具電商設計的自動化決策工具，旨在解決跨國物流中「運費計算繁瑣」與「重量利用率低」的痛點。透過 Python 強大的數據處理能力，實現帳本解析、運費優化與獲利監控的一站式管理。

## 🌟 核心功能 (Key Features)

* **📊 自動化數據解析**：直接對接 Apple Numbers 原始帳本，免去手動輸入煩惱。
* **⚖️ 運費最佳化演算法**：利用組合搜尋（Combination Search）在符合物流門檻（10kg - 13kg）的情況下，找出最省錢的打包組合。
* **📈 財務統計看板**：快速查詢特定年月份的總獲利與商品獲利明細。
* **🖥️ 互動式 Web 介面**：基於 Gradio 打造，操作直覺，無需代碼背景也能上手。

---

## 📸 畫面預覽 (Screenshots)

<p align="center">
  <img src="screenshots/ui_main.png" width="800" alt="UI 介面截圖"><br>
  <em>Gradio 打造的互動式控制面板</em>
</p>


## 🛠️ 安裝與啟動 (Installation)

### 1. 環境要求
* Python 3.8 或以上版本。
* 建議使用虛擬環境 (Conda 或 venv) 進行管理。

### 2. 安裝套件
在終端機執行以下指令：
```powershell
pip install -r requirements.txt