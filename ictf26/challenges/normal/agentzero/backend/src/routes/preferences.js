const { Router } = require('express');
const { deepMerge } = require('../lib/merge');
const { getSession } = require('../lib/session');

const router = Router();

router.post('/', (req, res) => {
  const session = getSession(req, res);
  deepMerge(session, req.body);
  res.json({ status: 'preferences updated' });
});

module.exports = router;
