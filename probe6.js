const https = require('https');

function fetchUrl(url, opts) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: { 'User-Agent': 'Mozilla/5.0', ...((opts && opts.headers) || {}) },
      ...opts
    };
    https.get(url, options, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve({ status: res.statusCode, body: data, headers: res.headers }));
    }).on('error', reject);
  });
}

async function main() {
  // Try to call the flight search API with typical parameters
  // Based on what the site does: arrivals for today
  const today = new Date();
  const dateStr = `${today.getFullYear()}${String(today.getMonth()+1).padStart(2,'0')}${String(today.getDate()).padStart(2,'0')}`;

  // Try domestic arrivals
  const apiUrl = `https://tokyo-haneda.com/app/api/v2/flight/search?date=${dateStr}&type=arrival&flightType=domestic`;
  console.log('Trying URL:', apiUrl);

  const res = await fetchUrl(apiUrl, {
    headers: {
      'Referer': 'https://tokyo-haneda.com/flight/dms_search.html',
      'Accept': 'application/json'
    }
  });

  console.log('Status:', res.status);
  console.log('Content-Type:', res.headers['content-type']);
  console.log('Body (first 1000):', res.body.substring(0, 1000));
}

main().catch(console.error);
