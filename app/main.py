import time
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from app.apiChecks import run_checks_once, LATEST
from app.auth import require_basic_auth

app = FastAPI(title="API Monitor POC")

CHECK_INTERVAL_SECONDS = 120
_last_run = 0.0


@app.on_event("startup")
async def startup():
    await run_checks_once()


@app.get("/api/status")
async def api_status() -> JSONResponse:
    global _last_run
    now = time.time()
    if now - _last_run >= CHECK_INTERVAL_SECONDS:
        await run_checks_once()
        _last_run = now
    return JSONResponse({"results": list(LATEST.values())})


@app.get("/", response_class=HTMLResponse)
async def home(user: str = Depends(require_basic_auth)) -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>API Monitor POC</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 16px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }
    th { position: sticky; top: 0; background: #f7f7f7; }
    .ok { font-weight: 600; }
    .bad { font-weight: 600; }
    .muted { color: #666; font-size: 0.9em; }
  </style>
</head>
<body>
  <h2>API Monitor POC</h2>
  <div class="muted">Tests endpoints every 120 seconds</div>
  <p><button onclick="loadData()">Refresh now</button></p>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Name</th>
        <th>HTTP</th>
        <th>Latency (ms)</th>
        <th>Body</th>
        <th>Checked</th>
        <th>Reason</th>
      </tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>

<script>
async function loadData() {
  const r = await fetch('/api/status');
  const j = await r.json();
  const rows = document.getElementById('rows');
  rows.innerHTML = '';

  for (const item of j.results) {
    const statusIcon = item.ok ? '✅' : '❌';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="${item.ok ? 'ok' : 'bad'}">${statusIcon}</td>
      <td>
        <div>${item.name}</div>
        <div class="muted"
             title="${item.request?.url ?? ''}"
             style="cursor: help; word-break: break-all;">
          ${item.url}
        </div>
      </td>
      <td>
        ${item.status_code ?? ''}
        ${(item.status_code >= 400 && item.error_message) ? `<div class="muted" style="font-size:0.9em;white-space:pre-wrap;">${item.error_message}</div>` : ''}
      </td>
      <td>${item.latency_ms ?? ''}</td>
      <td>
        ${item.body_len ?? ''}
        <div>
          ${
            (() => {
              try {
                const data = JSON.parse(item.response_body || "[]");
                if (!Array.isArray(data) || !data.length) return "";
                return data.map((outer, i) => `
                  <details>
                    <summary>Result List (${outer.result?.length ?? 0} items)</summary>
                    ${
                      Array.isArray(outer.result)
                        ? outer.result.map((obj, idx) => `
                          <details>
                            <summary>${obj.eventName || "Item " + (idx + 1)}</summary>
                            <pre style="white-space: pre-wrap; max-width: 400px;">${JSON.stringify(obj, null, 2)}</pre>
                          </details>
                        `).join("")
                        : ""
                    }
                  </details>
                `).join("");
              } catch (e) {
                return "";
              }
            })()
          }
        </div>
      </td>
      <td>${item.ts ?? ''}</td>
      <td>${item.reason ?? ''}</td>
    `;
    rows.appendChild(tr);
  }
}

loadData();
setInterval(loadData, 120000);
</script>
</body>
</html>
"""
