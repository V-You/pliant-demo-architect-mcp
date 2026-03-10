from __future__ import annotations


def render_controls_card_html() -> str:
    return """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>card controls inspector</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #121824;
        --panel: #1b2433;
        --text: #edf2f7;
        --muted: #9fb0c6;
        --border: #2a3649;
        --ok: #57c084;
        --bad: #f06a6a;
        --warn: #d9a441;
      }
      body {
        margin: 0;
        background: radial-gradient(circle at top, #202d42 0%, var(--bg) 55%);
        color: var(--text);
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
      }
      .card {
        margin: 16px;
        padding: 20px;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(27, 36, 51, 0.94);
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
      .section {
        margin-top: 16px;
        padding: 14px;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: rgba(18, 24, 36, 0.75);
      }
      .section h3 {
        margin: 0 0 10px;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
      }
      .row {
        display: flex;
        justify-content: space-between;
        gap: 12px;
      }
      .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .chip {
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: #223047;
      }
      .ok { color: var(--ok); }
      .bad { color: var(--bad); }
      .scenario {
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-style: italic;
      }
      pre {
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
      }
    </style>
  </head>
  <body>
    <div class=\"card\" id=\"app\">
      <p class=\"title\">card controls inspector</p>
      <p class=\"meta\">waiting for tool result</p>
    </div>
    <script type=\"module\">
      import { App } from \"https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps\";

      const appRoot = document.getElementById(\"app\");
      const app = new App({ name: \"controls card\", version: \"0.1.0\" });

      const escapeHtml = (value) => String(value)
        .replaceAll(\"&\", \"&amp;\")
        .replaceAll(\"<\", \"&lt;\")
        .replaceAll(\">\", \"&gt;\")
        .replaceAll('\\"', \"&quot;\")
        .replaceAll(\"'\", \"&#39;\");

      const chipList = (values = []) => {
        if (!values.length) {
          return \"<span class='chip'>none</span>\";
        }
        return values.map((value) => `<span class=\"chip\">${escapeHtml(value)}</span>`).join(\"\");
      };

      const render = (data) => {
        const controls = data.controls || {};
        const categoryControls = controls.category_controls;
        const timeControls = controls.time_controls || [];
        const amountControls = controls.amount_controls || {};
        const merchantControls = controls.merchant_controls;

        appRoot.innerHTML = `
          <p class=\"title\">card controls inspector</p>
          <p class=\"meta\">card: ${escapeHtml(data.card_token)} · ${escapeHtml(data.cardholder?.name || \"unknown\")} · ${escapeHtml(data.cardholder?.team || \"no team\")}</p>

          <div class=\"section\">
            <div class=\"row\"><h3>category controls</h3><strong class=\"ok\">${escapeHtml(categoryControls?.restriction || \"none\")}</strong></div>
            <div class=\"chips\">${chipList(categoryControls?.values || [])}</div>
          </div>

          <div class=\"section\">
            <h3>time controls</h3>
            <pre>${escapeHtml(JSON.stringify(timeControls, null, 2))}</pre>
          </div>

          <div class=\"section\">
            <h3>amount controls</h3>
            <pre>${escapeHtml(JSON.stringify(amountControls, null, 2))}</pre>
          </div>

          <div class=\"section\">
            <h3>merchant controls</h3>
            <pre>${escapeHtml(JSON.stringify(merchantControls, null, 2))}</pre>
          </div>

          <div class=\"scenario\">${escapeHtml(data.scenario || \"no scenario provided\")}</div>
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
