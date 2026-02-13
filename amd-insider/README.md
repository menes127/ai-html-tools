# AMD Insider Monitor 说明文档

这个目录提供一个可在 GitHub Pages 展示的 **AMD 高管 Form 4 交易监控面板**，并通过 GitHub Actions 每日自动更新数据。

## 文件结构

- `amd_insider_monitor.py`：抓取并解析 SEC Form 4 数据脚本
- `data/index.json`：数据索引（包含可用年份列表）
- `data/YYYY.json`：按年分片的交易数据
- `index.html`：dashboard（按需加载年份数据）
- `../.github/workflows/update-amd-insider.yml`：每日自动更新任务

## 脚本工作流程

1. 拉取 AMD submissions：`https://data.sec.gov/submissions/CIK0000002488.json`
2. 过滤 `4` / `4/A`，并按 `--days` 做时间窗口
3. 下载并解析每个 filing 的 XML，提取 non-derivative 交易
4. 输出结果：
   - `--output`：单文件（兼容模式）
   - `--output-dir`：按年分片（推荐）

## 为什么改成按年分片

之前是一个大 JSON，随着回看天数变大，页面首次加载慢。

现在改为：

- 首页先加载 `data/index.json`
- 默认只加载当前年份 `data/YYYY.json`
- 切换年份时再按需加载对应文件

这样可以显著减少首屏数据量，实现“增量加载”。

## 常用命令

在仓库根目录执行：

```bash
# 推荐：按年分片输出
python amd-insider/amd_insider_monitor.py --days 365 --output-dir amd-insider/data

# 兼容：单文件输出
python amd-insider/amd_insider_monitor.py --days 365 --output amd-insider/amd_insider_trades.json

# 本地预览
python -m http.server 8000
# 打开 http://localhost:8000/amd-insider/
```

## GitHub Actions 自动更新

工作流：`.github/workflows/update-amd-insider.yml`

- 定时：每天 01:00 UTC（09:00 Asia/Shanghai）
- 手动：`Run workflow` 时可设置 `days`（默认 365）
- 更新输出：`amd-insider/data/*.json`

## SEC 访问注意事项

建议在仓库 Secrets 里配置：

- `SEC_USER_AGENT`

示例：

```text
menes127 menes20240711@gmail.com
```

脚本已包含 403/429/5xx 重试与退避。

## 交易代码速查

- `P`：公开市场买入
- `S`：公开市场卖出
- `M`：期权行权
- `F`：税务预扣相关（常见于 RSU）

> 注意：`S` 不一定是看空，需结合 footnote（10b5-1 / 税务）判断。
