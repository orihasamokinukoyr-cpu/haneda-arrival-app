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

  // Find FlightType set function
  const idx = data.indexOf('ajaxParamFlightTypeSet');
  if (idx >= 0) {
    console.log('FlightTypeSet context:', data.substring(idx, idx + 500));
  }

  // Find appType set function
  const idx2 = data.indexOf('appTypeSet');
  if (idx2 >= 0) {
    console.log('\nappTypeSet context:', data.substring(idx2, idx2 + 500));
  }

  // Look for dms/int keywords
  const idx3 = data.indexOf('"dms"');
  if (idx3 >= 0) {
    console.log('\ndms context:', data.substring(Math.max(0, idx3-200), idx3 + 300));
  }
}

main().catch(console.error);
