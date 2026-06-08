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
  const data = await fetchUrl('https://tokyo-haneda.com/flight/dms_search.html');

  // Find script tags
  const re = /src="([^"]+\.js[^"]*)"/g;
  let m;
  while ((m = re.exec(data)) !== null) {
    console.log(m[1]);
  }

  // Look for API hints
  const apiHints = data.match(/api[^"'\s<>]*/gi);
  if (apiHints) console.log('\nAPI hints:', [...new Set(apiHints)].slice(0, 20));
}

main().catch(console.error);
