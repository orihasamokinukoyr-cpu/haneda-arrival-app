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

  // Search for URL patterns / API calls
  const urlMatches = data.match(/["'](\/[^"']*(?:api|flight|json|search)[^"']*)['"]/g);
  if (urlMatches) {
    console.log('URL patterns:', [...new Set(urlMatches)].join('\n'));
  }

  // Search for axios calls or fetch with URLs
  const axiosMatches = data.match(/axios\.[a-z]+\(['"][^'"]+['"]/g);
  if (axiosMatches) {
    console.log('\nAxios calls:', axiosMatches.join('\n'));
  }

  // Find any URL-like strings
  const allUrls = data.match(/["'][^"']*\/flight[^"']*["']/g);
  if (allUrls) {
    console.log('\nFlight URLs:', [...new Set(allUrls)].join('\n'));
  }
}

main().catch(console.error);
