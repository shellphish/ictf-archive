const { Router } = require('express');
const { randomUUID } = require('crypto');
const { signToken } = require('../lib/auth');
const { getSession } = require('../lib/session');

const router = Router();

router.post('/', (req, res) => {
  const session = getSession(req, res);
  if (!session.userSub) {
    session.userSub = `user_${randomUUID().slice(0, 8)}`;
  }
  const token = signToken({ sub: session.userSub, role: 'user' });
  const resp = { token };
  if (session.debug) {
    resp.debug = { secret: process.env.JWT_SECRET };
  }
  res.json(resp);
});

module.exports = router;
