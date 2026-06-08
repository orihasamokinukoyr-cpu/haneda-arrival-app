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

  // Find where axios is called with the search URL
  let pos = 0;
  let count = 0;
  while ((pos = data.indexOf('axios', pos)) >= 0 && count < 10) {
    console.log(`\naxios at ${pos}:`, data.substring(Math.max(0, pos), pos + 400));
    pos += 5;
    count++;
  }
}

main().catch(console.error);
