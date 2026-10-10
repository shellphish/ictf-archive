const { createHmac } = require('crypto');

const SECRET = process.env.JWT_SECRET;

function b64url(str) {
  return Buffer.from(str).toString('base64url');
}

function signToken(payload) {
  const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = b64url(JSON.stringify(payload));
  const sig = createHmac('sha256', SECRET).update(`${header}.${body}`).digest('base64url');
  return `${header}.${body}.${sig}`;
}

function verifyToken(token, session) {
  const parts = (token || '').split('.');
  if (parts.length !== 3) throw new Error('malformed token');
  const [headerB64, payloadB64, sig] = parts;

  const header = JSON.parse(Buffer.from(headerB64, 'base64url').toString());
  const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString());

  if (header.alg !== 'HS256') {
    throw new Error('algorithm not allowed');
  }

  if (header.alg !== 'none') {
    const expected = createHmac('sha256', SECRET)
      .update(`${headerB64}.${payloadB64}`)
      .digest('base64url');
    if (sig !== expected) throw new Error('invalid signature');
  }

  if (session && session.userSub && payload.sub !== session.userSub) {
    throw new Error('subject mismatch');
  }

  return payload;
}

module.exports = { signToken, verifyToken };
