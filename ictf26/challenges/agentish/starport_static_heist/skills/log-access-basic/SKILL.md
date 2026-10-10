# Skill: log-access-basic

## Purpose
Provide only low-level access primitives. Students must build their own agent logic for identity resolution, ordering, and rotating key extraction.

## Exposed Tools

### `list_logs()`
Returns available log files.

Output example:

```json
{
  "logs": [
    "vr_session_logs_part1.jsonl",
    "vr_session_logs_part2.jsonl",
    "vr_session_logs_part3.jsonl",
    "vr_session_logs_part4.jsonl",
    "vr_session_logs_part5.jsonl"
  ]
}
```

### `retrieve_lines_from_log(log_name, start_line, end_line)`
Returns inclusive line range from one log file.

Input:
- `log_name`: string, must be one of `list_logs()` output.
- `start_line`: integer, 1-based.
- `end_line`: integer, 1-based and `>= start_line`.

Output example:

```json
{
  "log_name": "vr_session_logs_part1.jsonl",
  "start_line": 1,
  "end_line": 3,
  "lines": [
    "{\"timestamp\":\"...\",\"event_id\":\"e008\",...}",
    "{\"timestamp\":\"...\",\"event_id\":\"e002\",...}",
    "{\"timestamp\":\"...\",\"event_id\":\"e014\",...}"
  ]
}
```
