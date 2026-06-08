const https = require('https');

function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function main() {
  const data = await fetchUrl('https://tokyo-haneda.com/site_resource/flight/js/flightSearch_v2.js?202605131439');

  // Find _flightData module function
  const idx = data.indexOf('flightData:function');
  if (idx >= 0) {
    console.log('flightData module:', data.substring(idx, idx + 1000));
  }

  // Also search for .get( with ajaxParams
  const ajaxIdx = data.indexOf('ajaxParams');
  let pos = ajaxIdx;
  while ((pos = data.indexOf('.get(', pos)) >= 0) {
    console.log('\n.get( at', pos, ':', data.substring(Math.max(0, pos-100), pos + 300));
    pos += 5;
    if (pos > ajaxIdx + 10000) break;
  }
}

main().catch(console.error);
