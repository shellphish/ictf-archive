# spamagent — iCTF 2005

**Competition:** iCTF 2005 "The Spam Museum" (December 2005, UCSB)
**Category:** pwn / web
**Format:** Attack-defense service

## Overview

A C daemon implementing an XML-based spam agent scripting engine. Users POST
XML "agent" scripts via a web form; the service executes the embedded code
using a Tcl-like interpreter and returns results. Flags are stored in the
agent's key-value store and retrieved via the `store get flag` command.

## Architecture

```
http://<host>/~spamagent/spamagent.html   — agent submission form
POST script=<XML agent definition>
```

XML format:
```xml
<agent>
  <sender><user>name</user><password>pass</password></sender>
  <code>set flag [store get flag]; results set $flag</code>
</agent>
```

The `spamagent` binary (24KB C source) parses the XML and executes the `<code>`
using an embedded scripting engine. The `store get <key>` command retrieves
per-user stored values; `results set <value>` outputs the result.

## Vulnerability

Code injection via the `<code>` element. If the scripting engine lacks proper
sandboxing, arbitrary store keys can be read regardless of the authenticated
`<sender>`. An attacker submitting a valid XML agent with any credentials
may be able to enumerate and read other users' stored flags.

## Files

| File | Description |
|------|-------------|
| `src/spamagent.c` | C source for the agent interpreter (24KB) |
| `src/configure.in` | Autoconf build configuration |
| `src/Makefile.am` | Automake build file |
| `src/README` | Original README |
| `src/spamagent` | Compiled binary (deployed) |
| `src/spamAgentScoringScript.py` | Scorebot flag set/get script |

## Notes

- Source extracted from CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- The service was compiled with the `spamagent-1.0` autotools build system
  (from `/home/spamagent/spamagent-1.0/`).
- The scoring script uses credentials `name:password` in a cookie and the
  commands `store get flag` / `store set flag <value>` to manage the flag.
