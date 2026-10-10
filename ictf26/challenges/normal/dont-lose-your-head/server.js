const http = require("http");
const { URL } = require("url");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PORT = Number(process.env.PORT || 3000);
const FLAG = process.env.FLAG || "FLAG{change_me}";

const MP4_PATH = path.join(__dirname, "static", "flag.mp4");
const IMG_PATH = path.join(__dirname, "static", "image.png");

const SESSIONS = new Map();

function parseCookies(cookieHeader = "") {
  const out = {};
  cookieHeader.split(";").forEach((part) => {
    const [k, ...rest] = part.trim().split("=");
    if (!k) return;
    out[k] = rest.join("=") ?? "";
  });
  return out;
}

function randomId(n = 16) {
  return crypto.randomBytes(n).toString("hex");
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function serveMp4(req, res) {
  if (!fs.existsSync(MP4_PATH)) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Missing static/flag.mp4\n");
    return;
  }
  const stat = fs.statSync(MP4_PATH);
  const fileSize = stat.size;
  const range = req.headers.range;

  if (range) {
    const m = /^bytes=(\d+)-(\d*)$/.exec(range);
    if (!m) {
      res.writeHead(416, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Invalid Range\n");
      return;
    }
    const start = Number(m[1]);
    const end = m[2] ? Number(m[2]) : fileSize - 1;

    if (start >= fileSize || end >= fileSize || start > end) {
      res.writeHead(416, { "Content-Range": `bytes */${fileSize}` });
      res.end();
      return;
    }

    const chunkSize = end - start + 1;
    res.writeHead(206, {
      "Content-Type": "video/mp4",
      "Content-Length": chunkSize,
      "Content-Range": `bytes ${start}-${end}/${fileSize}`,
      "Accept-Ranges": "bytes",
      "Cache-Control": "no-store",
    });
    fs.createReadStream(MP4_PATH, { start, end }).pipe(res);
  } else {
    res.writeHead(200, {
      "Content-Type": "video/mp4",
      "Content-Length": fileSize,
      "Accept-Ranges": "bytes",
      "Cache-Control": "no-store",
    });
    fs.createReadStream(MP4_PATH).pipe(res);
  }
}

function servePng(res) {
  if (!fs.existsSync(IMG_PATH)) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Missing static/image.png\n");
    return;
  }
  const buf = fs.readFileSync(IMG_PATH);
  res.writeHead(200, { "Content-Type": "image/png", "Cache-Control": "no-store" });
  res.end(buf);
}

function page({ mode, isAdmin }) {
  const bg = (mode === "dark" || isAdmin) ? "#000000" : "#ffffff";
  const fg = (mode === "dark" || isAdmin) ? "#ffffff" : "#000000";

  const center = isAdmin
    ? `<div class="flag">${escapeHtml(FLAG)}</div>`
    : (mode === "dark"
        ? `
  <video id="m" src="/static/flag.mp4" autoplay muted loop playsinline preload="auto" disablepictureinpicture></video>
  <script>
    (function () {
      const v = document.getElementById('m');
      v.controls = false;
      v.loop = true;

      // Avvia subito muted (i browser lo permettono sempre)
      v.muted = true;
      v.play().catch(() => {});

      v.addEventListener('pause', () => { v.play().catch(() => {}); });

      // Al primo gesto dell'utente sblocca l'audio
      let unlocked = false;
      function unlock() {
        if (unlocked) return;
        unlocked = true;
        v.muted = false;
        v.volume = 1.0;
        v.play().catch(() => {});
        document.removeEventListener('click',     unlock, true);
        document.removeEventListener('touchstart', unlock, true);
        document.removeEventListener('keydown',    unlock, true);
      }
      document.addEventListener('click',      unlock, true);
      document.addEventListener('touchstart', unlock, true);
      document.addEventListener('keydown',    unlock, true);

      document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') e.preventDefault();
      }, { capture: true });
    })();
  </script>
`
        : `<img src="/static/image.png" alt="image">`
      );

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>theme</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body { height:100%; margin:0; }
    body{
      background:${bg};
      color:${fg};
      display:flex;
      align-items:center;
      justify-content:center;
      overflow:hidden;
    }
    img, video{
      max-width:min(92vw, 960px);
      max-height:90vh;
      display:block;
      border:none;
      border-radius:0;
      background:transparent;
    }
    .flag{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 28px;
      padding: 0;
      border: none;
      border-radius: 0;
      box-shadow: none;
      text-align:center;
      white-space: pre-wrap;
      word-break: break-word;
      max-width: 92vw;
    }
  </style>
</head>
<body>
  <div class="card">
    ${center}
  </div>
</body>
</html>`;
}

const server = http.createServer((req, res) => {
  const u = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const pathname = u.pathname;

  if (pathname === "/static/flag.mp4") return serveMp4(req, res);
  if (pathname === "/static/image.png") return servePng(res);

  if (pathname !== "/") {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("not found\n");
    return;
  }

  if (!u.searchParams.has("theme")) {
    res.writeHead(302, { Location: "/?theme=light" });
    res.end();
    return;
  }

  const cookies = parseCookies(req.headers.cookie);

  const sessionId = cookies.session || randomId(16);
  if (!SESSIONS.has(sessionId)) SESSIONS.set(sessionId, { admin: false });
  const sess = SESSIONS.get(sessionId);

  const themeRaw = u.searchParams.get("theme") ?? "light";
  const mode = themeRaw.startsWith("dark") ? "dark" : "light";

  const isAdmin = !!sess.admin;

  const headersRaw =
    "HTTP/1.1 200 OK\r\n" +
    "Content-Type: text/html; charset=utf-8\r\n" +
    "Cache-Control: no-store\r\n" +
    `Set-Cookie: session=${sessionId}; HttpOnly; SameSite=Lax\r\n` +
    `Set-Cookie: theme=${themeRaw}\r\n`;

  if (/(?:^|\r\n)Set-Cookie:\s*admin=true\b/i.test(headersRaw)) {
    sess.admin = true;
  }

  const raw = headersRaw + "\r\n" + page({ mode, isAdmin: sess.admin });

  res.socket.write(raw);
  res.socket.end();
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Listening on http://0.0.0.0:${PORT}`);
});