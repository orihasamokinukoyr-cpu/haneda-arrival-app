const https = require('https');

function postJson(url, body, referer) {
  return new Promise((resolve, reject) => {
    const bodyStr = JSON.stringify(body);
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyStr),
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': referer || 'https://tokyo-haneda.com/flight/dms_search.html',
        'Origin': 'https://tokyo-haneda.com',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja',
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: data }));
    });
    req.on('error', reject);
    req.write(bodyStr);
    req.end();
  });
}

async function main() {
  const today = new Date();
  const dateStr = `${today.getFullYear()}${String(today.getMonth()+1).padStart(2,'0')}${String(today.getDate()).padStart(2,'0')}`;

  // status should be ["all"] not [""]
  const params = {
    flightType: 1,
    arrivalType: 2,
    searchDt: dateStr,
    airportCodes: [],
    airlineCodes: [],
    flightNumber: "",
    status: ["all"]
  };

  console.log('Trying domestic arrivals with status=all:', params);
  const res = await postJson('https://tokyo-haneda.com/app/api/v2/flight/search', params);
  console.log('Status:', res.status);
  console.log('Body (first 3000):', res.body.substring(0, 3000));
}

main().catch(console.error);
