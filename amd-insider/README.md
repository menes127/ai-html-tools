# Insider Monitor (AMD / NVDA)

该目录提供一个可在 GitHub Pages 展示的 Form 4 监控面板。当前版本使用 **Supabase 作为唯一数据源**，不再依赖本地 `data/YYYY.json` 作为运行时读取。

## 项目结构

- `amd_insider_monitor.py`：抓取并解析 SEC Form 4，并 upsert 到 Supabase
- `supabase/schema.sql`：表结构、视图、RLS 与只读授权
- `index.html`：前端 dashboard（读取 Supabase `v_summary` / `v_years` / `v_transactions`）
- `../.github/workflows/update-amd-insider.yml`：每日自动同步到 Supabase（最近 30 天，AMD + NVDA）

## Supabase 初始化

1. 在 Supabase SQL Editor 执行：`supabase/schema.sql`
2. 确保匿名角色可读视图：`v_summary`、`v_years`、`v_transactions`
3. 在 GitHub Secrets 配置：
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SEC_USER_AGENT`

## 本地环境变量（`.env`）

在 `amd-insider/.env` 中配置：

```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<publishable-or-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SEC_USER_AGENT=<name email@example.com>
```

- `SUPABASE_SERVICE_ROLE_KEY` 仅用于后端写入（抓取脚本），不要暴露到前端。
- `SUPABASE_ANON_KEY` 仅用于前端只读查询（配合 RLS 只读视图）。

## 常用命令

```bash
# 同步最近 365 天（默认 AMD）
python3 amd_insider_monitor.py --days 365

# 只更新某一年（默认 AMD）
python3 amd_insider_monitor.py --year 2025

# 同步多个公司（可重复 --company）
python3 amd_insider_monitor.py --days 365 --company AMD --company NVDA
```

当前内置支持：`AMD`、`NVDA`。如传入不支持的 ticker，脚本会直接报错并退出。

## 前端本地预览

`index.html` 通过 `config.js` 读取前端只读配置：

```js
window.SUPABASE_URL = 'https://<project>.supabase.co';
window.SUPABASE_ANON_KEY = '<anon-key>';
window.ALPHA_VANTAGE_API_KEY = '<alpha-vantage-key>';
// 可选：覆盖前端公司下拉项（默认 AMD/NVDA）
// window.DASHBOARD_COMPANIES = [
//   { ticker: 'AMD', name: 'Advanced Micro Devices' },
//   { ticker: 'NVDA', name: 'NVIDIA' },
// ];
```

请确保 `config.js` 中仅包含公开可见的 URL + publishable/anon key，不要放 service role key。  
`ALPHA_VANTAGE_API_KEY` 用于前端行情展示（价格强弱/最新价/K 线），可使用免费 key。

前端页面顶部支持公司切换，下拉选择会联动：
- 股票信号（价格强弱、最新价、K 线）
- 年份列表与汇总卡片
- 趋势表与交易明细

然后启动静态服务：

```bash
python3 -m http.server 8000
# 在当前目录启动时打开 http://localhost:8000/
# 在仓库根目录启动时打开 http://localhost:8000/amd-insider/
```

建议先在浏览器开发者工具确认：
- `window.SUPABASE_URL` 不为空
- `window.SUPABASE_ANON_KEY` 不为空

## SEC 访问提示

- 建议 `SEC_USER_AGENT` 使用真实联系方式（邮箱）。
- 脚本已包含 403/429/5xx 退避重试。

## GitHub Pages 部署说明

页面是纯静态资源，`index.html` 使用相对路径加载 `./config.js`，可直接部署到 GitHub Pages。  
请确认 Pages 发布分支/目录中同时包含：

- `amd-insider/index.html`
- `amd-insider/config.js`

若 `config.js` 缺失，页面会提示未配置 `SUPABASE_URL / SUPABASE_ANON_KEY`。

## GitHub Actions 同步策略

工作流文件：`../.github/workflows/update-amd-insider.yml`

- 定时任务：每天运行一次
- 默认增量范围：最近 `30` 天
- 默认公司：`AMD` + `NVDA`
- 手动触发：与定时任务一致，仍同步最近 `30` 天（AMD + NVDA）
