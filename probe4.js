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
  // Check _flightData.js for API call details
  const data = await fetchUrl('https://tokyo-haneda.com/site_resource/flight/js/flightSearch_v2/_flightData.js?202605131439');
  console.log(data.substring(0, 5000));
}

main().catch(console.error);
