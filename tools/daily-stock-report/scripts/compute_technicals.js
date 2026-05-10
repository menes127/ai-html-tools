const fs = require('fs');

function average(values) {
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function movingAverage(bars, period, field = 'close') {
  if (!Array.isArray(bars) || bars.length < period) return null;
  return average(bars.slice(-period).map((bar) => Number(bar[field])).filter(Number.isFinite));
}

function rsi(bars, period = 14) {
  if (!Array.isArray(bars) || bars.length <= period) return null;
  const closes = bars.map((bar) => Number(bar.close));
  const changes = [];
  for (let i = 1; i < closes.length; i += 1) changes.push(closes[i] - closes[i - 1]);
  const recent = changes.slice(-period);
  const gains = recent.map((change) => Math.max(change, 0));
  const losses = recent.map((change) => Math.max(-change, 0));
  const avgGain = average(gains);
  const avgLoss = average(losses);
  if (!avgLoss) return 100;
  const rs = avgGain / avgLoss;
  return 100 - 100 / (1 + rs);
}

function round(value, digits = 2) {
  return Number.isFinite(value) ? Number(value.toFixed(digits)) : null;
}

function inferLevels(price, technicals = {}) {
  const close = Number(price.close);
  const high = Number(price.high);
  const low = Number(price.low);
  const pivot = round((high + low + close) / 3);
  const resistance1 = round(2 * pivot - low);
  const support1 = round(2 * pivot - high);
  const resistance2 = round(pivot + (high - low));
  const support2 = round(pivot - (high - low));
  const breakout = round(Math.max(high, resistance1));
  const invalidation = round(Math.min(support2, close * 0.9));
  const target = round(breakout + (breakout - support1));

  return {
    resistance: [resistance1, high, resistance2].filter(Number.isFinite),
    support: [support1, support2].filter(Number.isFinite),
    pivot,
    breakout,
    target,
    invalidation,
  };
}

function buildSignals(report) {
  const close = report.price.close;
  const rsi14 = report.technicals.rsi14;
  const relativeVolume = report.technicals.relativeVolume;
  const breakout = report.levels.breakout;
  const firstSupport = report.levels.support?.[0];
  const invalidation = report.levels.invalidation;

  const overbought = Number.isFinite(rsi14) && rsi14 >= 70;
  const strongVolume = Number.isFinite(relativeVolume) && relativeVolume >= 1.5;
  const nearBreakout = Number.isFinite(breakout) && close >= breakout * 0.97;

  let headline = '持有 / 观望';
  if (close > breakout && strongVolume && !overbought) headline = '加仓 / 突破确认';
  else if (nearBreakout && overbought) headline = '持有 / 不追高';
  else if (firstSupport && close < firstSupport) headline = '降风险 / 等待企稳';

  return {
    headline,
    strength: strongVolume ? '高' : '中高',
    positionSize: headline.includes('加仓') ? '3 / 4' : headline.includes('降风险') ? '1 / 4' : '2 / 4',
    summary: `趋势${nearBreakout ? '偏强' : '中性偏强'}，相对成交量${strongVolume ? '达到' : '未达到'}强确认阈值${overbought ? '，但 RSI 已超买' : ''}。`,
    addConditions: [
      firstSupport ? `回踩 ${firstSupport.toFixed(2)} 附近不破，并出现缩量企稳。` : '回踩关键支撑不破，并出现缩量企稳。',
      breakout ? `收盘站上 ${breakout.toFixed(2)}，且成交量 > 20 日均量 1.5x。` : '收盘站上突破位，且成交量 > 20 日均量 1.5x。',
      '继续跑赢 SPY / QQQ / SOXX / SMH。',
    ],
    reduceConditions: [
      breakout ? `接近 ${breakout.toFixed(2)} 附近出现高位放量滞涨。` : '接近压力位出现高位放量滞涨。',
      invalidation ? `跌破 ${invalidation.toFixed(2)} 风控线。` : '跌破风控线。',
      '半导体 ETF 同步转弱，个股相对强度消失。',
    ],
    holdConditions: ['已有仓位按趋势持有。', '没有放量突破确认时不追高。'],
  };
}

function computeTechnicals(rawReport) {
  const report = JSON.parse(JSON.stringify(rawReport));
  const bars = report.history || [];
  const price = report.price;

  if (!report.technicals) report.technicals = {};
  if (Number.isFinite(price.previousClose)) {
    report.technicals.dailyReturn = round(price.close / price.previousClose - 1, 4);
  }
  report.technicals.ma20 ??= round(movingAverage(bars, 20));
  report.technicals.ma50 ??= round(movingAverage(bars, 50));
  report.technicals.ma200 ??= round(movingAverage(bars, 200));
  report.technicals.avgVolume20d ??= round(movingAverage(bars, 20, 'volume'), 0);
  if (!Number.isFinite(report.technicals.relativeVolume) && report.technicals.avgVolume20d) {
    report.technicals.relativeVolume = round(price.volume / report.technicals.avgVolume20d, 2);
  }
  report.technicals.rsi14 ??= round(rsi(bars, 14), 1);

  if (!report.levels || !report.levels.breakout) report.levels = inferLevels(price, report.technicals);
  if (!report.signals) report.signals = buildSignals(report);
  report.warnings ??= [];

  return report;
}

if (require.main === module) {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];
  if (!inputPath || !outputPath) {
    console.error('Usage: node compute_technicals.js <raw_data.json> <report_data.json>');
    process.exit(1);
  }
  const raw = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  fs.writeFileSync(outputPath, JSON.stringify(computeTechnicals(raw), null, 2));
}

module.exports = { computeTechnicals, movingAverage, rsi, inferLevels, buildSignals };
