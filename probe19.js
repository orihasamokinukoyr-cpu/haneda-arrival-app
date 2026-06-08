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

  // Find ajaxParamStatusSet
  const idx = data.indexOf('ajaxParamStatusSet');
  if (idx >= 0) {
    console.log('StatusSet context:', data.substring(idx, idx + 500));
  }

  // Also look for status values
  const idx2 = data.indexOf('"all"');
  if (idx2 >= 0) {
    console.log('\n"all" context:', data.substring(Math.max(0, idx2-200), idx2 + 300));
  }
}

main().catch(console.error);
