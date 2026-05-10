# Daily Stock Report 斜杠命令配置清单（ai-html-tools）

> 目标：把 `tools/daily-stock-report` 这套脚本封装成 Claude 可斜杠触发入口。
>
> 说明：`ai-html-tools` 当前没有插件骨架（无 `.claude-plugin/plugin.json`、`commands/`、`skills/`），先按下面最小结构补齐即可。

---

## 1) 目录结构（最小可用）

在仓库根目录创建：

```text
claude-plugin/
  .claude-plugin/
    plugin.json
  commands/
    daily-stock-report.md
  skills/
    daily-stock-report/
      SKILL.md
```

---

## 2) plugin.json（命令发现清单）

路径：`claude-plugin/.claude-plugin/plugin.json`

```json
{
  "name": "ai-html-tools",
  "version": "0.1.0",
  "description": "Slash commands for ai-html-tools report generators",
  "components": {
    "commands": {
      "enabled": true,
      "path": "../commands"
    },
    "skills": {
      "enabled": true,
      "path": "../skills"
    }
  }
}
```

---

## 3) 斜杠命令定义（commands）

路径：`claude-plugin/commands/daily-stock-report.md`

```markdown
---
description: Generate a daily single-stock HTML report with benchmark context
argument-hint: "[ticker] [date=YYYY-MM-DD, optional] [output=path, optional] [benchmarks=CSV, optional]"
---

Load the `daily-stock-report` skill and generate the report via:

`node tools/daily-stock-report/scripts/generate_daily_report.js`

Workflow requirements:
1. Parse args into ticker/date/output/benchmarks/refresh/provider.
2. Execute script command with those args.
3. Read only the generated `.summary.json` for response.
4. Return outputHtml path, headlineSignal, keyLevels, and dataWarnings.
```

---

## 4) Skill 封装（skills）

路径：`claude-plugin/skills/daily-stock-report/SKILL.md`

```markdown
# Daily Stock Report Skill

Generate a single-stock daily HTML report by running local Node scripts.

## Inputs
- ticker (default: AMD)
- date (default: today)
- output (default: AMD)
- benchmarks (default: SPY,QQQ,SOXX,SMH)
- refresh (default: false)
- provider (default: auto)

## Command

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --ticker <TICKER> \
  --date <DATE> \
  --output <OUTPUT_DIR> \
  --benchmarks <CSV> \
  [--refresh] \
  [--provider <PROVIDER>]
```

## Response Contract
After execution, read only:
- `<output>/<ticker>_daily_stock_report_<date>.summary.json`

Return compactly:
- summaryPath
- outputHtml
- provider
- marketDataDate
- headlineSignal
- positionSize
- keyLevels (breakout/firstSupport/invalidation/target)
- dataWarnings

## Rules
- Do not read generated HTML unless user asks.
- Prefer `--refresh` when user asks for real-time/latest data.
- If report date is non-trading day, accept provider backfill date and surface warning.
```

---

## 5) 命令参数映射清单

| Slash 参数 | 脚本参数 | 默认值 |
|---|---|---|
| ticker | `--ticker` | `AMD` |
| date | `--date` | 当天 |
| output | `--output` | `AMD` |
| benchmarks | `--benchmarks` | `SPY,QQQ,SOXX,SMH` |
| refresh=true | `--refresh` | false |
| provider | `--provider` | `auto` |

---

## 6) 手动验证（接入后）

1. 在 Claude 中触发：
   - `/my:daily-stock-report AMD date=2026-05-10 output=AMD/report benchmarks=SPY,QQQ,SOXX,SMH refresh=true`
2. 预期脚本执行后输出：
   - `AMD/report/amd_daily_stock_report_2026-05-10.html`
   - `AMD/report/amd_daily_stock_report_2026-05-10.summary.json`
3. summary 关键检查：
   - `provider = stockanalysis`
   - `headlineSignal` 有值
   - `dataWarnings` 仅包含合理提示（如周末回补）

---

## 7) 当前状态说明

- 这份清单已可直接复制到你的插件骨架。
- `ai-html-tools` 目前是普通仓库，不是已注册 Claude 插件仓库；只有把上述目录纳入插件加载路径后，斜杠命令才会真正可用。
