const fs = require('fs');
const https = require('https');
const path = require('path');

const STOCK_ANALYSIS_BASE_URL = 'https://stockanalysis.com';
const ETF_TICKERS = new Set(['SPY', 'QQQ', 'SOXX', 'SMH']);

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function cachePath(cacheDir, ticker, reportDate) {
  return path.join(cacheDir, `${ticker.toUpperCase()}_${reportDate}_raw_data.json`);
}

function loadFromCache(cacheDir, ticker, reportDate) {
  const file = cachePath(cacheDir, ticker, reportDate);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function saveToCache(cacheDir, ticker, reportDate, data) {
  ensureDir(cacheDir);
  const file = cachePath(cacheDir, ticker, reportDate);
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
  return file;
}

function stockAnalysisUrl(ticker) {
  const upper = ticker.toUpperCase();
  const type = ETF_TICKERS.has(upper) ? 'etf' : 'stocks';
  return `${STOCK_ANALYSIS_BASE_URL}/${type}/${upper.toLowerCase()}/history/`;
}

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 daily-stock-report/1.0' } }, (response) => {
      if (response.statusCode < 200 || response.statusCode >= 300) {
        response.resume();
        reject(new Error(`HTTP ${response.statusCode} for ${url}`));
        return;
      }
      let body = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => { body += chunk; });
      response.on('end', () => resolve(body));
    }).on('error', reject);
  });
}

function decodeHtml(value) {
  return String(value)
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .trim();
}

function stripTags(value) {
  return decodeHtml(String(value).replace(/<!--.*?-->/gs, '').replace(/<[^>]+>/g, '').trim());
}

function parseNumber(value) {
  const text = stripTags(value).replace(/,/g, '').replace(/%/g, '');
  const match = text.match(/-?\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function parseDate(value) {
  const text = stripTags(value);
  const timestamp = Date.parse(`${text} 00:00:00 UTC`);
  if (!Number.isFinite(timestamp)) return null;
  return new Date(timestamp).toISOString().slice(0, 10);
}

function parseStockAnalysisHtml(html) {
  const tableMatch = html.match(/<table[\s\S]*?<tbody>([\s\S]*?)<\/tbody>/i);
  if (!tableMatch) return [];
  const rowMatches = [...tableMatch[1].matchAll(/<tr[\s\S]*?<\/tr>/gi)].map((match) => match[0]);
  const bars = rowMatches.map((row) => {
    const cells = [...row.matchAll(/<td[\s\S]*?>([\s\S]*?)<\/td>/gi)].map((match) => match[1]);
    if (cells.length < 8) return null;
    return {
      date: parseDate(cells[0]),
      open: parseNumber(cells[1]),
      high: parseNumber(cells[2]),
      low: parseNumber(cells[3]),
      close: parseNumber(cells[4]),
      volume: parseNumber(cells[7]),
    };
  }).filter((bar) => bar && bar.date && [bar.open, bar.high, bar.low, bar.close, bar.volume].every(Number.isFinite));

  return bars.sort((a, b) => a.date.localeCompare(b.date));
}

function findMarketBar(history, reportDate) {
  const eligible = history.filter((bar) => bar.date <= reportDate);
  if (!eligible.length) return null;
  const index = history.indexOf(eligible[eligible.length - 1]);
  return { bar: history[index], previousBar: index > 0 ? history[index - 1] : null, index };
}

function companyNameFor(ticker) {
  const names = {
    AMD: 'Advanced Micro Devices',
    SPY: 'SPDR S&P 500 ETF Trust',
    QQQ: 'Invesco QQQ Trust',
    SOXX: 'iShares Semiconductor ETF',
    SMH: 'VanEck Semiconductor ETF',
  };
  return names[ticker.toUpperCase()] || ticker.toUpperCase();
}

function sessionType(reportDate, marketDataDate) {
  if (reportDate === marketDataDate) return 'regular';
  const day = new Date(`${reportDate}T00:00:00Z`).getUTCDay();
  return day === 0 || day === 6 ? 'weekend' : 'non-trading-day';
}

function rangeHigh(history, field) {
  const values = history.map((bar) => Number(bar[field])).filter(Number.isFinite);
  return values.length ? Math.max(...values) : null;
}

function rangeLow(history, field) {
  const values = history.map((bar) => Number(bar[field])).filter(Number.isFinite);
  return values.length ? Math.min(...values) : null;
}

async function fetchStockAnalysisHistory(ticker) {
  const url = stockAnalysisUrl(ticker);
  const html = await fetchText(url);
  const history = parseStockAnalysisHtml(html);
  if (!history.length) throw new Error(`No StockAnalysis daily data for ${ticker}`);
  return { history, url };
}

function benchmarkInterpretation(ticker, dailyReturn) {
  if (!Number.isFinite(dailyReturn)) return '数据不足。';
  const direction = dailyReturn >= 0 ? '上涨' : '下跌';
  const strength = Math.abs(dailyReturn) >= 0.02 ? '明显' : '温和';
  if (ticker === 'SPY') return `大盘${strength}${direction}，用于判断风险偏好。`;
  if (ticker === 'QQQ') return `科技成长股${strength}${direction}，影响高 beta 成长股环境。`;
  return `半导体 ETF ${strength}${direction}，用于验证板块共振。`;
}

async function buildBenchmark(ticker, reportDate, warnings, sources) {
  try {
    const { history, url } = await fetchStockAnalysisHistory(ticker);
    const found = findMarketBar(history, reportDate);
    if (!found) throw new Error(`No benchmark bar on or before ${reportDate}`);
    const { bar, previousBar } = found;
    const dailyReturn = previousBar ? bar.close / previousBar.close - 1 : null;
    sources.push({ title: `StockAnalysis — ${ticker.toUpperCase()} historical prices`, url });
    return {
      close: bar.close,
      dailyReturn,
      volume: bar.volume,
      marketDataDate: bar.date,
      interpretation: benchmarkInterpretation(ticker.toUpperCase(), dailyReturn),
    };
  } catch (error) {
    warnings.push(`Benchmark ${ticker} unavailable: ${error.message}`);
    return {};
  }
}

async function buildPublicReport(ticker, reportDate, benchmarks) {
  const upper = ticker.toUpperCase();
  const warnings = [];
  const sources = [];
  const { history, url } = await fetchStockAnalysisHistory(upper);
  const found = findMarketBar(history, reportDate);
  if (!found) throw new Error(`No ${upper} bar on or before ${reportDate}`);

  const { bar, previousBar, index } = found;
  const marketHistory = history.slice(0, index + 1);
  const oneYearHistory = marketHistory.slice(-260);
  const benchmarkEntries = await Promise.all(benchmarks.map(async (benchmark) => [benchmark.toUpperCase(), await buildBenchmark(benchmark, reportDate, warnings, sources)]));

  if (bar.date !== reportDate) warnings.push(`Report date ${reportDate} is not a trading date in provider data; using latest market data date ${bar.date}.`);
  sources.unshift({ title: `StockAnalysis — ${upper} historical prices`, url });

  return {
    metadata: {
      ticker: upper,
      companyName: companyNameFor(upper),
      reportDate,
      marketDataDate: bar.date,
      sessionType: sessionType(reportDate, bar.date),
      language: 'zh-CN',
      provider: 'stockanalysis',
    },
    price: {
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
      previousClose: previousBar?.close ?? null,
      volume: bar.volume,
      afterHours: null,
      fiftyTwoWeekHigh: rangeHigh(oneYearHistory, 'high'),
      fiftyTwoWeekLow: rangeLow(oneYearHistory, 'low'),
    },
    history: marketHistory,
    technicals: {},
    levels: null,
    benchmarks: Object.fromEntries(benchmarkEntries),
    signals: null,
    news: [],
    sources,
    warnings,
  };
}

function fallbackReport(ticker, reportDate, benchmarks = ['SPY', 'QQQ', 'SOXX', 'SMH'], reason = null) {
  const upper = ticker.toUpperCase();
  const dataWarnings = [
    reason ? `Real market data fetch failed; using deterministic fallback data. Reason: ${reason}` : 'Using deterministic fallback data. Provide --input-json or add a market data provider for production daily reports.',
  ];

  if (upper === 'AMD') {
    return {
      metadata: {
        ticker: 'AMD',
        companyName: 'Advanced Micro Devices',
        reportDate,
        marketDataDate: reportDate,
        sessionType: 'regular',
        language: 'zh-CN',
        provider: 'fallback',
      },
      price: {
        open: 418.59,
        high: 456.29,
        low: 418.29,
        close: 455.19,
        previousClose: 408.46,
        volume: 56904732,
        afterHours: 461.2,
        fiftyTwoWeekHigh: 456.29,
        fiftyTwoWeekLow: 101.56,
      },
      technicals: {
        rsi14: 80.8,
        ma20: null,
        ma50: 254.51,
        ma200: 217.35,
        avgVolume20d: 46680000,
        relativeVolume: 1.22,
      },
      levels: {
        resistance: [444.08, 451.3, 456.29, 465.72],
        support: [422.44, 408.02, 400.8],
        pivot: 429.66,
        breakout: 465.72,
        target: 474.62,
        invalidation: 395,
      },
      benchmarks: {
        SPY: { close: 737.62, dailyReturn: 0.0083, volume: 47230000, interpretation: '大盘风险偏好改善。' },
        QQQ: { close: 711.23, dailyReturn: 0.0234, volume: 44320000, interpretation: '科技成长股环境明显转强。' },
        SOXX: { close: 520.3, dailyReturn: 0.0567, volume: 7520000, interpretation: '半导体板块强共振。' },
        SMH: { close: 566.54, dailyReturn: 0.049, volume: 8440000, interpretation: '半导体 ETF 领涨，验证板块 beta。' },
      },
      signals: null,
      news: [],
      sources: [
        { title: 'StockAnalysis — AMD quote', url: 'https://stockanalysis.com/stocks/amd/' },
        { title: 'FX Leaders — AMD technical levels', url: 'https://www.fxleaders.com/live-rates/amd/' },
      ],
      warnings: dataWarnings,
    };
  }

  return {
    metadata: {
      ticker: upper,
      companyName: upper,
      reportDate,
      marketDataDate: reportDate,
      sessionType: 'regular',
      language: 'zh-CN',
      provider: 'fallback',
    },
    price: { open: 100, high: 104, low: 98, close: 102, previousClose: 100, volume: 10000000 },
    technicals: {},
    levels: null,
    benchmarks: Object.fromEntries(benchmarks.map((benchmark) => [benchmark, {}])),
    signals: null,
    news: [],
    sources: [],
    warnings: dataWarnings,
  };
}

async function fetchDailyData(options) {
  const ticker = options.ticker || 'AMD';
  const reportDate = options.date || new Date().toISOString().slice(0, 10);
  const cacheDir = options.cacheDir || path.resolve(__dirname, '..', 'cache');
  const benchmarks = options.benchmarks || ['SPY', 'QQQ', 'SOXX', 'SMH'];
  const provider = options.provider || 'auto';

  if (!options.refresh) {
    const cached = loadFromCache(cacheDir, ticker, reportDate);
    if (cached) return { data: cached, cacheFile: cachePath(cacheDir, ticker, reportDate), fromCache: true };
  }

  let data;
  if (provider === 'fallback') {
    data = fallbackReport(ticker, reportDate, benchmarks);
  } else {
    try {
      data = await buildPublicReport(ticker, reportDate, benchmarks);
    } catch (error) {
      data = fallbackReport(ticker, reportDate, benchmarks, error.message);
    }
  }

  const cacheFile = saveToCache(cacheDir, ticker, reportDate, data);
  return { data, cacheFile, fromCache: false };
}

if (require.main === module) {
  const [ticker = 'AMD', reportDate = new Date().toISOString().slice(0, 10), outputPath] = process.argv.slice(2);
  fetchDailyData({ ticker, date: reportDate, refresh: true }).then(({ data }) => {
    if (outputPath) fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    else process.stdout.write(JSON.stringify(data, null, 2));
  }).catch((error) => {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  });
}

module.exports = { fetchDailyData, parseStockAnalysisHtml, fetchStockAnalysisHistory, buildPublicReport };
