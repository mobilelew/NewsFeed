// NEWS READER iPHONE WIDGET — Scriptable
// Replace this with the raw URL of your published feed.json.
const FEED_URL = 'https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/feed.json';
const REFRESH_MINUTES = 45; // iOS determines actual widget refresh timing.

const fm = FileManager.local();
const cache = fm.joinPath(fm.documentsDirectory(), 'NewsReader-feed-cache.json');
const widget = new ListWidget();
widget.backgroundColor = new Color('#101827');
widget.setPadding(14, 15, 12, 15);
widget.url = 'https://chatgpt.com/'; // Optionally replace with your News Reader project URL.

function label(text, size, color, bold) {
  const t = widget.addText(String(text || ''));
  t.font = bold ? Font.boldSystemFont(size) : Font.systemFont(size);
  t.textColor = new Color(color);
  t.lineLimit = 2;
  return t;
}
function fmtDate(d) {
  if (!d) return 'Unknown';
  const v = new Date(d);
  if (isNaN(v.getTime())) return 'Unknown';
  return new DateFormatter().string(v);
}
let data = null;
let offline = false;
try {
  const req = new Request(FEED_URL);
  req.timeoutInterval = 12;
  req.headers = {'Cache-Control':'no-cache'};
  data = await req.loadJSON();
  if (!data || !Array.isArray(data.headlines)) throw new Error('Invalid feed');
  fm.writeString(cache, JSON.stringify(data));
} catch (error) {
  offline = true;
  if (fm.fileExists(cache)) {
    try { data = JSON.parse(fm.readString(cache)); } catch (e) {}
  }
}
label('NEWS READER  •  DAILY INTELLIGENCE', 11, '#8CB8FF', true);
widget.addSpacer(7);
if (!data) {
  label('Feed not connected', 17, '#FFFFFF', true);
  widget.addSpacer(5);
  label('Set FEED_URL in the script, publish feed.json, then preview again.', 11, '#CFD8E5', false);
} else {
  const date = data.updated_at || null;
  const daysOld = date ? (Date.now() - new Date(date).getTime()) / 86400000 : Infinity;
  const freshness = (offline ? 'CACHED  •  ' : '') + (daysOld > 1.5 ? 'STALE FEED  •  ' : '') + (date ? 'Updated ' + date.slice(0,16).replace('T',' ') + ' UTC' : 'Undated');
  label(freshness, 9, daysOld > 1.5 ? '#FFB76A' : '#AFC0D5', false);
  widget.addSpacer(9);
  const large = config.widgetFamily === 'large';
  const items = data.headlines.slice(0, large ? 5 : 3);
  for (const item of items) {
    const category = (item.category || 'NEWS').toUpperCase();
    const status = (item.verification || 'Not yet verified');
    const verified = /^confirmed$/i.test(status);
    label(category + '  •  ' + (verified ? '✓ CONFIRMED' : '◦ ' + status.toUpperCase()), 9, verified ? '#8EE0B0' : '#FFCB88', true);
    label(item.title || 'Untitled story', 12, '#FFFFFF', true);
    widget.addSpacer(7);
  }
  widget.addSpacer();
  const trend = data.weekly_trend || {};
  label('WEEKLY TREND', 10, '#8CB8FF', true);
  label(trend.title || 'No verified trend published yet', 11, '#E0E7F0', false);
  if (large && trend.summary) {
    widget.addSpacer(3);
    label(trend.summary, 10, '#ADBED4', false);
  }
  if (data.report_url && /^https:\/\//.test(data.report_url)) widget.url = data.report_url;
}
widget.refreshAfterDate = new Date(Date.now() + REFRESH_MINUTES * 60000);
Script.setWidget(widget);
if (!config.runsInWidget) await widget.presentMedium();
Script.complete();
