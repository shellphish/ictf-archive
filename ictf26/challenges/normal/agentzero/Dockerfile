FROM node:20-alpine

WORKDIR /app

# Install backend dependencies
COPY backend/package*.json ./backend/
RUN cd backend && npm install --production

# Copy backend source
COPY backend/src ./backend/src

# Install UI dependencies and build
COPY ui/package*.json ./ui/
RUN cd ui && npm install
COPY ui/ ./ui/
RUN cd ui && npm run build

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV FLAG=ictf{local_test_flag}
ENV JWT_SECRET=change_me
ENV LLM_BASE_URL=
ENV LLM_API_KEY=
ENV LLM_MODEL=gpt-4o-mini
ENV BACKEND_URL=http://localhost:3000

EXPOSE 3001

CMD ["/start.sh"]
