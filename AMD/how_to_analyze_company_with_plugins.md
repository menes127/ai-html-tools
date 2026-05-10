# 如何使用 Financial Analysis / Equity Research 插件分析一家公司：以 AMD 为例

本文档说明如何使用 Claude Code 中的金融分析与股票研究插件，对一家美股公司进行系统分析。示例公司为 **Advanced Micro Devices, Inc. (AMD)**。

> 适用场景：美股研究、DCF 估值、可比公司分析、财报前瞻、财报后复盘、投资 thesis、行业比较。

---

## 1. 推荐分析流程

分析 AMD 这类上市公司，建议按以下顺序进行：

```text
公司基础信息
→ 行业与竞争格局
→ 可比公司分析
→ DCF 估值
→ 投资 thesis
→ 财报前瞻 / 财报后分析
→ 催化剂与风险清单
```

对应插件如下：

| 分析环节 | 推荐插件 / Skill | 用途 |
|---|---|---|
| 可比公司分析 | `financial-analysis:comps-analysis` | 比较 AMD 与 NVDA、AVGO、QCOM、INTC、MRVL、TXN 等公司的估值倍数 |
| DCF 估值 | `financial-analysis:dcf-model` | 建立 AMD DCF，分析收入增长、毛利率、WACC、终值增长率 |
| 三表模型 | `financial-analysis:3-statement-model` | 建收入、利润表、资产负债表、现金流联动模型 |
| 投资 thesis | `equity-research:thesis` | 形成买入/持有/卖出逻辑，梳理 bull/base/bear case |
| 财报前瞻 | `equity-research:earnings-preview` | 财报前分析市场预期、关键指标和情景 |
| 财报后分析 | `equity-research:earnings-analysis` 或 `equity-research:earnings` | 财报发布后分析业绩、guidance、管理层表述和股价反应 |
| 行业分析 | `equity-research:sector` | 分析半导体行业趋势和 AMD 的竞争位置 |
| 催化剂日历 | `equity-research:catalysts` | 跟踪 AMD 财报、产品发布、AI GPU 订单、行业会议等催化剂 |
| 期权波动率 | `lseg:option-vol-analysis` | 分析 AMD 期权隐含波动率、earnings move、skew；通常需要 LSEG 账号 |

---

## 2. 第一步：做可比公司分析

### 使用命令

```text
/financial-analysis:comps-analysis AMD
```

### 适合回答的问题

- AMD 相对于 NVIDIA、Broadcom、Qualcomm、Intel、Marvell 是否便宜？
- AMD 的 EV/Sales 和 EV/EBITDA 在 peer group 中处于什么位置？
- AMD 当前估值是否已经反映 AI GPU 增长？
- DCF 的 terminal EV/EBITDA 应该用什么区间做交叉检查？

### 推荐 peer group

| 公司 | Ticker | 用途 |
|---|---:|---|
| NVIDIA | NVDA | AI GPU 高端估值参考 |
| Broadcom | AVGO | 高利润率半导体和 FCF 质量参考 |
| Intel | INTC | CPU 竞争对手，但 IDM 模式不同 |
| Qualcomm | QCOM | 成熟 fabless 半导体参考 |
| Marvell | MRVL | AI/networking 成长型半导体参考 |
| Texas Instruments | TXN | 成熟周期性半导体和现金流参考 |

### 核心输出

```text
Peer median EV/Sales
Peer median EV/EBITDA
AMD vs peer median
AMD vs 25th / 75th percentile
估值 premium / discount 解释
```

### 数据源说明

优先级：

```text
机构数据 MCP，例如 FactSet / S&P Global / Daloopa
→ 公司 filings / SEC EDGAR
→ 公开市场数据网站
```

如果没有 FactSet 或其他机构账号，可以使用公开数据版，但需要在结果中明确说明数据限制。

---

## 3. 第二步：做 DCF 模型框架

### 使用命令

```text
/financial-analysis:dcf-model AMD
```

或者更具体地写：

```text
/financial-analysis:dcf-model 为 AMD 建一个 7-10 年 DCF 框架，包含收入分部、毛利率、R&D、SG&A、税率、WACC、终值增长率和敏感性分析
```

### AMD DCF 应重点关注的变量

| 变量 | 为什么重要 |
|---|---|
| Data Center revenue growth | AI GPU 和 EPYC CPU 是 AMD 估值的核心增长驱动 |
| Gross margin | AI GPU、Data Center mix 和先进封装成本决定长期利润率 |
| R&D / Revenue | AMD 需要持续投入 AI GPU、CPU、software ecosystem |
| SG&A / Revenue | 反映 operating leverage |
| Terminal EBIT Margin | 决定当前高估值是否合理 |
| WACC | 成长股估值对折现率高度敏感 |
| Terminal Growth | 不应过高，通常应接近长期 GDP / 半导体成熟增长 |

### 推荐 DCF 结构

```text
Revenue by Segment
  Data Center
  Client
  Gaming
  Embedded

Gross Profit
Operating Expenses
  R&D
  SG&A
EBIT
Taxes
NOPAT
D&A
CapEx
Change in NWC
Unlevered Free Cash Flow
Terminal Value
Enterprise Value
Equity Value
Implied Share Price
```

### 推荐敏感性分析

```text
1. WACC vs Terminal Growth
2. Revenue CAGR vs Terminal EBIT Margin
3. Gross Margin vs R&D % of Revenue
```

---

## 4. 第三步：写投资 thesis

### 使用命令

```text
/equity-research:thesis AMD
```

或者：

```text
/equity-research:thesis 为 AMD 写一个 bull/base/bear investment thesis，重点分析 AI GPU、Data Center、Client PC、Embedded 和估值风险
```

### 应覆盖的问题

- AMD 是否能在 AI GPU 市场拿到足够份额？
- AMD 的 MI 系列 GPU 是否能形成可持续增长？
- Data Center CPU 是否继续从 Intel 手中拿份额？
- Client PC 周期恢复对收入有多大贡献？
- Embedded / Xilinx 业务是否恢复？
- 当前估值隐含了多高的收入增长和利润率？
- 最大 downside risk 是什么？

### 推荐输出结构

```text
Investment Rating / View
Price Target Framework
Bull Case
Base Case
Bear Case
Key Catalysts
Key Risks
What Would Change Our View
```

---

## 5. 第四步：做财报前瞻

### 使用命令

```text
/equity-research:earnings-preview AMD
```

或者：

```text
/equity-research:earnings-preview 为 AMD 做下一季度财报前瞻，重点关注 Data Center revenue、AI GPU guidance、gross margin、client recovery 和管理层对全年指引的表述
```

### 财报前需要关注的指标

| 指标 | 重要性 |
|---|---|
| Revenue | 是否超过市场预期 |
| Data Center Revenue | AI 和服务器 CPU 核心驱动 |
| Gross Margin | 产品组合和定价能力的关键指标 |
| Operating Margin | 经营杠杆是否显现 |
| EPS | 与 consensus 对比 |
| Guidance | 对下一季度和全年预期最重要 |
| AI GPU commentary | 市场最关注的叙事来源 |

### 输出建议

```text
Consensus Snapshot
Key Debate
Bull / Base / Bear Scenarios
Expected Stock Reaction
Questions for Management
Post-Earnings Checklist
```

---

## 6. 第五步：财报后分析

### 使用命令

```text
/equity-research:earnings-analysis AMD
```

或：

```text
/equity-research:earnings AMD
```

### 适合回答的问题

- AMD 财报是 beat 还是 miss？
- 哪个 segment 超预期或低于预期？
- Gross margin 是否支持长期 DCF 假设？
- 管理层对 AI GPU 的表述是否强化 thesis？
- Guidance 是否足以支撑估值？
- 财报后是否需要调整 DCF 或 price target？

### 输出建议

```text
Headline Results
Segment Performance
Guidance vs Consensus
Management Commentary
Model Changes
Valuation Impact
Investment View Update
```

---

## 7. 第六步：行业与竞争格局分析

### 使用命令

```text
/equity-research:sector 半导体行业，重点比较 AMD、NVIDIA、Intel、Broadcom、Marvell、Qualcomm
```

### 适合回答的问题

- AI accelerator 市场增长是否还能持续？
- AMD 与 NVIDIA 的差距在哪里？
- Intel 是否能在 CPU / foundry 上重新夺回份额？
- Broadcom 和 Marvell 在 AI networking 中的地位如何？
- 半导体估值是否已经过热？

---

## 8. 第七步：催化剂日历

### 使用命令

```text
/equity-research:catalysts AMD
```

### AMD 可能的重要催化剂

```text
Quarterly earnings
AI GPU shipment / customer updates
MI-series product launches
Cloud capex commentary from hyperscalers
Intel competitive updates
NVIDIA product cycle updates
Semiconductor industry conferences
Analyst day
Guidance revisions
```

---

## 9. 如果要生成 HTML 页面

可以让 Claude 把任何分析结果转成 HTML，并保存到本目录，例如：

```text
把 AMD DCF 框架生成一个 HTML 页面，保存到 D:\github\ai-html-tools\AMD\amd_dcf_framework.html
```

```text
把 AMD 可比公司分析生成一个 HTML 页面，保存到 D:\github\ai-html-tools\AMD\amd_comps_analysis.html
```

当前已生成的页面包括：

```text
D:\github\ai-html-tools\AMD\amd_dcf_framework.html
D:\github\ai-html-tools\AMD\amd_comps_analysis.html
```

---

## 10. 推荐的一次完整 AMD 分析 Prompt

可以直接使用下面的 prompt：

```text
请用 financial-analysis 和 equity-research 插件，为 AMD 做一个完整股票分析：
1. 先做 comparable company analysis，peer group 包括 NVDA、AVGO、INTC、QCOM、MRVL、TXN；
2. 再做 DCF 框架，重点分析 Data Center、AI GPU、gross margin、R&D、SG&A、tax rate、WACC、terminal growth；
3. 写一个 bull/base/bear investment thesis；
4. 列出未来 6-12 个月关键催化剂和主要风险；
5. 最后把结果整理成 HTML 页面，保存到 D:\github\ai-html-tools\AMD。
```

---

## 11. 推荐输出文件

完整项目可以包含：

```text
amd_comps_analysis.html
amd_dcf_framework.html
amd_investment_thesis.html
amd_earnings_preview.html
amd_catalyst_calendar.html
how_to_analyze_company_with_plugins.md
```

---

## 12. 注意事项

1. 如果有 FactSet、S&P Global、Daloopa、LSEG 等账号，应优先使用机构数据源。
2. 如果没有机构数据源，可以做公开数据版，但必须标注数据来源和限制。
3. DCF 不应只看单一 fair value，要结合 sensitivity table 和 peer multiples。
4. 对 AMD 这类 AI 相关股票，最关键的不是当前 earnings，而是未来收入规模和 terminal margin 是否能兑现。
5. 可比公司不能简单平均；NVIDIA、Broadcom、Intel、Qualcomm 的商业模式和利润结构差异很大。
6. 所有结论都应区分：事实数据、模型假设、投资判断。

---

## 13. 快速命令清单

```text
/financial-analysis:comps-analysis AMD
/financial-analysis:dcf-model AMD
/financial-analysis:3-statement-model AMD
/equity-research:thesis AMD
/equity-research:earnings-preview AMD
/equity-research:earnings-analysis AMD
/equity-research:sector 半导体行业，重点分析 AMD
/equity-research:catalysts AMD
```
