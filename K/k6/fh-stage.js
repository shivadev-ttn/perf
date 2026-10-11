import { textSummary } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/latest/dist/bundle.js';
import { runAllApis } from './lib/apis.js';
import { THRESHOLDS_MS } from './lib/config.js';

const vus = Number(__ENV.VUS || 1);
const rampTime = __ENV.RAMP_TIME || '1s';
const duration = __ENV.DURATION || '60s';
const reportTitle = __ENV.REPORT_TITLE || `FH Stage API - ${vus} User(s)`;

export const options = {
  scenarios: {
    fh_stage_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: rampTime, target: vus },
        { duration: duration, target: vus },
      ],
      gracefulRampDown: '5s',
    },
  },
  thresholds: {
    checks: ['rate>0.99'],
    http_req_failed: ['rate<0.01'],
    'http_req_duration{name:Offers Hotel List}': [`p(95)<${THRESHOLDS_MS.offersHotelList}`],
    'http_req_duration{name:Offers List}': [`p(95)<${THRESHOLDS_MS.lightApi}`],
    'http_req_duration{name:Locations Property Listing}': [`p(95)<${THRESHOLDS_MS.lightApi}`],
  },
  tags: {
    test: reportTitle,
  },
};

export default function () {
  runAllApis();
}

export function handleSummary(data) {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const fileName = __ENV.RESULT_FILE || `results/summary-${vus}user-${stamp}.json`;
  const htmlFile = __ENV.HTML_REPORT || 'results/latest-report.html';

  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
    [fileName]: JSON.stringify(data, null, 2),
    'results/latest-summary.json': JSON.stringify(data, null, 2),
    [htmlFile]: htmlReport(data, { title: reportTitle }),
  };
}
