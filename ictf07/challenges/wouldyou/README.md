# iCTF 2007 — Copyright Mafia: Would You...?

**Edition:** iCTF 2007 | **Category:** binary | **Language:** C++ (Windows PE) + Python 2 (CGI)

## Description

Mafia social compliance questionnaire: "Would you pay the fine? Would you
sign the settlement?" A compiled Windows PE executable runs under Wine on
the Linux CTF host. A Python 2.5 CGI script (`wouldyou.pyc`) bridges the
Apache web server to the Wine process via a local TCP socket.

## Architecture

```
Browser → Apache (port 80)
              ↓ CGI
          wouldyou.pyc (Python 2.5 CGI wrapper)
              ↓ localhost TCP socket
          wouldyou.exe (Wine — Windows PE binary)
```

### init.d Startup (reconstructed from `/etc/init.d/wouldyou` on VM)

```bash
DAEMON=/usr/bin/wine
ARGS="/home/wouldyou/public_html/wouldyou.exe"
start-stop-daemon --start -b -m -d $PROGHOME -c wouldyou \
    --pidfile /var/run/wouldyou.pid --exec $DAEMON -- $ARGS
```

The Python CGI layer receives HTTP requests, forwards them to the Wine
process socket, and relays responses back to the browser.

## Source Availability

| File | Status |
|------|--------|
| `src/wouldyou.exe` | Windows PE binary — available for RE |
| `src/wouldyou.pyc` | Python 2.5 CGI bytecode — available for RE |
| `src/wouldyou.cpp` | C++ source — **GPG-encrypted on VM**, key unknown |

## Vulnerability Hints

### In the Windows binary (wouldyou.exe)

- **Buffer overflow**: The binary likely uses fixed-size buffers for the
  TCP protocol fields; oversized input may overwrite the stack or heap
- **Format string**: Win32 `printf`-family functions with user-controlled
  format strings allow arbitrary read/write
- **Integer issues**: Question/answer IDs parsed with `atoi()` or
  `sscanf()` may overflow or wrap

### In the CGI wrapper (wouldyou.pyc)

- **Parameter injection**: URL parameters forwarded to the Win32 socket
  may not be sanitized; injecting socket protocol delimiters could
  manipulate requests seen by the exe
- **Session token**: The CGI layer may issue its own session tokens;
  examine the token format for predictability

## Reverse Engineering

The Python 2.5 bytecode can be decompiled with `uncompyle6` (Python 3.8-):

```bash
pip install uncompyle6
python -m uncompyle6 wouldyou.pyc
```

For the Windows binary:

```bash
# Static analysis
file wouldyou.exe
strings wouldyou.exe | less
# Dynamic: run under Wine with a debugger
wine wouldyou.exe &
winedbg --gdb wouldyou.exe
```

## Note

No Dockerfile — the service requires Wine. To reproduce locally:

```bash
apt-get install wine32
useradd -m wouldyou
su wouldyou -c 'wine /path/to/wouldyou.exe'
# Then run the Python CGI wrapper in your web server's cgi-bin
```
