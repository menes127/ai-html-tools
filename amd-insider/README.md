# AMD Insider Monitor

该目录提供一个可在 GitHub Pages 展示的 AMD Form 4 监控面板。当前版本使用 **Supabase 作为唯一数据源**，不再依赖本地 `data/YYYY.json` 作为运行时读取。

## 项目结构

- `amd_insider_monitor.py`：抓取并解析 SEC Form 4，并 upsert 到 Supabase
- `scripts/backfill_json_to_supabase.py`：一次性把历史 `data/*.json` 回填到 Supabase
- `supabase/schema.sql`：表结构、视图、RLS 与只读授权
- `index.html`：前端 dashboard（读取 Supabase `v_summary` / `v_years` / `v_transactions`）
- `../.github/workflows/update-amd-insider.yml`：每日自动同步到 Supabase

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

- `SUPABASE_SERVICE_ROLE_KEY` 仅用于后端写入（抓取/回填脚本），不要暴露到前端。
- `SUPABASE_ANON_KEY` 仅用于前端只读查询（配合 RLS 只读视图）。

## 常用命令

```bash
# 同步最近 365 天到 Supabase
python3 amd_insider_monitor.py --days 365 --to-supabase

# 只更新某一年
python3 amd_insider_monitor.py --year 2025 --to-supabase

# 历史 JSON 回填预演
python3 scripts/backfill_json_to_supabase.py --dry-run

# 历史 JSON 回填执行
python3 scripts/backfill_json_to_supabase.py --batch-size 500
```

## 前端本地预览

`index.html` 依赖全局变量（可从 `.env` 手动复制）：

```html
<script>
  window.SUPABASE_URL = 'https://<project>.supabase.co';
  window.SUPABASE_ANON_KEY = '<anon-key>';
</script>
```

然后启动静态服务：

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000/amd-insider/
```

建议先在浏览器开发者工具确认：
- `window.SUPABASE_URL` 不为空
- `window.SUPABASE_ANON_KEY` 不为空

## SEC 访问提示

- 建议 `SEC_USER_AGENT` 使用真实联系方式（邮箱）。
- 脚本已包含 403/429/5xx 退避重试。
