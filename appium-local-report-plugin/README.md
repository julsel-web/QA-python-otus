# Appium Local Report Plugin

This local Appium plugin adds three custom endpoints:

- `GET /getReport`
- `DELETE /deleteReportData`
- `POST /setTestInfo`

Install locally:

```bash
appium plugin install --source=local /Users/uliatuz/PycharmProjects/QA-python-otus/appium-local-report-plugin
```

Run Appium with the plugin:

```bash
appium --use-plugins=local-report
```
