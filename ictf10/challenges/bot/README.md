# iCTF 2010 — Bot Service

**Edition:** iCTF 2010 — Hit 'em Where it Hurts  
**Category:** Network  
**Source:** Extracted from VM image `dumps/ictf2010.bot.tar.gz`

## Description

The bot service is Litya's botnet agent. Each team's VM ran a copy of `bot.py`
that periodically connects to a central "mothership" C2 server at `10.14.0.100:8080`
and sends a base64-encoded heartbeat:

```
aGVhcnRiZWF0Cg==   (decodes to: "heartbeat\n")
```

The bot reconnects automatically on connection failure, sleeping 30 seconds between
attempts. Teams that compromised the bot service could disrupt rivals' check-in
cycles or intercept mothership commands.

## Source

`src/bot.py` — extracted from `/home/seclab/bot.py` on the competition VM
(Ubuntu Server 10.10 32-bit, VMware).

## Running

```bash
docker build -t ictf10-bot .
docker run -p 8080:8080 ictf10-bot
```

## Flag Format

`ictf2010{bot_compromised}`
