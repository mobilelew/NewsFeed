// Scriptable: News Reader Home Screen widget. iOS controls actual refresh times.
const FEED_URL = 'https://mobilelew.github.io/NewsFeed/feed.json';
const REFRESH_MINUTES = 45;
const fm = FileManager.local();
const cache = fm.joinPath(fm.documentsDirectory(), 'NewsReader-feed-cache.json');
const widget = new ListWidget();
widget.backgroundColor = new Color('#101827');
widget.setPadding(13, 14, 12, 14);
function label(value, size, color, strong, limit) {
  const t = widget.addText(String(value || ''));
  t.font = strong ? Font.boldSystemFont(size) : Font.systemFont(size);
  t.textColor = new Color(color);
  t.lineLimit = limit || 2;
  return t;
}
let feed = null, offline = false;
try {
  const request = new Request(FEED_URL);
  request.timeoutInterval = 12;
  request.headers = {'Cache-Control': 'no-cache'};
  feed = await request.loadJSON();
  if (!feed || !Array.isArray(feed.headlines)) throw new Error('Invalid JSON feed');
  fm.writeString(cache, JSON.stringify(feed));
} catch (e) {
  offline = true;
  if (fm.fileExists(cache)) { try { feed = JSON.parse(fm.readString(cache)); } catch (ignored) {} }
}
label('NEWS READER · DAILY INTELLIGENCE', 10, '#9EC5FF', true, 1);
widget.addSpacer(5);
if (!feed) {
  label('Feed unavailable', 16, '#FFFFFF', true);
  label('Check the GitHub Pages feed URL.', 11, '#ADBED4', false);
} else {
  const updated = Date.parse(feed.updated_at || '');
  const stale = !Number.isFinite(updated) || (Date.now() - updated) > 36*60*60*1000;
  label((offline ? 'CACHED · ' : '') + (stale ? 'STALE · ' : '') +
        (Number.isFinite(updated) ? 'Updated ' + new Date(updated).toLocaleString() : 'Update unknown'),
        9, stale ? '#FFB76A' : '#AFC0D5', false, 1);
  widget.addSpacer(8);
  const large = config.widgetFamily === 'large';
  const small = config.widgetFamily === 'small';
  const items = feed.headlines.slice(0, large ? 5 : small ? 1 : 3);
  if (!items.length) label('No recent relevant headlines.', 13, '#CFD8E5', true);
  for (const item of items) {
    const status = item.verification || 'Not yet verified';
    const reviewed = item.is_editorial === true && status !== 'Not yet verified';
    const color = reviewed && status === 'Confirmed' ? '#9CE3BB' : '#F9CB8A';
    label((item.category || 'NEWS') + ' · ' + (reviewed ? status : 'Unverified'), 9, color, true, 1);
    label(item.title || 'Untitled', 11, '#F4F7FB', true, 2);
    if (large && item.source_differences) label('Source differences: ' + item.source_differences, 9, '#BACADD', false, 2);
    widget.addSpacer(7);
  }
  if (!small) {
    widget.addSpacer();
    label('WEEKLY TRENDS', 10, '#9EC5FF', true, 1);
    label((feed.weekly_trend || {}).title || 'No published trend yet', 11, '#F4F7FB', false, 2);
    if (large && feed.weekly_trend && feed.weekly_trend.summary) {
      label(feed.weekly_trend.summary, 9, '#ADBED4', false, 2);
    }
  }
  widget.url = /^https:\/\//.test(feed.report_url || '') ? feed.report_url : FEED_URL;
}
widget.refreshAfterDate = new Date(Date.now() + REFRESH_MINUTES*60000);
Script.setWidget(widget);
if (!config.runsInWidget) await widget.presentMedium();
Script.complete();
