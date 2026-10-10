# Don't Lose Your Head

A minimal Node.js web app with a light/dark theme toggle.
The flag is only shown to admin users, but the session logic has a flaw.

## Components

- **crlf-ctf**: Bare `http` Node.js server (no framework). Handles a single route (`/`)
  with a `?theme=` query parameter. The server builds the HTTP response by manually
  concatenating a header string and writing it directly to the socket.
  The `theme` value is reflected verbatim into a `Set-Cookie: theme=<value>` header
  line without any sanitisation, enabling CRLF injection.
  Admin status is determined by checking whether the raw header string contains a
  `Set-Cookie: admin=true` line — a check that can be satisfied through the injection.

## Intended solve

1. Send a request with a crafted `theme` parameter that injects a newline sequence
   followed by `Set-Cookie: admin=true` into the response headers:
   ```
   GET /?theme=dark%0d%0aSet-Cookie:%20admin=true HTTP/1.1
   ```
2. The server appends the injected line to `headersRaw` and then tests `headersRaw`
   against the admin regex — which now matches — so `sess.admin` is set to `true`.
3. The response is served with admin privileges and the flag is displayed.

## Quickstart (local/dev)

```bash
docker compose up --build
```

The service is exposed on port **3000**.