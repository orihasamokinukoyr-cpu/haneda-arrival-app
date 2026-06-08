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

  // Find where result() is called with search - look for the actual fetch call
  const resultIdx = data.indexOf('result:function');
  if (resultIdx >= 0) {
    console.log('result function:', data.substring(resultIdx, resultIdx + 2000));
  }

  // Also look for 'get(' calls with the api path
  let pos = data.indexOf('flightData');
  while (pos >= 0) {
    const ctx = data.substring(pos, pos + 200);
    if (ctx.includes('.get(') || ctx.includes('axios')) {
      console.log('\nFlightData API call at', pos, ':', ctx);
    }
    pos = data.indexOf('flightData', pos + 1);
    if (pos > 200000) break;
  }
}

main().catch(console.error);
