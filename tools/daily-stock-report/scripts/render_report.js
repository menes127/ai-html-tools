const fs = require('fs');
const path = require('path');

function money(value) {
  return Number.isFinite(value) ? `$${value.toFixed(2)}` : 'N/A';
}

function percent(value) {
  return Number.isFinite(value) ? `${(value * 100).toFixed(2)}%` : 'N/A';
}

function compactNumber(value) {
  if (!Number.isFinite(value)) return 'N/A';
  if (Math.abs(value) >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`;
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  return value.toLocaleString('en-US');
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function listItems(items = []) {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
}

function sourceItems(items = []) {
  return items.map((source) => {
    const title = escapeHtml(source.title || source.url || 'Source');
    const url = escapeHtml(source.url || '#');
    return `<li><a href="${url}">${title}</a></li>`;
  }).join('');
}

function benchmarkRows(benchmarks = {}) {
  return Object.entries(benchmarks).map(([ticker, data]) => (
    `<tr><td>${escapeHtml(ticker)}</td><td class="number">${money(Number(data.close))}</td><td class="number ${Number(data.dailyReturn) >= 0 ? 'positive' : 'negative'}">${percent(Number(data.dailyReturn))}</td><td class="number">${compactNumber(Number(data.volume))}</td><td>${escapeHtml(data.interpretation || '')}</td></tr>`
  )).join('');
}

function newsRows(news = []) {
  if (!news.length) return '<tr><td colspan="3">暂无结构化新闻；请在数据源中补充 catalysts/news 字段。</td></tr>';
  return news.map((item) => `<tr><td>${escapeHtml(item.title)}</td><td>${escapeHtml(item.impact)}</td><td>${escapeHtml(item.summary)}</td></tr>`).join('');
}

function levelRows(report) {
  const levels = report.levels || {};
  const resistance = levels.resistance || [];
  const support = levels.support || [];
  return [
    `<tr><td>压力位</td><td>${resistance.map(money).join(' / ') || 'N/A'}</td><td>接近压力区若放量滞涨，考虑部分兑现或等待突破确认。</td></tr>`,
    `<tr><td>突破确认</td><td>${money(levels.breakout)}</td><td>需要收盘站上且成交量超过 20 日均量 1.5x，才视为强确认。</td></tr>`,
    `<tr><td>上行目标</td><td>${money(levels.target)}</td><td>突破确认后的目标观察区，接近目标应提高止盈纪律。</td></tr>`,
    `<tr><td>Pivot</td><td>${money(levels.pivot)}</td><td>短线多空平衡位；回踩不破更适合观察低吸。</td></tr>`,
    `<tr><td>支撑位</td><td>${support.map(money).join(' / ') || 'N/A'}</td><td>缩量企稳且板块未转弱时，才考虑加仓或加回仓位。</td></tr>`,
    `<tr><td>风控失效</td><td>${money(levels.invalidation)}</td><td>跌破后代表短线多头结构明显走弱。</td></tr>`,
  ].join('');
}

function priceSvg(report) {
  const { price, levels, technicals } = report;
  const values = [price.high, price.low, price.open, price.close, levels.breakout, levels.pivot, levels.invalidation, ...(levels.support || []), ...(levels.resistance || [])].filter(Number.isFinite);
  const max = Math.max(...values) * 1.02;
  const min = Math.min(...values) * 0.98;
  const y = (value) => 40 + ((max - value) / (max - min)) * 230;
  const line = (value, cls, label, tx = 500) => Number.isFinite(value)
    ? `<line class="level-line ${cls}" x1="80" y1="${y(value).toFixed(1)}" x2="690" y2="${y(value).toFixed(1)}" /><text x="${tx}" y="${(y(value) - 7).toFixed(1)}" font-size="13" font-weight="800" fill="#172033">${escapeHtml(label)} ${money(value)}</text>`
    : '';
  const bodyY = Math.min(y(price.open), y(price.close));
  const bodyH = Math.max(Math.abs(y(price.open) - y(price.close)), 4);

  return `<svg viewBox="0 0 760 360" role="img" aria-label="${escapeHtml(report.metadata.ticker)} price chart">
    <rect x="0" y="0" width="760" height="360" fill="#ffffff" />
    <line x1="70" y1="40" x2="700" y2="40" stroke="#edf2f7" />
    <line x1="70" y1="95" x2="700" y2="95" stroke="#edf2f7" />
    <line x1="70" y1="150" x2="700" y2="150" stroke="#edf2f7" />
    <line x1="70" y1="205" x2="700" y2="205" stroke="#edf2f7" />
    <line x1="70" y1="260" x2="700" y2="260" stroke="#edf2f7" />
    ${line(levels.breakout, 'level-breakout', '突破')}
    ${line(levels.resistance?.[levels.resistance.length - 1], 'level-resistance', '压力')}
    ${line(levels.pivot, 'level-pivot', 'Pivot')}
    ${line(levels.support?.[0], 'level-support', '支撑')}
    ${line(levels.invalidation, 'level-resistance', '失效')}
    <line class="candle-wick" x1="265" y1="${y(price.high).toFixed(1)}" x2="265" y2="${y(price.low).toFixed(1)}" />
    <rect class="candle-body" x="230" y="${bodyY.toFixed(1)}" width="70" height="${bodyH.toFixed(1)}" rx="5" />
    <text x="205" y="${(y(price.high) - 9).toFixed(1)}" font-size="13" font-weight="800" fill="#067647">High ${money(price.high)}</text>
    <text x="305" y="${(y(price.close) + 14).toFixed(1)}" font-size="13" font-weight="800" fill="#067647">Close ${money(price.close)}</text>
    <rect class="volume-actual" x="210" y="292" width="110" height="44" rx="6" />
    <line class="volume-average" x1="120" y1="300" x2="650" y2="300" />
    <text x="330" y="306" font-size="13" font-weight="800" fill="#b54708">20日均量 ${compactNumber(Number(technicals.avgVolume20d))}</text>
    <text x="210" y="352" font-size="13" font-weight="800" fill="#067647">成交量 ${compactNumber(Number(price.volume))}；相对量 ${Number.isFinite(technicals.relativeVolume) ? `${technicals.relativeVolume.toFixed(2)}x` : 'N/A'}</text>
  </svg>`;
}

function renderReport(report, templatePath) {
  const template = fs.readFileSync(templatePath, 'utf8');
  const ticker = report.metadata.ticker;
  const replacements = {
    TITLE: `${ticker} 股票日报 — ${report.metadata.reportDate}`,
    H1: `${ticker} 股票日报：${report.metadata.reportDate}`,
    SUBTITLE: `${report.metadata.companyName} 日报，市场数据日 ${report.metadata.marketDataDate}，覆盖个股量价、大环境、关键价位和短线操作信号。`,
    TICKER: ticker,
    REPORT_DATE: report.metadata.reportDate,
    MARKET_DATA_DATE: report.metadata.marketDataDate,
    HEADLINE_SIGNAL: report.signals.headline,
    SIGNAL_SUMMARY: report.signals.summary,
    SIGNAL_STRENGTH: report.signals.strength || 'N/A',
    POSITION_SIZE: report.signals.positionSize,
    DECISION_TEXT: report.signals.summary,
    BENCHMARK_ROWS: benchmarkRows(report.benchmarks),
    PRICE_SVG: priceSvg(report),
    OPEN: money(report.price.open),
    HIGH: money(report.price.high),
    LOW: money(report.price.low),
    CLOSE: money(report.price.close),
    VOLUME: compactNumber(report.price.volume),
    RSI14: Number.isFinite(report.technicals.rsi14) ? report.technicals.rsi14.toFixed(1) : 'N/A',
    RELATIVE_VOLUME: Number.isFinite(report.technicals.relativeVolume) ? `${report.technicals.relativeVolume.toFixed(2)}x` : 'N/A',
    LEVEL_ROWS: levelRows(report),
    ADD_CONDITIONS: listItems(report.signals.addConditions),
    HOLD_CONDITIONS: listItems(report.signals.holdConditions),
    REDUCE_CONDITIONS: listItems(report.signals.reduceConditions),
    NEWS_ROWS: newsRows(report.news),
    RISK_ITEMS: listItems(report.signals.reduceConditions),
    SOURCE_ITEMS: sourceItems(report.sources),
    FOOTER: `${ticker} 股票日报 ${report.metadata.reportDate}。本页面为研究和交易框架，不构成投资建议。`,
  };

  return Object.entries(replacements).reduce((html, [key, value]) => html.replaceAll(`{{${key}}}`, value ?? ''), template);
}

function writeReport(report, outputDir, templatePath) {
  fs.mkdirSync(outputDir, { recursive: true });
  const fileName = `${report.metadata.ticker.toLowerCase()}_daily_stock_report_${report.metadata.reportDate}.html`;
  const outputHtml = path.join(outputDir, fileName);
  fs.writeFileSync(outputHtml, renderReport(report, templatePath));
  return outputHtml;
}

if (require.main === module) {
  const [inputPath, outputDir, templatePath = path.resolve(__dirname, '..', 'templates', 'daily-stock-report.html')] = process.argv.slice(2);
  if (!inputPath || !outputDir) {
    console.error('Usage: node render_report.js <report_data.json> <output_dir> [template_path]');
    process.exit(1);
  }
  const report = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  process.stdout.write(writeReport(report, outputDir, templatePath));
}

module.exports = { renderReport, writeReport, money, percent, compactNumber };
