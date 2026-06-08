const https = require('https');

function postJson(url, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = JSON.stringify(body);
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyStr),
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://tokyo-haneda.com/flight/int_search.html',
        'Origin': 'https://tokyo-haneda.com',
        'Accept': 'application/json',
      }
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(bodyStr);
    req.end();
  });
}

async function main() {
  const today = new Date();
  const dateStr = `${today.getFullYear()}${String(today.getMonth()+1).padStart(2,'0')}${String(today.getDate()).padStart(2,'0')}`;

  const res = await postJson('https://tokyo-haneda.com/app/api/v2/flight/search', {
    flightType: 2,
    arrivalType: 2,
    searchDt: dateStr,
    airportCodes: [],
    airlineCodes: [],
    flightNumber: "",
    status: [0]
  });

  const json = JSON.parse(res.body);
  // Find T2 international flights
  const t2 = json.flightlists.filter(f => f.terminal && f.terminal.terminal === 'T2');
  console.log('T2 international count:', t2.length);
  console.log(JSON.stringify(t2.slice(0, 3), null, 2));
}

main().catch(console.error);
