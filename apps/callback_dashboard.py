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
        --bg: #121827;
        --panel: rgba(24, 35, 52, 0.94);
        --panel-soft: rgba(17, 24, 39, 0.84);
        --text: #edf2f7;
        --muted: #a5b4c7;
        --border: #314057;
        --ok: #57c084;
        --bad: #f06a6a;
        --warn: #d9a441;
      }
      body {
        margin: 0;
        background:
          radial-gradient(circle at top left, rgba(71, 110, 167, 0.18), transparent 34%),
          linear-gradient(160deg, #1b2739 0%, var(--bg) 58%);
        color: var(--text);
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
      }
      .card {
        margin: 16px;
        padding: 22px;
        border: 1px solid var(--border);
        border-radius: 20px;
        background: var(--panel);
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
        border-bottom: 1px solid var(--border);
        padding-bottom: 14px;
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
        padding: 16px;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: var(--panel-soft);
      }
      .section h3 {
        margin: 0 0 10px;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
      }
      .event {
        padding: 12px 0;
        border-top: 1px solid rgba(49, 64, 87, 0.7);
      }
      .event:first-child {
        border-top: 0;
        padding-top: 0;
      }
      .event-id {
        color: var(--bad);
        font-weight: 700;
      }
      .subtle {
        color: var(--muted);
      }
      .bad { color: var(--bad); }
      .ok { color: var(--ok); }
      .breaker {
        margin-top: 16px;
        padding: 14px 16px;
        border-radius: 16px;
        border: 1px solid var(--border);
        background: rgba(17, 24, 39, 0.78);
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
      }
      .status-pill {
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .status-pill.ok {
        color: var(--ok);
        background: rgba(87, 192, 132, 0.12);
      }
      .status-pill.bad {
        color: var(--bad);
        background: rgba(240, 106, 106, 0.12);
      }
      .status-pill.warn {
        color: var(--warn);
        background: rgba(217, 164, 65, 0.12);
      }
      .strategy-lines,
      .security-copy {
        color: var(--muted);
      }
      .strategy-lines div + div,
      .security-copy div + div {
        margin-top: 6px;
      }
      .empty-copy {
        color: var(--muted);
      }
      @media (max-width: 720px) {
        .stats {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
      @media (max-width: 520px) {
        .stats {
          grid-template-columns: minmax(0, 1fr);
        }
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
      const responseCodeLabels = {
        408: \"Request Timeout\",
        429: \"Too Many Requests\",
        502: \"Bad Gateway\",
        503: \"Service Unavailable\",
      };

      const escapeHtml = (value) => String(value)
        .replaceAll(\"&\", \"&amp;\")
        .replaceAll(\"<\", \"&lt;\")
        .replaceAll(\">\", \"&gt;\")
        .replaceAll('\\"', \"&quot;\")
        .replaceAll(\"'\", \"&#39;\");

      const formatDateTime = (value) => {
        if (!value) {
          return \"n/a\";
        }
        return String(value).replace(\"T\", \" \" ).slice(0, 16);
      };

      const formatResponse = (code) => {
        if (!code) {
          return \"n/a\";
        }
        const label = responseCodeLabels[code];
        return label ? `${code} ${label}` : String(code);
      };

      const statusTone = (state) => {
        if (state === \"OPEN\") {
          return \"bad\";
        }
        return \"ok\";
      };

      const renderError = (data) => {
        appRoot.innerHTML = `
          <p class=\"title\">callback health dashboard</p>
          <p class=\"meta\">Unable to render callbacks</p>
          <div class=\"section\">
            <h3>error</h3>
            <div class=\"empty-copy\">${escapeHtml(data?.error || \"Unknown error\")}</div>
          </div>
        `;
      };

      const render = (data) => {
        if (data?.status === \"error\") {
          renderError(data);
          return;
        }

        const health = data.callback_health || {};
        const events = data.events || [];
        const breakerTone = statusTone(health.circuit_breaker);
        const breakerCopy = health.circuit_breaker === \"OPEN\" ? \"degraded\" : \"healthy\";
        const retryStrategy = data.retry_strategy || {};

        appRoot.innerHTML = `
          <p class=\"title\">callback health dashboard</p>
          <p class=\"meta\">Account: ${escapeHtml(data.card_account_id)}</p>

          <div class=\"stats\">
            <div class=\"stat\"><div class=\"value\">${escapeHtml(health.total_events ?? 0)}</div><div class=\"label\">total</div></div>
            <div class=\"stat\"><div class=\"value ok\">${escapeHtml(health.success_count ?? 0)}</div><div class=\"label\">sent</div></div>
            <div class=\"stat\"><div class=\"value bad\">${escapeHtml(health.failure_count ?? 0)}</div><div class=\"label\">failed</div></div>
            <div class=\"stat\"><div class=\"value\">${escapeHtml(health.success_rate ?? \"0%\")}</div><div class=\"label\">success rate</div></div>
          </div>

          <div class=\"breaker\">
            <span class=\"subtle\">Circuit breaker:</span>
            <span class=\"status-pill ${breakerTone}\">${escapeHtml(health.circuit_breaker || \"UNKNOWN\")}</span>
            <span class=\"subtle\">${escapeHtml(breakerCopy)}</span>
          </div>

          <div class=\"section\">
            <h3>failed events</h3>
            ${events.length ? events.map((event) => `
              <div class=\"event\">
                <div><span class=\"event-id\">${escapeHtml(event.id)}</span> &middot; ${escapeHtml(event.event_type)}</div>
                <div>${escapeHtml(formatDateTime(event.created_at))} &middot; ${escapeHtml(formatResponse(event.http_response_code))}</div>
                <div class=\"subtle\">Attempts: ${escapeHtml(event.attempt_count)} / ${escapeHtml(event.max_retries)} &middot; Endpoint: ${escapeHtml(event.endpoint_url)}</div>
                ${event.failure_reason ? `<div class=\"subtle\">${escapeHtml(event.failure_reason)}</div>` : \"\"}
              </div>
            `).join(\"\") : '<div class="empty-copy">No failed events in the selected view.</div>'}
          </div>

          <div class=\"section\">
            <h3>retry strategy</h3>
            <div class=\"strategy-lines\">
              <div>4xx: ${escapeHtml(retryStrategy[\"4xx_errors\"] || \"n/a\")}</div>
              <div>Other: ${escapeHtml(retryStrategy[\"other_errors\"] || \"n/a\")}</div>
              <div>Circuit breaker: ${escapeHtml(retryStrategy.circuit_breaker || \"n/a\")}</div>
            </div>
          </div>

          <div class=\"section\">
            <h3>security</h3>
            <div class=\"security-copy\">${escapeHtml(data.security_note || \"\")}</div>
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
