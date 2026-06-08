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

  // Find flightData module - look for the module definition
  // The module is called as (0,o.flightData)(this) - find o.flightData definition
  let pos = 0;
  const results = [];
  while ((pos = data.indexOf('M.flightData', pos)) >= 0) {
    results.push(data.substring(pos, pos + 2000));
    pos += 10;
  }
  console.log('Found', results.length, 'flightData definitions');
  results.forEach((r, i) => console.log(`\n[${i}]:`, r.substring(0, 500)));
}

main().catch(console.error);
