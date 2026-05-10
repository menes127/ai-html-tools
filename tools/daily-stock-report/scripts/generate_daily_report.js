const fs = require('fs');
const path = require('path');
const { fetchDailyData } = require('./fetch_daily_data');
const { computeTechnicals } = require('./compute_technicals');
const { writeReport } = require('./render_report');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) args[key] = true;
    else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeJson(file, data) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function summaryFor(report, outputHtml, runDir, warnings = []) {
  return {
    ticker: report.metadata.ticker,
    reportDate: report.metadata.reportDate,
    marketDataDate: report.metadata.marketDataDate,
    provider: report.metadata.provider || 'unknown',
    outputHtml,
    headlineSignal: report.signals.headline,
    positionSize: report.signals.positionSize,
    keyLevels: {
      breakout: report.levels?.breakout ?? null,
      firstSupport: report.levels?.support?.[0] ?? null,
      invalidation: report.levels?.invalidation ?? null,
      target: report.levels?.target ?? null,
    },
    runDir,
    dataWarnings: [...(report.warnings || []), ...warnings],
  };
}

async function generateDailyReport(options) {
  const rootDir = path.resolve(__dirname, '..');
  const outputDir = path.resolve(options.output || process.cwd());
  const reportDate = options.date || new Date().toISOString().slice(0, 10);
  const ticker = (options.ticker || 'AMD').toUpperCase();
  const benchmarks = String(options.benchmarks || 'SPY,QQQ,SOXX,SMH').split(',').map((item) => item.trim()).filter(Boolean);
  const runDir = path.join(rootDir, 'cache', `${ticker}_${reportDate}`);
  const templatePath = options.template || path.join(rootDir, 'templates', 'daily-stock-report.html');
  ensureDir(runDir);

  let rawData;
  const warnings = [];
  if (options['input-json']) {
    rawData = JSON.parse(fs.readFileSync(path.resolve(options['input-json']), 'utf8'));
  } else {
    const fetchResult = await fetchDailyData({ ticker, date: reportDate, benchmarks, provider: options.provider || 'auto', refresh: Boolean(options.refresh), cacheDir: path.join(rootDir, 'cache') });
    rawData = fetchResult.data;
    if (fetchResult.fromCache) warnings.push(`Loaded raw data from cache: ${fetchResult.cacheFile}`);
  }

  const rawDataPath = path.join(runDir, 'raw_data.json');
  writeJson(rawDataPath, rawData);

  const report = computeTechnicals(rawData);
  const reportDataPath = path.join(runDir, 'report_data.json');
  writeJson(reportDataPath, report);

  let outputHtml = null;
  if (!options['summary-only']) {
    outputHtml = writeReport(report, outputDir, templatePath);
  }

  const summary = summaryFor(report, outputHtml, runDir, warnings);
  const summaryPath = path.join(outputDir, `${report.metadata.ticker.toLowerCase()}_daily_stock_report_${report.metadata.reportDate}.summary.json`);
  writeJson(summaryPath, summary);

  return { summary, summaryPath };
}

if (require.main === module) {
  const args = parseArgs(process.argv.slice(2));
  generateDailyReport(args).then(({ summary, summaryPath }) => {
    process.stdout.write(JSON.stringify({ summaryPath, ...summary }, null, 2));
  }).catch((error) => {
    process.stderr.write(JSON.stringify({ error: error.message, stack: error.stack }, null, 2));
    process.exit(1);
  });
}

module.exports = { generateDailyReport, parseArgs };
