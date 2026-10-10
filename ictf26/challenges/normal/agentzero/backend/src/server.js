const express = require('express');

const indexRouter = require('./routes/index');
const authRouter = require('./routes/auth');
const preferencesRouter = require('./routes/preferences');
const toolsRouter = require('./routes/tools');
const chatRouter = require('./routes/chat');

const app = express();
app.use(express.json());

app.use('/', indexRouter);
app.use('/api/auth', authRouter);
app.use('/api/preferences', preferencesRouter);
app.use('/api/tools', toolsRouter);
app.use('/api/chat', chatRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT);
