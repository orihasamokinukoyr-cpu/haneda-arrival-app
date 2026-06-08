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

  // Find context around the search API call
  const idx = data.indexOf('/app/api/v2/flight/search');
  if (idx >= 0) {
    console.log('Context around API call:');
    console.log(data.substring(Math.max(0, idx - 500), idx + 500));
  }

  // Also look for params object
  const paramIdx = data.indexOf('params');
  if (paramIdx >= 0) {
    console.log('\nParams context:');
    console.log(data.substring(Math.max(0, paramIdx - 100), paramIdx + 300));
  }
}

main().catch(console.error);
