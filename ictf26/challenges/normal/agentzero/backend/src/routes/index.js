const { Router } = require('express');

const router = Router();

router.get('/', (req, res) => {
  res.json({
    name: 'AgentZero',
    version: '0.1.0',
    endpoints: {
      'POST /api/preferences': 'Update your session preferences',
      'GET /api/tools': 'List available agent tools',
      'POST /api/chat': 'Chat with the agent',
    },
  });
});

module.exports = router;
