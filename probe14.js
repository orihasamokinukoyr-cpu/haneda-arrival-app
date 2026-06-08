const https = require('https');

function postJson(url, body, referer) {
  return new Promise((resolve, reject) => {
    const bodyStr = JSON.stringify(body);
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyStr),
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Referer': referer || 'https://tokyo-haneda.com/flight/dms_search.html',
        'Origin': 'https://tokyo-haneda.com',
        'Accept': 'application/json',
      }
    };
    const urlObj = new URL(url);
    options.hostname = urlObj.hostname;
    options.path = urlObj.pathname + urlObj.search;

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

  // Try domestic arrivals - flightType=1 for domestic, arrivalType=1 for arrival?
  // Based on ajaxParams: flightType:0, arrivalType:0
  // flightType 0=domestic?, 1=international?
  // Let's try different combinations

  const params = {
    flightType: 0,   // Try 0 for domestic
    arrivalType: 1,  // 1 for arrival?
    searchDt: dateStr,
    airportCodes: [],
    airlineCodes: [],
    flightNumber: "",
    status: [""]
  };

  console.log('Trying params:', params);
  const res = await postJson('https://tokyo-haneda.com/app/api/v2/flight/search', params);
  console.log('Status:', res.status);
  console.log('Body (first 1000):', res.body.substring(0, 1000));
}

main().catch(console.error);
