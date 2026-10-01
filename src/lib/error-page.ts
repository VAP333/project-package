export function renderErrorPage(error?: unknown): string {
  let errorMessage = "Something went wrong on our end. You can try refreshing or head back home.";
  let errorStack = "";

  if (error instanceof Error) {
    errorMessage = error.message || String(error);
    errorStack = error.stack || "";
  } else if (typeof error === "string") {
    errorMessage = error;
  } else if (error && typeof error === "object") {
    try {
      errorMessage = JSON.stringify(error, null, 2);
    } catch {
      errorMessage = String(error);
    }
  }

  // Escape HTML entities to prevent injection
  const escapeHtml = (str: string) =>
    str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const safeMessage = escapeHtml(errorMessage);
  const safeStack = escapeHtml(errorStack);

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>This page didn't load — AksharSetu</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root {
        --bg: #0f172a;
        --card: #1e293b;
        --border: #334155;
        --text: #f8fafc;
        --muted: #94a3b8;
        --primary: #3b82f6;
        --primary-hover: #2563eb;
        --danger: #ef4444;
        --danger-bg: rgba(239, 68, 68, 0.1);
      }
      @media (prefers-color-scheme: light) {
        :root {
          --bg: #f8fafc;
          --card: #ffffff;
          --border: #e2e8f0;
          --text: #0f172a;
          --muted: #64748b;
          --primary: #2563eb;
          --primary-hover: #1d4ed8;
          --danger: #dc2626;
          --danger-bg: #fef2f2;
        }
      }
      body {
        font: 15px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: var(--bg);
        color: var(--text);
        display: grid;
        place-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 1.5rem;
        box-sizing: border-box;
      }
      .card {
        max-width: 36rem;
        width: 100%;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 1rem;
        text-align: center;
        padding: 2.25rem 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
      }
      .icon {
        width: 3.5rem;
        height: 3.5rem;
        margin: 0 auto 1.25rem;
        border-radius: 9999px;
        background: var(--danger-bg);
        color: var(--danger);
        display: grid;
        place-items: center;
        font-size: 1.75rem;
        font-weight: bold;
      }
      h1 {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem;
        letter-spacing: -0.025em;
      }
      p.sub {
        color: var(--muted);
        margin: 0 0 1.5rem;
        font-size: 0.95rem;
      }
      .error-details {
        margin: 1.25rem 0;
        text-align: left;
        background: var(--danger-bg);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 0.5rem;
        padding: 0.875rem 1rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.8125rem;
        color: var(--danger);
        word-break: break-word;
        max-height: 14rem;
        overflow-y: auto;
      }
      .error-title {
        font-weight: 700;
        margin-bottom: 0.25rem;
      }
      pre {
        margin: 0.5rem 0 0;
        white-space: pre-wrap;
        font-size: 0.75rem;
        color: var(--muted);
      }
      .actions {
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 1.5rem;
      }
      a, button {
        padding: 0.625rem 1.25rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        border: 1px solid transparent;
        transition: all 0.15s ease-in-out;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
      }
      .primary {
        background: var(--primary);
        color: #ffffff;
      }
      .primary:hover {
        background: var(--primary-hover);
      }
      .secondary {
        background: transparent;
        color: var(--text);
        border-color: var(--border);
      }
      .secondary:hover {
        background: rgba(148, 163, 184, 0.1);
      }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="icon">!</div>
      <h1>This page didn't load</h1>
      <p class="sub">Something went wrong on our end. You can try refreshing or head back home.</p>
      
      ${
        errorStack || errorMessage !== "Something went wrong on our end. You can try refreshing or head back home."
          ? `<div class="error-details">
              <div class="error-title">${safeMessage}</div>
              ${safeStack ? `<pre>${safeStack}</pre>` : ""}
            </div>`
          : ""
      }

      <div class="actions">
        <button class="primary" onclick="location.reload()">Try again</button>
        <a class="secondary" href="/">Go home</a>
        <a class="secondary" href="/read">Open History Reader</a>
      </div>
    </div>
  </body>
</html>`;
}
