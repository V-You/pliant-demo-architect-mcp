from __future__ import annotations


def render_callback_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>callback health dashboard</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #111827;
        --panel: #182334;
        --text: #edf2f7;
        --muted: #a5b4c7;
        --border: #2a3649;
        --ok: #57c084;
        --bad: #f06a6a;
        --warn: #d9a441;
      }
      body {
        margin: 0;
        background: linear-gradient(160deg, #20314a 0%, var(--bg) 58%);
        color: var(--text);
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
      }
      .card {
        margin: 16px;
        padding: 20px;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(24, 35, 52, 0.94);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
      }
      .title {
        margin: 0 0 6px;
        font-size: 12px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
      }
      .meta {
        margin: 0 0 18px;
        color: var(--muted);
      }
      .stats {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
      }
      .stat {
        padding: 12px;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: rgba(17, 24, 39, 0.78);
      }
      .value {
        font-size: 20px;
        font-weight: 700;
      }
      .label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 11px;
      }
      .section {
        margin-top: 16px;
        padding: 14px;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: rgba(17, 24, 39, 0.78);
      }
      .section h3 {
        margin: 0 0 10px;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
      }
      .event {
        padding: 10px 0;
        border-top: 1px solid var(--border);
      }
      .event:first-child {
        border-top: 0;
        padding-top: 0;
      }
      .bad { color: var(--bad); }
      .ok { color: var(--ok); }
      pre {
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
      }
    </style>
  </head>
  <body>
    <div class=\"card\" id=\"app\">
      <p class=\"title\">callback health dashboard</p>
      <p class=\"meta\">waiting for tool result</p>
    </div>
    <script type=\"module\">
      import { App } from \"https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps\";

      const appRoot = document.getElementById(\"app\");
      const app = new App({ name: \"callback dashboard\", version: \"0.1.0\" });

      const escapeHtml = (value) => String(value)
        .replaceAll(\"&\", \"&amp;\")
        .replaceAll(\"<\", \"&lt;\")
        .replaceAll(\">\", \"&gt;\")
        .replaceAll('\\"', \"&quot;\")
        .replaceAll(\"'\", \"&#39;\");

      const render = (data) => {
        const health = data.callback_health || {};
        const events = data.events || [];

        appRoot.innerHTML = `
          <p class=\"title\">callback health dashboard</p>
          <p class=\"meta\">account: ${escapeHtml(data.card_account_id)}</p>

          <div class=\"stats\">
            <div class=\"stat\"><div class=\"value\">${escapeHtml(health.total_events ?? 0)}</div><div class=\"label\">total</div></div>
            <div class=\"stat\"><div class=\"value ok\">${escapeHtml(health.success_count ?? 0)}</div><div class=\"label\">sent</div></div>
            <div class=\"stat\"><div class=\"value bad\">${escapeHtml(health.failure_count ?? 0)}</div><div class=\"label\">failed</div></div>
            <div class=\"stat\"><div class=\"value\">${escapeHtml(health.success_rate ?? \"0%\")}</div><div class=\"label\">success rate</div></div>
          </div>

          <div class=\"section\">
            <h3>failed events</h3>
            ${events.length ? events.map((event) => `
              <div class=\"event\">
                <div><strong class=\"bad\">${escapeHtml(event.id)}</strong> · ${escapeHtml(event.event_type)}</div>
                <div>${escapeHtml(event.created_at)} · ${escapeHtml(event.http_response_code ?? \"n/a\")}</div>
                <div>attempts: ${escapeHtml(event.attempt_count)} / ${escapeHtml(event.max_retries)}</div>
              </div>
            `).join(\"\") : \"<div>no events</div>\"}
          </div>

          <div class=\"section\">
            <h3>retry strategy</h3>
            <pre>${escapeHtml(JSON.stringify(data.retry_strategy, null, 2))}</pre>
          </div>

          <div class=\"section\">
            <h3>security</h3>
            <div>${escapeHtml(data.security_note || \"\")}</div>
          </div>
        `;
      };

      app.ontoolresult = ({ content }) => {
        const text = content?.find((item) => item.type === \"text\");
        if (!text) {
          return;
        }
        try {
          render(JSON.parse(text.text));
        } catch (error) {
          appRoot.innerHTML = `<pre>${escapeHtml(text.text)}</pre>`;
        }
      };

      await app.connect();
    </script>
  </body>
</html>
"""
