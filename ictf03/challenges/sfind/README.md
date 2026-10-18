# sfind — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, Shellphish)
**Category:** pwn / binary
**Format:** Attack-defense service

## Overview

`sfind` was a custom file-search daemon written in C. Clients connected via TCP
and submitted search requests specifying a filename glob and a keyword to grep for.
The service ran `find | grep` and returned matches. Flags were stored as keywords
in a file on disk, with the filename XOR-encoded in the binary.

## Protocol

Text-based TCP protocol; clients use the `sfindc` binary:

```
id <num>
user <username>
password <password>
filename <glob>
keyword <searchterm>
environ <VAR=value>
```

## Vulnerabilities

**1. Command injection via `keyword`** (from `sfind.c`):

```c
sprintf(cmd, "find %s -name \"%s\" -exec grep -H -n %s \\{\\} \\; > %s",
        init_cwd, filename, keyword, outf);
system(cmd);
```

The `keyword` is passed unquoted to `system()`. Injecting shell metacharacters
(e.g., `keyword=; cat /flag`) executes arbitrary commands.

**2. Environment variable injection**: The `environ` command calls `putenv()` before
the `find` exec, enabling `LD_PRELOAD` or `PATH` manipulation.

## Files

| File | Description |
|------|-------------|
| `src/sfind.c` | Final deployed server source |
| `src/weirdfind.c` | Earlier development version |
| `src/weirdfindc.c` | Earlier client version |
| `src/encode.c` | Flag/password XOR encoder |
| `src/get_sfind` | Scorebot flag retrieval script |
| `src/set_sfind` | Scorebot flag update script |
| `src/setup.sh` | VM deployment script |
| `src/init_sfind` | Service init script |

## Notes

- The hardcoded `BYPASSWORD = "XXGvWEuD1BDMI"` bypasses normal authentication.
- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
