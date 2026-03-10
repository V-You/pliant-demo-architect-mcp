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
        --bg: #151c29;
        --panel: rgba(27, 36, 51, 0.94);
        --panel-soft: rgba(17, 24, 39, 0.82);
        --text: #edf2f7;
        --muted: #9db0c8;
        --border: #314057;
        --ok: #57c084;
        --bad: #f06a6a;
        --warn: #d9a441;
        --shadow: rgba(0, 0, 0, 0.36);
      }
      body {
        margin: 0;
        background:
          radial-gradient(circle at top left, rgba(72, 114, 168, 0.18), transparent 32%),
          radial-gradient(circle at top right, rgba(65, 120, 96, 0.12), transparent 28%),
          linear-gradient(180deg, #1a2332 0%, var(--bg) 58%);
        color: var(--text);
        font: 14px/1.5 -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
      }
      .card {
        margin: 16px;
        padding: 22px;
        border: 1px solid var(--border);
        border-radius: 20px;
        background: var(--panel);
        box-shadow: 0 22px 50px var(--shadow);
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
      .row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
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
      .status-pill.allowed {
        color: var(--ok);
        background: rgba(87, 192, 132, 0.12);
      }
      .status-pill.blocked {
        color: var(--bad);
        background: rgba(240, 106, 106, 0.12);
      }
      .rule-list {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .rule-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 0;
        border-top: 1px solid rgba(49, 64, 87, 0.7);
      }
      .rule-item:first-child {
        border-top: 0;
        padding-top: 0;
      }
      .mark {
        width: 18px;
        flex: 0 0 18px;
        text-align: center;
        font-weight: 700;
      }
      .mark.ok::before {
        content: "\\2713";
        color: var(--ok);
      }
      .mark.bad::before {
        content: "\\00d7";
        color: var(--bad);
      }
      .empty-copy {
        color: var(--muted);
      }
      .detail-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        gap: 8px;
      }
      .detail-row {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        padding: 6px 0;
        border-top: 1px solid rgba(49, 64, 87, 0.7);
      }
      .detail-row:first-child {
        border-top: 0;
        padding-top: 0;
      }
      .detail-label {
        color: var(--muted);
      }
      .detail-value {
        text-align: right;
      }
      .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .tag {
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(34, 48, 71, 0.8);
        color: var(--text);
      }
      .scenario {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-style: italic;
      }
      .summary {
        margin-top: 14px;
        padding: 12px 14px;
        border-radius: 14px;
        background: rgba(13, 19, 29, 0.55);
        color: var(--muted);
      }
      @media (max-width: 640px) {
        .card {
          margin: 12px;
          padding: 16px;
        }
        .detail-row,
        .row {
          flex-direction: column;
          align-items: flex-start;
        }
        .detail-value {
          text-align: left;
        }
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
      const dayLabels = {
        MONDAY: \"Mon\",
        TUESDAY: \"Tue\",
        WEDNESDAY: \"Wed\",
        THURSDAY: \"Thu\",
        FRIDAY: \"Fri\",
        SATURDAY: \"Sat\",
        SUNDAY: \"Sun\",
      };

      const escapeHtml = (value) => String(value)
        .replaceAll(\"&\", \"&amp;\")
        .replaceAll(\"<\", \"&lt;\")
        .replaceAll(\">\", \"&gt;\")
        .replaceAll('\\"', \"&quot;\")
        .replaceAll(\"'\", \"&#39;\");

      const titleizeEnum = (value) => String(value || \"\")
        .toLowerCase()
        .split(\"_\")
        .map((part) => part ? part[0].toUpperCase() + part.slice(1) : \"\")
        .join(\" \");

      const formatAmount = (amount) => {
        if (!amount) {
          return \"none\";
        }
        const value = Number(amount.value || 0) / 100;
        return `${escapeHtml(amount.currency)} ${value.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`;
      };

      const friendlyCategory = (category, labels) => {
        return labels?.[category] || titleizeEnum(category);
      };

      const formatDays = (days = []) => {
        const joined = days.join(\",\");
        if (joined === \"MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY\") {
          return \"Mon-Fri\";
        }
        if (joined === \"MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,SUNDAY\") {
          return \"Daily\";
        }
        return days.map((day) => dayLabels[day] || titleizeEnum(day)).join(\", \" );
      };

      const renderCategoryControls = (categoryControls, categoryLabels) => {
        if (!categoryControls) {
          return '<div class="empty-copy">No category restrictions</div>';
        }

        const allCategories = Object.keys(categoryLabels || {});
        const selected = categoryControls.values || [];
        const items = [];

        if (categoryControls.restriction === \"ALLOWED\") {
          selected.forEach((category) => {
            items.push(`
              <li class=\"rule-item\">
                <span class=\"mark ok\"></span>
                <span>${escapeHtml(friendlyCategory(category, categoryLabels))}</span>
              </li>
            `);
          });

          const remaining = allCategories.filter((category) => !selected.includes(category));
          if (remaining.length) {
            const lead = friendlyCategory(remaining[0], categoryLabels);
            const tailCount = remaining.length - 1;
            const tail = tailCount > 0 ? ` (${tailCount} more blocked)` : \"\";
            items.push(`
              <li class=\"rule-item\">
                <span class=\"mark bad\"></span>
                <span>${escapeHtml(lead + tail)}</span>
              </li>
            `);
          }
        } else {
          selected.forEach((category) => {
            items.push(`
              <li class=\"rule-item\">
                <span class=\"mark bad\"></span>
                <span>${escapeHtml(friendlyCategory(category, categoryLabels))}</span>
              </li>
            `);
          });
        }

        return `<ul class=\"rule-list\">${items.join(\"\")}</ul>`;
      };

      const renderTimeControls = (timeControls = []) => {
        if (!timeControls.length) {
          return '<div class="empty-copy">No time restrictions</div>';
        }
        return `
          <ul class=\"rule-list\">
            ${timeControls.map((window) => `
              <li class=\"rule-item\">
                <span class=\"mark ok\"></span>
                <span>${escapeHtml(`${formatDays(window.days)}  ${window.start_time} - ${window.end_time}  ${window.timezone}`)}</span>
              </li>
            `).join(\"\")}
          </ul>
        `;
      };

      const renderAmountControls = (amountControls) => {
        const perTransaction = amountControls?.per_transaction || null;
        const periodic = amountControls?.periodic || null;
        const periodicLabel = periodic ? `${titleizeEnum(periodic.period)} limit` : \"Monthly limit\";
        return `
          <div class=\"detail-grid\">
            <div class=\"detail-row\">
              <span class=\"detail-label\">Per transaction</span>
              <span class=\"detail-value\">${formatAmount(perTransaction)}</span>
            </div>
            <div class=\"detail-row\">
              <span class=\"detail-label\">${escapeHtml(periodicLabel)}</span>
              <span class=\"detail-value\">${periodic ? formatAmount(periodic.amount) : \"none\"}</span>
            </div>
          </div>
        `;
      };

      const renderMerchantControls = (merchantControls) => {
        if (!merchantControls || !merchantControls.values?.length) {
          return '<div class="empty-copy">No merchant-specific rules</div>';
        }
        return `
          <div class=\"detail-grid\">
            <div class=\"detail-row\">
              <span class=\"detail-label\">Type</span>
              <span class=\"detail-value\">${escapeHtml(titleizeEnum(merchantControls.type))}</span>
            </div>
            <div class=\"detail-row\">
              <span class=\"detail-label\">Restriction</span>
              <span class=\"detail-value\">${escapeHtml(merchantControls.restriction)}</span>
            </div>
            <div class=\"tag-cloud\">${merchantControls.values.map((value) => `<span class=\"tag\">${escapeHtml(value)}</span>`).join(\"\")}</div>
          </div>
        `;
      };

      const renderError = (data) => {
        appRoot.innerHTML = `
          <p class=\"title\">card controls inspector</p>
          <p class=\"meta\">Unable to render controls</p>
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

        const controls = data.controls || {};
        const categoryControls = controls.category_controls;
        const timeControls = controls.time_controls || [];
        const amountControls = controls.amount_controls || {};
        const merchantControls = controls.merchant_controls;
        const categoryLabels = data.category_labels || {};
        const restriction = categoryControls?.restriction || \"none\";
        const restrictionClass = restriction === \"ALLOWED\" ? \"allowed\" : \"blocked\";
        const lastFour = data.card_last_four || String(data.card_token || \"\").slice(-4);

        appRoot.innerHTML = `
          <p class=\"title\">card controls inspector</p>
          <p class=\"meta\">Card: ****${escapeHtml(lastFour)} &middot; ${escapeHtml(data.cardholder?.name || \"unknown\")} &middot; ${escapeHtml(data.cardholder?.team || \"no team\")}</p>

          <div class=\"section\">
            <div class=\"row\">
              <h3>category controls</h3>
              <span class=\"status-pill ${restrictionClass}\">${escapeHtml(restriction)}</span>
            </div>
            ${renderCategoryControls(categoryControls, categoryLabels)}
          </div>

          <div class=\"section\">
            <h3>time controls</h3>
            ${renderTimeControls(timeControls)}
          </div>

          <div class=\"section\">
            <h3>amount controls</h3>
            ${renderAmountControls(amountControls)}
          </div>

          <div class=\"section\">
            <h3>merchant controls</h3>
            ${renderMerchantControls(merchantControls)}
          </div>

          <div class=\"summary\">${escapeHtml(data.controls_summary || \"No restrictions active.\")}</div>

          <div class=\"scenario\">Scenario: &quot;${escapeHtml(data.scenario || \"No scenario provided\")}&quot;</div>
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
