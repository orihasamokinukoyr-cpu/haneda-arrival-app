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

  // Find ajaxParamSet
  const idx = data.indexOf('ajaxParamSet');
  if (idx >= 0) {
    console.log('ajaxParamSet context:', data.substring(idx, idx + 1500));
  }
}

main().catch(console.error);
