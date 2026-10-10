# iCTF 2010 — Bribe Service

**Edition:** iCTF 2010 — Hit 'em Where it Hurts  
**Category:** Web  
**Port:** 8082  
**Source:** Extracted from VM `dumps/ictf2010.bribe.tar.gz`

## Description

Litya's corruption service. Teams paid in-game currency ("bribes") to gain
temporary firewall relief. The bribe amount was divided by a per-minute exchange
rate to compute minutes of protection, then forwarded to the scorekeeper and
firewall APIs.

### Endpoints

| Path | Description |
|------|-------------|
| `GET /` | Home page with bribe form |
| `GET /bribe?bribe=<amount>&fc=<token>` | Submit a bribe |
| `GET /style.css` | CSS stylesheet |

### Session Token

The anti-CSRF form cookie (`fc`) is computed as:

```python
hashlib.md5(client_ip + "youwillneverguessthissecretphrase").hexdigest()
```

### Key Credentials

- Scorekeeper API secret: `iseeeverything`
- Session secret: `youwillneverguessthissecretphrase`
- Dump auth: `auth=s3cr3t`

## Running

```bash
docker build -t ictf10-bribe .
docker run -p 8082:8082 ictf10-bribe
```

## Flag Format

`ictf2010{bribe_compromised}`
