import ipaddress
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import redis  # type: ignore[import-not-found]


CONFIG_KEY = "mariosoc:config"  # Redis hash
UBA_USERS_KEY = "mariosoc:uba:users_json"
EDR_HOSTS_KEY = "mariosoc:edr:hosts_json"
IDS_IPS_KEY = "mariosoc:ids:ips_json"

UBA_EVENTS_KEY_PREFIX = "mariosoc:uba:events:"
EDR_EVENTS_KEY_PREFIX = "mariosoc:edr:events:"
IDS_EVENTS_KEY_PREFIX = "mariosoc:ids:events:"

TRUTH_KEY = "mariosoc:truth"  # Redis hash (json blobs)


def _clean_env_value(v: str) -> str:
    """
    Be resilient to common `.env` mistakes where inline comments get appended to values, e.g.
    `ATTACK_SEED=123 # comment` or `INTERNAL_HOST_COUNT= # empty => random`.
    """
    return v.split("#", 1)[0].strip()


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    v_clean = _clean_env_value(v) if v is not None else ""
    if v is None or v_clean == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v_clean


def _maybe_int_env(name: str) -> int | None:
    v = os.environ.get(name)
    if v is None:
        return None
    v = _clean_env_value(v)
    if not v:
        return None
    return int(v)


def _maybe_float_env(name: str) -> float | None:
    v = os.environ.get(name)
    if v is None:
        return None
    v = _clean_env_value(v)
    if not v:
        return None
    return float(v)


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    v = _clean_env_value(v)
    if v == "":
        return default
    return v.lower() in {"1", "true", "yes", "y", "on"}


def _iso(ts: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


@dataclass(frozen=True)
class Host:
    ip: str
    domain: str


@dataclass(frozen=True)
class CveDef:
    cve_id: str
    title: str
    ids_signature: str


DOMAIN_POOL: list[str] = [
    # 50 plausible organization domains (mix of .com/.net/.org).
    "acme.com",
    "corp.com",
    "utility.org",
    "example.com",
    "example.net",
    "example.org",
    "contoso.com",
    "fabrikam.com",
    "northwindtraders.com",
    "adatum.com",
    "tailspintoys.com",
    "wideworldimporters.com",
    "woodgrovebank.com",
    "proseware.com",
    "treyresearch.net",
    "humongousinsurance.com",
    "blueyonderairlines.com",
    "litwareinc.com",
    "cohovineyard.com",
    "wingtiptoys.com",
    "alpineskihouse.com",
    "fourthcoffee.com",
    "margiestravel.com",
    "graphicdesigninstitute.org",
    "citypowerandlight.org",
    "cloudnine.net",
    "greenfieldenergy.org",
    "metrotransit.org",
    "riverbankcreditunion.org",
    "horizonhealthcare.org",
    "atlasmanufacturing.com",
    "pioneerlogistics.com",
    "summittelecom.net",
    "lakesideutilities.org",
    "primeconstruction.com",
    "starlightmedia.net",
    "evergreenconsulting.com",
    "silveroakfinancial.com",
    "seasidelabs.net",
    "highlandretail.com",
    "oakridgeuniversity.org",
    "redwoodsystems.net",
    "sunriseoutdoors.com",
    "copperleafsoftware.com",
    "ironcladsecurity.net",
    "skylineit.com",
    "meadowbrookservices.org",
    "grandcanyonhosting.net",
    "pinecrestsolutions.com",
    "clearwateranalytics.org",
]


def _pick_domain(rng: random.Random, *, exclude: set[str] | None = None) -> str:
    ex = exclude or set()
    choices = [d for d in DOMAIN_POOL if d not in ex]
    if not choices:
        # Fallback: allow reuse
        choices = list(DOMAIN_POOL)
    return rng.choice(choices)


def load_cves(cve_dir: Path) -> list[CveDef]:
    out: list[CveDef] = []
    for p in sorted(cve_dir.glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        cve_id = str(obj.get("cve_id", "")).strip()
        title = str(obj.get("title", "")).strip()
        ids_signature = str(obj.get("ids_signature", "")).strip()
        if not (cve_id and title and ids_signature):
            continue
        out.append(CveDef(cve_id=cve_id, title=title, ids_signature=ids_signature))
    if not out:
        raise RuntimeError(f"No valid CVE definitions found in {cve_dir}")
    return out


def pick_ip(net: ipaddress.IPv4Network, used: set[str], rng: random.Random) -> str:
    # Avoid .0/.1 and broadcast; pick from usable hosts
    hosts = list(net.hosts())
    for _ in range(10000):
        ip = str(rng.choice(hosts))
        if ip not in used:
            used.add(ip)
            return ip
    raise RuntimeError("Unable to allocate unique IP in network")


def _store_json(r: redis.Redis, key: str, obj: Any) -> None:
    r.set(key, json.dumps(obj, ensure_ascii=False))


def generate_attack(*, rng: random.Random, internal_count: int, success_rate: float, cves: list[CveDef]) -> dict[str, Any]:
    used_ips: set[str] = set()

    attacker_net = ipaddress.ip_network("203.0.113.0/24")
    internal_net = ipaddress.ip_network("10.0.5.0/24")

    # Keep the external host naming non-suspicious: avoid strings like "attacker" or "evil".
    ext_prefix = rng.choice(["edge", "relay", "node", "gw", "cdn", "router", "cache", "proxy"])
    corp_zone = _pick_domain(rng)
    ext_zone = _pick_domain(rng, exclude={corp_zone})

    attacker = Host(
        ip=pick_ip(attacker_net, used_ips, rng),
        domain=f"{ext_prefix}-{rng.randint(100, 999)}.{ext_zone}",
    )
    victim = Host(
        ip=pick_ip(internal_net, used_ips, rng),
        domain=f"workstation-{rng.randint(10, 99)}.{corp_zone}",
    )

    victim_user = rng.choice(
        [
            "amartin",
            "jdoe",
            "ssmith",
            "mnguyen",
            "rpatel",
            "dgarcia",
            "kchan",
        ]
    )

    # Internal targets (excluding the victim IP)
    internal_hosts: list[dict[str, Any]] = []
    for i in range(internal_count):
        ip = pick_ip(internal_net, used_ips, rng)
        internal_hosts.append(
            {
                "ip": ip,
                "domain": f"server-{i+1:02d}.{corp_zone}",
                "cve": None,
                "exploitation_succeeded": False,
            }
        )

    # Choose CVEs
    rng.shuffle(cves)
    for i, h in enumerate(internal_hosts):
        c = cves[i % len(cves)]
        h["cve"] = {"cve_id": c.cve_id, "title": c.title, "ids_signature": c.ids_signature}

    # Choose success set
    success_flags = [rng.random() < success_rate for _ in internal_hosts]
    if not any(success_flags):
        success_flags[rng.randrange(len(success_flags))] = True
    if all(success_flags) and len(success_flags) > 1:
        success_flags[rng.randrange(len(success_flags))] = False

    successful_internal: list[dict[str, Any]] = []
    failed_internal: list[dict[str, Any]] = []
    for h, ok in zip(internal_hosts, success_flags, strict=True):
        h["exploitation_succeeded"] = bool(ok)
        if ok:
            successful_internal.append(h)
        else:
            failed_internal.append(h)

    return {
        "attacker": {"ip": attacker.ip, "domain": attacker.domain},
        "victim": {"ip": victim.ip, "domain": victim.domain, "user": victim_user},
        "internal_hosts": internal_hosts,
        "successful_internal_hosts": successful_internal,
        "failed_internal_hosts": failed_internal,
        "internal_network_cidr": str(internal_net),
        "attacker_network_cidr": str(attacker_net),
    }


def build_logs(attack: dict[str, Any], *, rng: random.Random) -> dict[str, Any]:
    now = int(time.time())
    base_ts = now - 3600

    attacker = attack["attacker"]
    victim = attack["victim"]
    internal_hosts = attack["internal_hosts"]
    successful_internal = attack["successful_internal_hosts"]

    # --- User behavior (UBA) logs ---
    users = sorted({victim["user"], "svc-backup", "tjohnson", "hlewis", "opsbot"})

    uba_events: dict[str, list[dict[str, Any]]] = {u: [] for u in users}

    # Noise: 20 normal logins to internal hosts
    normal_users = [u for u in users if u != victim["user"]]
    for i in range(20):
        u = rng.choice(normal_users)
        dst = rng.choice(internal_hosts)["ip"]
        src = rng.choice(list(ipaddress.ip_network(attack["internal_network_cidr"]).hosts()))
        ev_ts = base_ts + 10 + i * 7
        uba_events[u].append(
            {
                "timestamp": _iso(ev_ts),
                "event_type": "login",
                "user": u,
                "source_ip": str(src),
                "destination_ip": dst,
                "destination_domain": next(h["domain"] for h in internal_hosts if h["ip"] == dst),
                "is_anomalous": False,
                "reason": "Known device / typical login pattern",
            }
        )

    # Signal: anomaly login from attacker IP to victim host for victim user
    anomaly_ts = base_ts + 600
    uba_events[victim["user"]].append(
        {
            "timestamp": _iso(anomaly_ts),
            "event_type": "login",
            "user": victim["user"],
            "source_ip": attacker["ip"],
            "source_domain": attacker["domain"],
            "destination_ip": victim["ip"],
            "destination_domain": victim["domain"],
            "is_anomalous": True,
            "reason": "User has never logged in from this source address",
        }
    )

    # --- EDR logs (victim host) ---
    edr_hosts = [victim["ip"]]
    edr_events: dict[str, list[dict[str, Any]]] = {victim["ip"]: []}

    # Noise: 20 normal executions of UNIX tools
    unix_tools = [
        "/bin/ls",
        "/bin/cat",
        "/usr/bin/grep",
        "/usr/bin/find",
        "/bin/ps",
        "/usr/bin/awk",
        "/usr/bin/sed",
        "/usr/bin/ssh",
        "/usr/bin/scp",
        "/usr/bin/curl",
    ]
    for i in range(20):
        ev_ts = base_ts + 200 + i * 11
        edr_events[victim["ip"]].append(
            {
                "timestamp": _iso(ev_ts),
                "event_type": "process_start",
                "host_ip": victim["ip"],
                "host_domain": victim["domain"],
                "process_path": rng.choice(unix_tools),
                "user": rng.choice(users),
                "severity": "info",
            }
        )

    # Signal: malicious download alert ("metasploit")
    edr_events[victim["ip"]].append(
        {
            "timestamp": _iso(base_ts + 900),
            "event_type": "malware_alert",
            "host_ip": victim["ip"],
            "host_domain": victim["domain"],
            "alert_name": "Suspicious download detected",
            "file_name": "metasploit",
            "file_path": "/tmp/metasploit",
            "severity": "high",
        }
    )

    # --- IDS logs ---
    ids_events_by_ip: dict[str, list[dict[str, Any]]] = {}

    def add_ids_event(ev: dict[str, Any]) -> None:
        for ip in {ev.get("src_ip"), ev.get("dst_ip")}:
            if not ip:
                continue
            ids_events_by_ip.setdefault(str(ip), []).append(ev)

    # Exploit attempts for each internal host (from victim host)
    for i, h in enumerate(internal_hosts):
        ev_ts = base_ts + 1200 + i * 13
        cve = h["cve"]
        add_ids_event(
            {
                "timestamp": _iso(ev_ts),
                "event_type": "ids_alert",
                "signature": str(cve["ids_signature"]),
                "cve_id": str(cve["cve_id"]),
                "src_ip": victim["ip"],
                "src_domain": victim["domain"],
                "dst_ip": h["ip"],
                "dst_domain": h["domain"],
                "severity": "medium",
            }
        )

    # C2 connections from successfully compromised internal hosts to attacker host
    for i, h in enumerate(successful_internal):
        ev_ts = base_ts + 1800 + i * 17
        add_ids_event(
            {
                "timestamp": _iso(ev_ts),
                "event_type": "ids_alert",
                "signature": "Command-and-control connection",
                "src_ip": h["ip"],
                "src_domain": h["domain"],
                "dst_ip": attacker["ip"],
                "dst_domain": attacker["domain"],
                "dst_port": 4444,
                "severity": "high",
            }
        )

    ids_ips = sorted(ids_events_by_ip.keys())
    return {
        "uba": {"users": users, "events_by_user": uba_events},
        "edr": {"hosts": edr_hosts, "events_by_host": edr_events},
        "ids": {"ips": ids_ips, "events_by_ip": ids_events_by_ip},
    }


def main() -> None:
    redis_url = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
    force_regen = _bool_env("FORCE_REGEN", True)

    seed_raw = os.environ.get("ATTACK_SEED")
    seed_clean = _clean_env_value(seed_raw) if seed_raw is not None else ""
    if seed_clean == "":
        seed = random.randrange(0, 2**31 - 1)
    else:
        seed = int(seed_clean)
    rng = random.Random(seed)

    internal_count = _maybe_int_env("INTERNAL_HOST_COUNT")
    if internal_count is None:
        internal_count = rng.randint(2, 10)
    internal_count = max(2, min(10, int(internal_count)))

    success_rate = _maybe_float_env("INTERNAL_SUCCESS_RATE")
    if success_rate is None:
        success_rate = 0.6
    success_rate = float(max(0.0, min(1.0, success_rate)))

    r = redis.Redis.from_url(redis_url, decode_responses=True)

    # Give Redis a moment on cold start.
    for _ in range(30):
        try:
            r.ping()
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("Redis not reachable")

    if not force_regen and r.exists(CONFIG_KEY):
        print(f"[datastore] {CONFIG_KEY} already exists; skipping (FORCE_REGEN=0).")
        return

    cves = load_cves(Path("/app/cves"))
    attack = generate_attack(rng=rng, internal_count=internal_count, success_rate=success_rate, cves=cves)
    logs = build_logs(attack, rng=rng)

    created_at = int(time.time())
    r.hset(
        CONFIG_KEY,
        mapping={
            "created_at": str(created_at),
            "attack_seed": str(seed),
            "internal_host_count": str(internal_count),
            "internal_success_rate": str(success_rate),
            "attacker_json": json.dumps(attack["attacker"], ensure_ascii=False),
            "victim_json": json.dumps(attack["victim"], ensure_ascii=False),
            "internal_hosts_json": json.dumps(attack["internal_hosts"], ensure_ascii=False),
        },
    )

    # Write logs
    _store_json(r, UBA_USERS_KEY, logs["uba"]["users"])
    for user, events in logs["uba"]["events_by_user"].items():
        _store_json(r, UBA_EVENTS_KEY_PREFIX + user, events)

    _store_json(r, EDR_HOSTS_KEY, logs["edr"]["hosts"])
    for host_ip, events in logs["edr"]["events_by_host"].items():
        _store_json(r, EDR_EVENTS_KEY_PREFIX + host_ip, events)

    _store_json(r, IDS_IPS_KEY, logs["ids"]["ips"])
    for ip, events in logs["ids"]["events_by_ip"].items():
        _store_json(r, IDS_EVENTS_KEY_PREFIX + ip, events)

    successful_internal_ips = [h["ip"] for h in attack["successful_internal_hosts"]]
    truth = {
        "attacker": attack["attacker"],
        "victim": attack["victim"],
        "successful_internal_ips": successful_internal_ips,
    }
    r.hset(TRUTH_KEY, mapping={"truth_json": json.dumps(truth, ensure_ascii=False), "created_at": str(created_at)})

    print(
        "[datastore] Generated Mario SOC attack. "
        f"attacker={attack['attacker']['ip']} victim={attack['victim']['ip']} "
        f"successful_internal={successful_internal_ips}"
    )


if __name__ == "__main__":
    main()

