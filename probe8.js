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

  // Search for how the API is actually called - look for axios.get with the search endpoint
  const searchIdx = data.indexOf('flight/search');
  let pos = searchIdx;
  // Find the larger context - look back for function definition
  const context = data.substring(Math.max(0, pos - 2000), pos + 1000);
  console.log(context);
}

main().catch(console.error);
