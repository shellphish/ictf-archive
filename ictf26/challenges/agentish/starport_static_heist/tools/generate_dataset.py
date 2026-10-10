#!/usr/bin/env python3
import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
TOOLS_DIR = ROOT / "tools"
DATA_DIR = ROOT / "services" / "mcp_logs" / "data"
PRIVATE_DIR = ROOT / "private"


@dataclass
class Event:
    ts: str
    session_id: str
    event_id: str
    event_type: str
    speaker_id: str
    speaker_alias: str
    text: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.ts,
            "session_id": self.session_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "speaker_id": self.speaker_id,
            "speaker_alias": self.speaker_alias,
            "text": self.text,
        }


def ts(base: datetime, seconds: int) -> str:
    return (base + timedelta(seconds=seconds)).isoformat() + "Z"


def build_events() -> List[Event]:
    base = datetime(2026, 2, 20, 19, 0, 0)
    session = "starport-concourse-42"
    # u03/sable12 is the secret holder.
    # Two-hop clue chain (no self-introduction, no direct "X has the secret"):
    #   Hop 1 — e030: "rotation key shards belong to whoever is on Gate 7 comms duty"
    #   Hop 2 — e052: "sable12 is on Gate 7 comms for tonight's session"
    # Decoys use non-obvious hex (3f8a, c91d, …) not readable words.
    # No meta-hints in the logs.
    return [
        # 0–60s: session opens, general noise
        Event(ts(base, 0),   session, "e001", "speech", "u01", "panda_loop",  "Mic check — anyone in the lobby?"),
        Event(ts(base, 7),   session, "e002", "speech", "u04", "zerochime",   "Here. Gate 3 queue was brutal tonight."),
        Event(ts(base, 13),  session, "e003", "speech", "u09", "raindot",     "Gate 3 always backs up after the shift change."),
        Event(ts(base, 20),  session, "e004", "speech", "u11", "mintwisp",    "Anyone running night ops tonight?"),
        Event(ts(base, 27),  session, "e005", "speech", "u14", "echo_moth",   "Night ops kick off at 20:00 sharp."),
        Event(ts(base, 34),  session, "e006", "speech", "u13", "drift_nine",  "West cluster latency is rough right now."),
        Event(ts(base, 40),  session, "e007", "speech", "u05", "glitch_ivy",  "Switching to east node then."),
        # sable12 posts real shards — no announcement, no self-identification
        Event(ts(base, 46),  session, "e008", "speech", "u03", "sable12",     "Key shard one: {{KEY_1}}"),
        Event(ts(base, 53),  session, "e009", "speech", "u17", "prism_syd",   "Cargo manifest for bay 4 is still incomplete."),
        Event(ts(base, 59),  session, "e010", "speech", "u02", "neon_lime",   "key shard one: 3f8a"),          # decoy

        # 60–120s
        Event(ts(base, 65),  session, "e011", "speech", "u03", "sable12",     "Key shard two: {{KEY_2}}"),
        Event(ts(base, 71),  session, "e012", "speech", "u10", "copper_fin",  "Has anyone seen the fuel depot status report?"),
        Event(ts(base, 77),  session, "e013", "speech", "u07", "aqua_haze",   "key shard two: c91d"),          # decoy
        Event(ts(base, 83),  session, "e014", "speech", "u15", "nova_ratch",  "Crew rotation schedule is posted in bay 2."),
        Event(ts(base, 89),  session, "e015", "speech", "u03", "sable12",     "Key shard three: {{KEY_3}}"),
        Event(ts(base, 96),  session, "e016", "speech", "u08", "vanta",       "key shard three: 7e2b"),        # decoy
        Event(ts(base, 103), session, "e017", "speech", "u01", "panda_loop",  "Anyone need a slot on the asteroid run?"),
        Event(ts(base, 109), session, "e018", "speech", "u18", "tangent_k",   "Queue is full, try again in five."),
        Event(ts(base, 116), session, "e019", "speech", "u04", "zerochime",   "Docking permissions expired on my end again."),
        Event(ts(base, 122), session, "e020", "speech", "u16", "hex_crane",   "key shard one: a4f3"),          # decoy

        # 120–180s
        Event(ts(base, 129), session, "e021", "speech", "u09", "raindot",     "East comms relay jammed — anyone else seeing this?"),
        Event(ts(base, 136), session, "e022", "speech", "u13", "drift_nine",  "Maintenance logged it, should clear in twenty."),
        Event(ts(base, 143), session, "e023", "speech", "u11", "mintwisp",    "key shard two: 8b5c"),          # decoy
        Event(ts(base, 150), session, "e024", "speech", "u05", "glitch_ivy",  "Who left the hangar doors open on deck C?"),
        Event(ts(base, 157), session, "e025", "speech", "u14", "echo_moth",   "Crew log shows it was an automated cycle trigger."),
        Event(ts(base, 163), session, "e026", "speech", "u17", "prism_syd",   "Automated cycles do not open exterior doors — that is wrong."),
        Event(ts(base, 170), session, "e027", "speech", "u02", "neon_lime",   "key shard three: 2e9f"),        # decoy
        Event(ts(base, 177), session, "e028", "speech", "u15", "nova_ratch",  "Filed an incident note for the Gate 7 comms breach."),
        Event(ts(base, 183), session, "e029", "speech", "u10", "copper_fin",  "Is there a duty officer assigned to Gate 7 right now?"),

        # 180–250s: Clue 1 + misdirection
        Event(ts(base, 190), session, "e030", "speech", "u06", "red_orbit",   "The rotation key shards belong to whoever is on Gate 7 comms duty this session."),
        Event(ts(base, 197), session, "e031", "speech", "u18", "tangent_k",   "I heard vanta pulled comms duty tonight — unconfirmed though."),   # misdirection
        Event(ts(base, 204), session, "e032", "speech", "u01", "panda_loop",  "Passenger stacking at Gate 5, queue management needed."),
        Event(ts(base, 211), session, "e033", "speech", "u16", "hex_crane",   "key shard one: d61a"),          # decoy
        Event(ts(base, 218), session, "e034", "speech", "u08", "vanta",       "Shift logs from yesterday show copper_fin on Gate 7 comms."),   # misdirection — yesterday's shift
        Event(ts(base, 225), session, "e035", "speech", "u09", "raindot",     "That was yesterday's crew. Tonight is a different rotation."),
        Event(ts(base, 232), session, "e036", "speech", "u04", "zerochime",   "I am not assigned to Gate 7 tonight — check the current roster."),
        Event(ts(base, 239), session, "e037", "speech", "u13", "drift_nine",  "Comms relay packet dump running now."),
        Event(ts(base, 246), session, "e038", "speech", "u07", "aqua_haze",   "key shard two: f047"),          # decoy
        Event(ts(base, 253), session, "e039", "speech", "u11", "mintwisp",    "Dock crew briefing was at 18:45 tonight."),

        # 250–320s: more noise
        Event(ts(base, 260), session, "e040", "speech", "u05", "glitch_ivy",  "Does anyone have the full duty roster link?"),
        Event(ts(base, 267), session, "e041", "speech", "u14", "echo_moth",   "Bay 9 sealed for inspection until 21:00."),
        Event(ts(base, 274), session, "e042", "speech", "u02", "neon_lime",   "key shard three: 5c8e"),        # decoy
        Event(ts(base, 281), session, "e043", "speech", "u17", "prism_syd",   "Stardock control, please confirm Gate 7 crew list."),
        Event(ts(base, 288), session, "e044", "speech", "u10", "copper_fin",  "Fuel rods need manual sign-off before bay 11 opens."),
        Event(ts(base, 295), session, "e045", "speech", "u18", "tangent_k",   "key shard one: 9a3d"),          # decoy
        Event(ts(base, 302), session, "e046", "speech", "u06", "red_orbit",   "Emergency lockdown drill at 20:30 — all crew acknowledge."),
        Event(ts(base, 309), session, "e047", "speech", "u08", "vanta",       "Drill will cut comms for five minutes."),
        Event(ts(base, 316), session, "e048", "speech", "u01", "panda_loop",  "Five-minute outage is too long during active ops."),

        # 316–380s: Clue 2 embedded in chatter
        Event(ts(base, 323), session, "e049", "speech", "u09", "raindot",     "My latency just spiked to 400ms."),
        Event(ts(base, 330), session, "e050", "speech", "u16", "hex_crane",   "key shard two: b73e"),          # decoy
        Event(ts(base, 337), session, "e051", "speech", "u13", "drift_nine",  "Node failover in sector 3 triggered."),
        Event(ts(base, 344), session, "e052", "speech", "u12", "solace",      "Duty board update: sable12 is on Gate 7 comms for tonight's session."),  # Clue 2
        Event(ts(base, 351), session, "e053", "speech", "u04", "zerochime",   "Admin request queue at thirty-two pending items."),
        Event(ts(base, 358), session, "e054", "speech", "u05", "glitch_ivy",  "key shard three: 4f1c"),        # decoy
        Event(ts(base, 365), session, "e055", "speech", "u11", "mintwisp",    "Power fluctuation on deck B, backup kicked in."),
        Event(ts(base, 372), session, "e056", "speech", "u14", "echo_moth",   "Generator backup report filed."),
        Event(ts(base, 379), session, "e057", "speech", "u17", "prism_syd",   "key shard one: e28c"),          # decoy

        # 380–450s
        Event(ts(base, 386), session, "e058", "speech", "u10", "copper_fin",  "Healer slot open for the raid run tonight."),
        Event(ts(base, 393), session, "e059", "speech", "u02", "neon_lime",   "GG run starts in ten minutes."),
        Event(ts(base, 400), session, "e060", "speech", "u07", "aqua_haze",   "Who archived the last bay manifest?"),
        Event(ts(base, 407), session, "e061", "speech", "u15", "nova_ratch",  "key shard two: 0d5b"),          # decoy
        Event(ts(base, 414), session, "e062", "speech", "u18", "tangent_k",   "Archival system offline for migration."),
        Event(ts(base, 421), session, "e063", "speech", "u08", "vanta",       "Migration was supposed to finish yesterday."),
        Event(ts(base, 428), session, "e064", "speech", "u12", "solace",      "key shard three: 6a9f"),        # decoy
        Event(ts(base, 435), session, "e065", "speech", "u06", "red_orbit",   "Dock supervisor requesting all crew IDs now."),
        Event(ts(base, 442), session, "e066", "speech", "u03", "sable12",     "ID submitted via secure channel."),
        Event(ts(base, 449), session, "e067", "speech", "u01", "panda_loop",  "Session wrapping up soon. Good ops everyone."),

        # 450–530s: wind-down
        Event(ts(base, 456), session, "e068", "speech", "u09", "raindot",     "Same channel next cycle?"),
        Event(ts(base, 463), session, "e069", "speech", "u13", "drift_nine",  "Confirmed. Signing off shortly."),
        Event(ts(base, 470), session, "e070", "speech", "u16", "hex_crane",   "key shard one: c3e7"),          # decoy
        Event(ts(base, 477), session, "e071", "speech", "u04", "zerochime",   "Maintenance window opens at midnight."),
        Event(ts(base, 484), session, "e072", "speech", "u11", "mintwisp",    "key shard two: 7b4d"),          # decoy
        Event(ts(base, 491), session, "e073", "speech", "u05", "glitch_ivy",  "Anyone doing the bridge puzzle run?"),
        Event(ts(base, 498), session, "e074", "speech", "u14", "echo_moth",   "Bridge puzzle resets after the drill."),
        Event(ts(base, 505), session, "e075", "speech", "u17", "prism_syd",   "Gate 7 comms log is being reviewed by supervisors."),
        Event(ts(base, 512), session, "e076", "speech", "u07", "aqua_haze",   "key shard three: 9c2a"),        # decoy
        Event(ts(base, 519), session, "e077", "speech", "u15", "nova_ratch",  "Supervisor review usually takes about an hour."),
        Event(ts(base, 526), session, "e078", "speech", "u08", "vanta",       "Crew assignments for next session posted in bay 1."),

        # 530–610s: final noise
        Event(ts(base, 533), session, "e079", "speech", "u02", "neon_lime",   "Heading to bay 1 now."),
        Event(ts(base, 540), session, "e080", "speech", "u10", "copper_fin",  "GG run is full, sorry late arrivals."),
        Event(ts(base, 547), session, "e081", "speech", "u12", "solace",      "Final boarding call for the night shuttle."),
        Event(ts(base, 554), session, "e082", "speech", "u18", "tangent_k",   "key shard one: 5d0e"),          # decoy
        Event(ts(base, 561), session, "e083", "speech", "u09", "raindot",     "Shuttle is always packed on Fridays."),
        Event(ts(base, 568), session, "e084", "speech", "u06", "red_orbit",   "See everyone next rotation."),
        Event(ts(base, 575), session, "e085", "speech", "u13", "drift_nine",  "Logs archived. Gate 7 comms closed for this session."),
        Event(ts(base, 582), session, "e086", "speech", "u16", "hex_crane",   "key shard two: 2f6c"),          # decoy
        Event(ts(base, 589), session, "e087", "speech", "u01", "panda_loop",  "Thanks all, same channel next time."),
        Event(ts(base, 596), session, "e088", "speech", "u04", "zerochime",   "Good session despite the latency issues."),
        Event(ts(base, 603), session, "e089", "speech", "u11", "mintwisp",    "Signing off. GG."),
        Event(ts(base, 610), session, "e090", "speech", "u05", "glitch_ivy",  "Later everyone."),
    ]


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")


def clear_old_parts(data_dir: Path) -> None:
    for p in data_dir.glob("vr_session_logs_part*.jsonl"):
        p.unlink()


def write_shuffled_parts(records: List[Dict[str, Any]], parts: int = 10, seed: int = 2026) -> List[Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clear_old_parts(DATA_DIR)

    rng = random.Random(seed)
    shuffled = list(records)
    rng.shuffle(shuffled)

    buckets: List[List[Dict[str, Any]]] = [[] for _ in range(parts)]
    for idx, record in enumerate(shuffled):
        buckets[idx % parts].append(record)

    output_paths: List[Path] = []
    for idx, bucket in enumerate(buckets, start=1):
        rng.shuffle(bucket)
        out = DATA_DIR / f"vr_session_logs_part{idx}.jsonl"
        write_jsonl(out, bucket)
        output_paths.append(out)
    return output_paths


def validator_script() -> str:
    return """#!/usr/bin/env python3
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = ROOT / "private" / "answer_key.json"


def now_unix() -> int:
    override = os.environ.get("CHALLENGE_NOW")
    if override:
        return int(override)
    return int(time.time())


def compute_temporal_key(secret: str, bucket: int) -> str:
    raw = f"{secret}|{bucket}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:10]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py <key>")
        return 2

    submitted = sys.argv[1].strip().lower()
    if not re.fullmatch(r"[a-f0-9]{10}", submitted):
        print("invalid format")
        return 1

    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    bucket = now_unix() // int(key["key_rotation_seconds"])
    expected = compute_temporal_key(key["key_secret"], bucket)
    if submitted == expected:
        print(key["flag"])
        return 0

    print("incorrect key")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
"""


def challenge_text() -> str:
    return """# Challenge: Starport Static Heist

At the Nova Starport arcade concourse, comms logs were dumped during a suspected vault breach.
The logs contain fragments of the current vault unlock key among a large volume of noise and decoys.

Objective:

Extract the current key from the logs and submit it to the validator to receive the flag.

Rules:

- The validator takes a key, not a flag.
- Log entries may be out of order and split across multiple files.
- Decoy content is present.
- The real key rotates every 30 seconds.
- You must submit the current key (old keys are rejected).
"""


def main() -> None:
    events = build_events()
    public_logs = [event.as_dict() for event in events]
    paths = write_shuffled_parts(public_logs, parts=10, seed=2026)

    answer = {
        "challenge_id": "starport-static-heist-001",
        "secret_holder_alias": "sable12",
        "secret_holder_speaker_id": "u03",
        "clue_event_ids": ["e030", "e052"],
        "key_shard_event_ids": ["e008", "e011", "e015"],
        "key_rotation_seconds": 30,
        "key_secret": "server-side-only-rotating-key-secret-v1",
        "flag": "flag{dock7-signal-scramble}",
    }

    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    with (PRIVATE_DIR / "answer_key.json").open("w", encoding="utf-8") as f:
        json.dump(answer, f, indent=2, ensure_ascii=True)
        f.write("\n")

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "challenge.md").write_text(challenge_text(), encoding="utf-8")
    (TOOLS_DIR / "validate.py").write_text(validator_script(), encoding="utf-8")

    print("Generated:")
    for p in paths:
        print(f"- {p}")
    print(f"- {PUBLIC_DIR / 'challenge.md'}")
    print(f"- {TOOLS_DIR / 'validate.py'}")
    print(f"- {PRIVATE_DIR / 'answer_key.json'}")


if __name__ == "__main__":
    main()
