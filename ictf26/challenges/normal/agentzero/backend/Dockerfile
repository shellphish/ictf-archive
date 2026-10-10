FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY src/ ./src/

ENV FLAG=ictf{local_test_flag}
ENV JWT_SECRET=change_me
ENV LLM_BASE_URL=
ENV LLM_API_KEY=
ENV LLM_MODEL=gpt-4o-mini

EXPOSE 3000

CMD ["node", "src/server.js"]
