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

  // Find auth/token related code
  const idx = data.indexOf('MemberId');
  console.log('MemberId context:', data.substring(Math.max(0, idx - 200), idx + 500));

  // Find axios call with headers
  const axiosIdx = data.indexOf('axios.get');
  if (axiosIdx >= 0) {
    console.log('\nAxios.get context:', data.substring(Math.max(0, axiosIdx - 100), axiosIdx + 500));
  }

  // Find all occurrences of 'header'
  let pos = 0;
  let count = 0;
  while ((pos = data.indexOf('header', pos)) >= 0 && count < 5) {
    console.log(`\nheader at ${pos}:`, data.substring(Math.max(0, pos - 50), pos + 200));
    pos += 1;
    count++;
  }
}

main().catch(console.error);
