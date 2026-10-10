# iCTF 2015 — Crowdsourcing Evil

**Date:** December 2015
**Format:** Attack-Defense

---

## The Story

The 2015 iCTF was themed **"Crowdsourcing Evil"** — a reflection of the
emerging crowdsourcing economy applied to the world of malware and cybercrime.
Teams played as competing criminal organizations crowdsourcing their hacking
operations through shared infrastructure.

## Services

### `notecxx` — C++ Note-Taking Service

A C++ service allowing users to write notes and issue load/save commands.

**The vulnerability:** Issuing a `read` command from the CLI secretly also
issued an `authenticate` command first, which read a 64-bit integer from a
passcode file and compared it against user input using `strtoull()`. The buffer
`"18446744073709551616"` (UINT64_MAX+1) caused integer overflow, allowing bypass.

```cpp
if (str == "read") {
    uint64_t passcode;
    cin >> passcode;
    commands.emplace_back(authenticate_tag(), passcode);
    commands.emplace_back(read_file_tag());
}
```

A writeup by team **DCIETS** is preserved in [`notecxx_writeup.md`](notecxx_writeup.md).

## Data

| Path | Contents |
|------|----------|
| `ictf_registration_apr_2015-final-final.sql` | Team registration database |
| `iCTF 2015 Team Location (Responses).xlsx` | Team geographic locations |
| `iCTF 2015 Working Notes.docx` | Organizer notes |
| `iCTF 2015 Service Vote.xlsx` | Service selection process |
| `The 2015 iCTF Evaluation Questionnaire (Responses).xlsx` | Participant feedback |
| `base-vms/` | Base VM images |
| `database/` | Competition database |
| `notecxx_writeup.md` | Challenge writeup (DCIETS) |

## References

- [Original website](https://ictf.cs.ucsb.edu/archive/2015/site)
- [Final results](https://ictf.cs.ucsb.edu/archive/2015/scoreboard)
- [Traffic dumps](https://ictf.cs.ucsb.edu/archive/2015/dumps)
- [Pictures](https://ictf.cs.ucsb.edu/archive/2015/pictures)
- [Video](https://www.youtube.com/watch?v=hAP04xIQ8yg)
- [Memes](http://chaoticshitshow.tumblr.com/)
