# AMD Insider Monitor 说明文档

这个目录提供一个可在 GitHub Pages 展示的 **AMD 高管 Form 4 交易监控面板**，并通过 GitHub Actions 每日自动更新数据。

---

## 文件结构

- `amd_insider_monitor.py`：抓取并解析 SEC Form 4 数据的脚本
- `amd_insider_trades.json`：脚本生成的数据文件（供前端读取）
- `index.html`：可视化 dashboard 页面
- `../.github/workflows/update-amd-insider.yml`：每日自动更新任务

---

## 脚本工作流程（amd_insider_monitor.py）

脚本主逻辑分 4 步：

## 1) 拉取 AMD 提交记录（SEC submissions）

- 固定使用 AMD CIK：`0000002488`
- 请求：`https://data.sec.gov/submissions/CIK0000002488.json`
- 读取 `filings.recent`，筛选表单类型：
  - `4`
  - `4/A`

只保留设定回看天数（`--days`）内的申报。

---

## 2) 定位每个 Form 4 的 XML 文件

对每份 filing：

- 先尝试 `primaryDocument`
- 若不是可解析 XML，则读取 filing 目录 `index.json`
- 自动寻找 `.xml` 文件并尝试解析

这样可以兼容 SEC 文件结构差异（有些 filing 主文档是 txt，有些是 xml）。

---

## 3) 解析交易记录（non-derivative transactions）

从 `ownershipDocument` 提取：

- 报告人信息：姓名、职位、身份（Officer/Director 等）
- 交易信息：
  - `transaction_date`
  - `code`（如 P/S/M/F）
  - `shares`
  - `price`
  - `acquired_disposed`
  - `shares_owned_after`
- 附注 footnotes

并基于 footnote 文本判断是否疑似 `10b5-1` 计划交易（`is_10b5_1`）。

---

## 4) 生成统一 JSON 输出

输出文件默认 `amd_insider_trades.json`，包含：

- `summary`：总条数、代码分布、最近交易日、人员统计
- `transactions`：逐条交易明细（供 dashboard 直接渲染）

前端页面 `index.html` 通过 `fetch('./amd_insider_trades.json')` 读取该文件。

---

## 常用命令

在仓库根目录执行：

```bash
# 本地更新数据
python amd-insider/amd_insider_monitor.py --days 180 --output amd-insider/amd_insider_trades.json

# 本地预览页面
python -m http.server 8000
# 打开 http://localhost:8000/amd-insider/
```

---

## 自动更新（GitHub Actions）

工作流文件：`.github/workflows/update-amd-insider.yml`

触发方式：

- 每天定时执行（01:00 UTC / 09:00 Asia/Shanghai）
- 手动触发（Run workflow）

执行内容：

1. checkout 仓库
2. setup python
3. 运行脚本更新 `amd_insider_trades.json`
4. 若文件有变化则自动 commit + push

---

## SEC 访问注意事项

SEC 可能对请求频率和请求头较敏感，建议在仓库里设置 Secret：

- `SEC_USER_AGENT`

示例值：

```text
menes127 menes20240711@gmail.com
```

脚本已内置重试和退避机制（403/429/5xx）。

---

## 交易代码速查

- `P`：公开市场买入
- `S`：公开市场卖出
- `M`：期权行权
- `F`：为税务预扣而交付/扣股（常见于 RSU 归属）

> 注意：`S` 不一定是看空，需结合 footnote（是否 10b5-1 / 税务处理）判断。
