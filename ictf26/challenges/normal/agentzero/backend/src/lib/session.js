const { randomUUID } = require('crypto');

const sessions = new Map();

function parseCookies(header) {
  if (!header) return {};
  return Object.fromEntries(
    header.split(';')
      .map(c => c.trim().split('='))
      .filter(p => p.length === 2)
      .map(([k, v]) => [k.trim(), decodeURIComponent(v.trim())])
  );
}

function getSession(req, res) {
  const cookies = parseCookies(req.headers.cookie);
  let id = cookies.sid;
  if (!id || !sessions.has(id)) {
    id = randomUUID();
    sessions.set(id, {});
    res.setHeader('Set-Cookie', `sid=${id}; HttpOnly; SameSite=Lax; Path=/`);
  }
  return sessions.get(id);
}

module.exports = { getSession };
