// Vercel serverless function: talks to Apify so the API token never reaches the browser.
//
//   POST /api/comments            { url, max }   -> starts a scraper run  -> { runId }
//   GET  /api/comments?runId=...                 -> run status            -> { status, datasetId }
//   GET  /api/comments?datasetId=...&offset=N    -> one page of comments  -> { items, nextOffset }
//
// Env vars (set in Vercel → Project → Settings → Environment Variables):
//   APIFY_TOKEN  (required)  your Apify API token
//   APIFY_ACTOR  (optional)  defaults to clockworks~tiktok-comments-scraper

const APIFY = "https://api.apify.com/v2";
const PAGE = 1000;
const TIKTOK_URL = /^https:\/\/(www\.|vm\.|vt\.|m\.)?tiktok\.com\/\S+$/i;
const ID = /^[A-Za-z0-9]{8,32}$/;

async function apify(path, token, init = {}) {
  const r = await fetch(APIFY + path, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(init.headers || {}) },
  });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) {
    const msg = body?.error?.message || `Apify a răspuns cu ${r.status}`;
    const err = new Error(msg);
    err.status = r.status === 401 || r.status === 403 ? 500 : 502;
    throw err;
  }
  return body;
}

module.exports = async function handler(req, res) {
  const token = process.env.APIFY_TOKEN;
  const actor = process.env.APIFY_ACTOR || "clockworks~tiktok-comments-scraper";
  res.setHeader("Cache-Control", "no-store");

  if (!token) {
    return res.status(500).json({ error: "Lipsește APIFY_TOKEN din setările Vercel." });
  }

  try {
    if (req.method === "POST") {
      const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
      const url = String(body.url || "").trim();
      const max = Math.min(Math.max(parseInt(body.max, 10) || 5000, 1), 20000);
      if (!TIKTOK_URL.test(url)) {
        return res.status(400).json({ error: "Linkul nu pare a fi de pe TikTok." });
      }
      const run = await apify(`/acts/${encodeURIComponent(actor)}/runs`, token, {
        method: "POST",
        body: JSON.stringify({ postURLs: [url], commentsPerPost: max, maxRepliesPerComment: 0 }),
      });
      return res.status(200).json({ runId: run.data.id });
    }

    if (req.method === "GET") {
      const { runId, datasetId } = req.query || {};
      if (runId) {
        if (!ID.test(runId)) return res.status(400).json({ error: "runId invalid." });
        const run = await apify(`/actor-runs/${runId}`, token);
        return res.status(200).json({ status: run.data.status, datasetId: run.data.defaultDatasetId });
      }
      if (datasetId) {
        if (!ID.test(datasetId)) return res.status(400).json({ error: "datasetId invalid." });
        const offset = Math.max(parseInt(req.query.offset, 10) || 0, 0);
        const qs = new URLSearchParams({
          clean: "true",
          format: "json",
          offset: String(offset),
          limit: String(PAGE),
          fields: "cid,uniqueId,text,avatarThumbnail",
        });
        const items = await apify(`/datasets/${datasetId}/items?${qs}`, token);
        const list = Array.isArray(items) ? items : [];
        return res.status(200).json({ items: list, nextOffset: list.length === PAGE ? offset + PAGE : null });
      }
      return res.status(400).json({ error: "Lipsește runId sau datasetId." });
    }

    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({ error: "Metodă nepermisă." });
  } catch (e) {
    return res.status(e.status || 500).json({ error: e.message || "Eroare necunoscută." });
  }
};
