(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = {
    comments: [],        // { user, text, avatar }
    removed: new Set(),  // users excluded by "re-draw"
    pool: [],
    spinning: false,
  };

  // ---------------- crypto-fair random ----------------
  function randInt(n) {
    if (n <= 1) return 0;
    const max = Math.floor(0x100000000 / n) * n; // rejection sampling: no modulo bias
    const buf = new Uint32Array(1);
    do { crypto.getRandomValues(buf); } while (buf[0] >= max);
    return buf[0] % n;
  }

  // ---------------- tabs ----------------
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => {
        const on = t === tab;
        t.classList.toggle("active", on);
        t.setAttribute("aria-selected", String(on));
      });
      document.querySelectorAll(".pane").forEach((p) => { p.hidden = p.dataset.pane !== tab.dataset.tab; });
    });
  });

  // ---------------- status ----------------
  function setStatus(msg, kind = "", busy = false) {
    const el = $("status");
    el.className = "status " + kind;
    el.textContent = msg;
    if (busy) { const d = document.createElement("span"); d.className = "dots"; el.appendChild(d); }
  }

  // ---------------- normalisation ----------------
  const cleanUser = (u) => String(u || "").trim().replace(/^@+/, "");
  function normalize(raw) {
    const out = [];
    for (const r of raw) {
      if (!r) continue;
      const user = cleanUser(r.uniqueId ?? r.username ?? r.user ?? r.author ?? r.nickname ?? r.name);
      if (!user) continue;
      out.push({
        user,
        text: String(r.text ?? r.comment ?? r.content ?? "").trim(),
        avatar: typeof (r.avatarThumbnail ?? r.avatar) === "string" ? (r.avatarThumbnail ?? r.avatar) : "",
      });
    }
    return out;
  }

  function parseLines(txt) {
    return txt.split(/\r?\n/).map((l) => l.trim()).filter(Boolean).map((l) => {
      const i = l.indexOf(":");
      return i > 0 ? { user: l.slice(0, i), text: l.slice(i + 1) } : { user: l.split(/\s+/)[0], text: l.split(/\s+/).slice(1).join(" ") };
    });
  }

  function parseCSV(txt) {
    const rows = [];
    let row = [], cell = "", q = false;
    for (let i = 0; i < txt.length; i++) {
      const c = txt[i];
      if (q) {
        if (c === '"' && txt[i + 1] === '"') { cell += '"'; i++; }
        else if (c === '"') q = false;
        else cell += c;
      } else if (c === '"') q = true;
      else if (c === "," || c === ";") { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && txt[i + 1] === "\n") i++;
        row.push(cell); rows.push(row); row = []; cell = "";
      } else cell += c;
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    const nonEmpty = rows.filter((r) => r.some((c) => c.trim()));
    if (!nonEmpty.length) return [];
    const head = nonEmpty[0].map((h) => h.trim().toLowerCase());
    const ui = head.findIndex((h) => ["uniqueid", "username", "user", "author", "nickname"].includes(h));
    const ti = head.findIndex((h) => ["text", "comment", "content"].includes(h));
    const ai = head.findIndex((h) => ["avatarthumbnail", "avatar"].includes(h));
    if (ui === -1) return nonEmpty.map((r) => ({ user: r[0], text: r[1] || "" })); // no header row
    return nonEmpty.slice(1).map((r) => ({ user: r[ui], text: ti >= 0 ? r[ti] : "", avatar: ai >= 0 ? r[ai] : "" }));
  }

  // ---------------- pool ----------------
  function excluded() {
    return new Set($("exclude").value.split(",").map((s) => cleanUser(s).toLowerCase()).filter(Boolean));
  }

  function rebuildPool() {
    const ex = excluded();
    const unique = $("unique").checked;
    const seen = new Set();
    const pool = [];
    for (const c of state.comments) {
      const key = c.user.toLowerCase();
      if (ex.has(key) || state.removed.has(key)) continue;
      if (unique) { if (seen.has(key)) continue; seen.add(key); }
      pool.push(c);
    }
    state.pool = pool;

    const uniqueCount = new Set(state.comments.map((c) => c.user.toLowerCase()).filter((u) => !ex.has(u))).size;
    $("stats").hidden = state.comments.length === 0;
    $("statTotal").textContent = state.comments.length.toLocaleString("ro-RO");
    $("statUnique").textContent = uniqueCount.toLocaleString("ro-RO");
    $("poolCount").textContent = pool.length.toLocaleString("ro-RO");
    $("spinBtn").disabled = pool.length === 0 || state.spinning;
    $("reelEmpty").hidden = pool.length > 0 || $("track").children.length > 0;
    renderPreview();
  }

  function renderPreview() {
    const ul = $("preview");
    ul.replaceChildren();
    for (const c of state.comments.slice(0, 30)) {
      const li = document.createElement("li");
      const b = document.createElement("b");
      b.textContent = "@" + c.user;
      li.append(b, " " + c.text);
      ul.appendChild(li);
    }
    if (state.comments.length > 30) {
      const li = document.createElement("li");
      li.textContent = `… și încă ${(state.comments.length - 30).toLocaleString("ro-RO")} comentarii`;
      ul.appendChild(li);
    }
  }

  function loadComments(list, source) {
    state.comments = normalize(list);
    state.removed.clear();
    $("winner").hidden = true;
    $("track").replaceChildren();
    $("track").style.transform = "translateX(0)";
    rebuildPool();
    if (state.comments.length) {
      setStatus(`Gata! Am încărcat ${state.comments.length.toLocaleString("ro-RO")} comentarii ${source}. Treci la pasul 2 👇`, "ok");
    } else {
      setStatus("Nu am găsit niciun comentariu valid.", "err");
    }
  }

  $("unique").addEventListener("change", rebuildPool);
  $("exclude").addEventListener("input", rebuildPool);

  // ---------------- manual input ----------------
  $("pasteBtn").addEventListener("click", () => loadComments(parseLines($("paste").value), "din listă"));
  $("file").addEventListener("change", async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const txt = await f.text();
    try {
      let rows;
      if (/\.json$/i.test(f.name) || /^\s*[[{]/.test(txt)) {
        const data = JSON.parse(txt);
        rows = Array.isArray(data) ? data : data.items || data.comments || [];
      } else if (/\.csv$/i.test(f.name)) rows = parseCSV(txt);
      else rows = parseLines(txt);
      loadComments(rows, `din ${f.name}`);
    } catch {
      setStatus("Nu am putut citi fișierul. Verifică formatul (JSON, CSV sau text).", "err");
    }
    e.target.value = "";
  });

  // ---------------- automatic extraction (via /api/comments) ----------------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function api(path, opts) {
    const r = await fetch(path, opts);
    const body = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(body.error || `Eroare server (${r.status})`);
    return body;
  }

  $("fetchBtn").addEventListener("click", async () => {
    const url = $("url").value.trim();
    if (!/^https:\/\/(www\.|vm\.|vt\.|m\.)?tiktok\.com\//i.test(url)) {
      setStatus("Lipește un link valid de TikTok (începe cu https://www.tiktok.com/ sau https://vm.tiktok.com/).", "err");
      return;
    }
    const btn = $("fetchBtn");
    btn.disabled = true;
    try {
      setStatus("Pornesc extragerea", "", true);
      const { runId } = await api("/api/comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const started = Date.now();
      let datasetId = null;
      while (true) {
        await sleep(4000);
        const s = await api(`/api/comments?runId=${encodeURIComponent(runId)}`);
        const secs = Math.round((Date.now() - started) / 1000);
        if (s.status === "SUCCEEDED") { datasetId = s.datasetId; break; }
        if (["FAILED", "ABORTED", "TIMED-OUT"].includes(s.status)) throw new Error(`Extragerea a eșuat (${s.status}). Încearcă din nou sau folosește varianta manuală.`);
        if (secs > 900) throw new Error("Durează prea mult. Încearcă din nou sau folosește varianta manuală.");
        setStatus(`Adun comentariile de pe TikTok (${secs}s)`, "", true);
      }

      const all = [];
      let offset = 0;
      while (offset !== null) {
        setStatus(`Descarc comentariile (${all.length.toLocaleString("ro-RO")})`, "", true);
        const page = await api(`/api/comments?datasetId=${encodeURIComponent(datasetId)}&offset=${offset}`);
        all.push(...page.items);
        offset = page.nextOffset;
      }
      loadComments(all, "de pe TikTok");
    } catch (err) {
      setStatus(err.message || "Ceva n-a mers.", "err");
    } finally {
      btn.disabled = false;
    }
  });

  // ---------------- reel ----------------
  function slotEl(c) {
    const d = document.createElement("div");
    d.className = "slot";
    const u = document.createElement("div");
    u.className = "u";
    const ph = document.createElement("span");
    ph.className = "ph";
    u.appendChild(ph);
    if (c.avatar) {
      const img = new Image();
      img.referrerPolicy = "no-referrer";
      img.alt = "";
      img.loading = "lazy";
      img.onload = () => ph.replaceWith(img);
      img.src = c.avatar;
    }
    const name = document.createElement("span");
    name.textContent = "@" + c.user;
    u.appendChild(name);
    const t = document.createElement("div");
    t.className = "t";
    t.textContent = c.text || "💬";
    d.append(u, t);
    return d;
  }

  const easeOutQuint = (t) => 1 - Math.pow(1 - t, 5);

  function spin() {
    if (state.spinning || !state.pool.length) return;
    state.spinning = true;
    $("spinBtn").disabled = true;
    $("redrawBtn").disabled = true;
    $("winner").hidden = true;
    $("reelEmpty").hidden = true;

    const pool = state.pool;
    const winner = pool[randInt(pool.length)];

    // Visual filler: a shuffled sample of real participants, winner placed near the end.
    const TOTAL = 90, WIN_AT = 76;
    const cards = [];
    for (let i = 0; i < TOTAL; i++) cards.push(i === WIN_AT ? winner : pool[randInt(pool.length)]);

    const track = $("track");
    track.replaceChildren(...cards.map(slotEl));
    track.style.transform = "translateX(0)";

    const first = track.children[0];
    const slotW = first.offsetWidth;
    const step = slotW + parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || "12");
    const reelW = $("reel").clientWidth;
    const jitter = (randInt(1000) / 1000 - 0.5) * slotW * 0.7; // land anywhere inside the card
    const target = WIN_AT * step + slotW / 2 - reelW / 2 + jitter;

    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const duration = reduce ? 1200 : 7000;
    const t0 = performance.now();

    function frame(now) {
      const p = Math.min((now - t0) / duration, 1);
      track.style.transform = `translateX(${-target * easeOutQuint(p)}px)`;
      if (p < 1) requestAnimationFrame(frame);
      else finish(winner, track.children[WIN_AT]);
    }
    requestAnimationFrame(frame);
  }

  function finish(winner, el) {
    el.classList.add("win");
    state.spinning = false;
    state.current = winner;

    const av = $("wAvatar");
    av.referrerPolicy = "no-referrer";
    av.hidden = !winner.avatar;
    av.onerror = () => { av.hidden = true; };
    if (winner.avatar) av.src = winner.avatar;
    $("wUser").textContent = "@" + winner.user;
    $("wText").textContent = winner.text;
    $("winner").hidden = false;
    $("redrawBtn").disabled = false;
    $("spinBtn").disabled = state.pool.length === 0;
    $("winner").scrollIntoView({ behavior: "smooth", block: "center" });
    confetti();
  }

  $("spinBtn").addEventListener("click", spin);
  $("redrawBtn").addEventListener("click", () => {
    if (!state.current || state.spinning) return;
    state.removed.add(state.current.user.toLowerCase());
    $("removed").textContent = "Scoși din extragere: " + [...state.removed].map((u) => "@" + u).join(", ");
    state.current = null;
    rebuildPool();
    if (state.pool.length) spin();
    else setStatus("Nu mai sunt participanți în extragere.", "err");
  });

  // ---------------- confetti ----------------
  function confetti() {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const cv = $("confetti");
    const ctx = cv.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    cv.width = innerWidth * dpr; cv.height = innerHeight * dpr;
    ctx.scale(dpr, dpr);
    const colors = ["#ff5fb2", "#9b4dff", "#ff9bd2", "#c79bff", "#ffd1ec", "#ffffff"];
    const parts = Array.from({ length: 180 }, () => ({
      x: innerWidth / 2 + (Math.random() - 0.5) * 200,
      y: innerHeight / 2,
      vx: (Math.random() - 0.5) * 16,
      vy: -Math.random() * 16 - 4,
      s: Math.random() * 8 + 5,
      r: Math.random() * Math.PI,
      vr: (Math.random() - 0.5) * 0.3,
      c: colors[(Math.random() * colors.length) | 0],
      heart: Math.random() < 0.3,
    }));
    const t0 = performance.now();
    (function draw(now) {
      ctx.clearRect(0, 0, innerWidth, innerHeight);
      for (const p of parts) {
        p.vy += 0.35; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c;
        if (p.heart) { ctx.font = `${p.s * 2}px sans-serif`; ctx.fillText("💖", -p.s, p.s); }
        else ctx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2);
        ctx.restore();
      }
      if (now - t0 < 4500) requestAnimationFrame(draw);
      else ctx.clearRect(0, 0, innerWidth, innerHeight);
    })(t0);
  }

  rebuildPool();
})();
