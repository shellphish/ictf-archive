# Starport Static Heist — Writeup

## Challenge Summary

Ten JSONL log files contain shuffled, noisy VR session events from many speakers.
The logs include ~20 decoy shard lines using non-obvious hex values, three misdirection
events pointing at the wrong crew members, and two clue events that together identify
the single authentic shard holder via two-hop reasoning.

## Intended Solution

1. **Enumerate logs** via `list_logs` to get all ten log file names.

2. **Fetch all events** via `retrieve_lines_from_log` for each file.

3. **Hop 1 — role clue**: scan events for a line that says the Gate 7 comms duty officer
   holds the rotation key shards (e030: *"The rotation key shards belong to whoever is on
   Gate 7 comms duty this session."*).

4. **Hop 2 — identity clue**: find the line that names the Gate 7 comms duty officer
   (e052: *"Duty board update: sable12 is on Gate 7 comms for tonight's session."*).
   Note: the holder never self-identifies and there is no direct "X has the secret"
   announcement; the identity must be inferred from the duty roster entry.

5. **Resolve speaker ID**: map alias `sable12` → `speaker_id` `u03` using the
   `speaker_alias` field in any of sable12's events.

6. **Collect shards**: filter events by `speaker_id == "u03"` and extract lines matching
   `"key shard (one|two|three): <hex>"`. Discard all other speakers' shard lines —
   they are decoys.

7. **Assemble the key**: sort shards by ordinal (one → two → three) and concatenate
   the three hex fragments.

8. **Submit** via `submit_key`. The key rotates every 30 seconds — submit promptly.
   The server returns `flag{dock7-signal-scramble}` on success.

## Misdirection to Ignore

- e031 claims vanta pulled comms duty (unconfirmed rumour — wrong).
- e034 says copper_fin was on Gate 7 comms (yesterday's shift — wrong).
- e036 has zerochime explicitly denying Gate 7 duty.

## Reference Solver

`solve.py` implements this algorithmically (no LLM required) as a correctness baseline.
A real CTF agent would use LLM reasoning to follow the two-hop clue chain through the
noisy log corpus.
