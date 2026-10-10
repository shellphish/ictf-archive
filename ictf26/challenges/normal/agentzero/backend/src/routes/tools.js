const { Router } = require('express');
const { getSession } = require('../lib/session');
const { verifyToken } = require('../lib/auth');

const router = Router();

router.get('/', (req, res) => {
  const session = getSession(req, res);
  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';

  let decoded = null;
  try {
    decoded = verifyToken(token, session);
  } catch {
    decoded = null;
  }

  const tools = ['chat'];
  if (decoded && decoded.role === 'admin') {
    tools.push('listVaults');
    tools.push('openVault');
  }
  res.json({ tools });
});

module.exports = router;
