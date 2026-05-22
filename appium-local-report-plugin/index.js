'use strict';

const {BasePlugin} = require('appium/plugin');

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

class LocalReportPlugin extends BasePlugin {
  static reportEntries = [];

  static clearReport() {
    LocalReportPlugin.reportEntries = [];
  }

  static setTestInfo(payload) {
    const entry = {
      sessionId: payload.sessionId ?? 'unknown',
      testName: payload.testName ?? 'unknown',
      testStatus: payload.testStatus ?? 'unknown',
      updatedAt: new Date().toISOString(),
    };

    const existingIndex = LocalReportPlugin.reportEntries.findIndex(
      (item) => item.sessionId === entry.sessionId,
    );

    if (existingIndex >= 0) {
      LocalReportPlugin.reportEntries[existingIndex] = entry;
    } else {
      LocalReportPlugin.reportEntries.push(entry);
    }

    return entry;
  }

  static renderReport() {
    const rows = LocalReportPlugin.reportEntries.length
      ? LocalReportPlugin.reportEntries.map((entry) => `
          <tr>
            <td>${escapeHtml(entry.testName)}</td>
            <td>${escapeHtml(entry.testStatus)}</td>
            <td>${escapeHtml(entry.sessionId)}</td>
            <td>${escapeHtml(entry.updatedAt)}</td>
          </tr>
        `).join('')
      : `
          <tr>
            <td colspan="4">No test data collected yet.</td>
          </tr>
        `;

    return `
      <!doctype html>
      <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>Appium Local Report</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 24px;
            color: #202124;
          }
          h1 {
            margin-bottom: 16px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          th, td {
            border: 1px solid #dfe1e5;
            padding: 10px 12px;
            text-align: left;
          }
          th {
            background: #f8f9fa;
          }
          tr:nth-child(even) {
            background: #fbfbfb;
          }
        </style>
      </head>
      <body>
        <h1>Appium Local Report</h1>
        <table>
          <thead>
            <tr>
              <th>Test name</th>
              <th>Status</th>
              <th>Session ID</th>
              <th>Updated at</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </body>
      </html>
    `.trim();
  }

  static async updateServer(app) {
    app.delete('/deleteReportData', (req, res) => {
      LocalReportPlugin.clearReport();
      res.json({value: {cleared: true}});
    });

    app.post('/setTestInfo', (req, res) => {
      const entry = LocalReportPlugin.setTestInfo(req.body ?? {});
      res.json({value: entry});
    });

    app.get('/getReport', (req, res) => {
      res.json({value: LocalReportPlugin.renderReport()});
    });
  }
}

module.exports = {
  LocalReportPlugin,
};
