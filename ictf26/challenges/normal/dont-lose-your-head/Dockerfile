FROM node:20-alpine
WORKDIR /app
COPY package.json ./package.json
COPY server.js ./server.js
COPY static ./static
RUN addgroup -S app && adduser -S app -G app
USER app
ENV PORT=3000
ENV FLAG=ictf{crlf_g0t_me_4dm1n_73183220}

EXPOSE 3000
CMD ["npm", "start"]