"""
MCP Server for NetBreach — Cybersecurity Attack-Simulation CTF Challenge

A turn-based, text-based game where the player acts as a red-team operator
attempting to compromise a Windows Domain Controller inside a procedurally
generated corporate network.

Tools (action):  scan, exploit, move, exfiltrate, pivot, sleep, cloak
Tools (free):    status, get_map
"""

import json
import os
import random
import time
import math
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FLAG = os.environ["FLAG_CHALLENGE"]

# Detection thresholds
DETECTION_GREEN = 30
DETECTION_YELLOW = 50
DETECTION_ORANGE = 75
DETECTION_RED = 90  # game over

# ---------------------------------------------------------------------------
# CVE Pool
# ---------------------------------------------------------------------------
CVE_POOL = [
    {"id": "CVE-2024-21762", "service": "HTTP", "name": "FortiGate RCE", "reliability": 0.80},
    {"id": "CVE-2024-3400", "service": "HTTP", "name": "PAN-OS Command Injection", "reliability": 0.75},
    {"id": "CVE-2023-36884", "service": "SMB", "name": "Office HTML RCE", "reliability": 0.70},
    {"id": "CVE-2024-1709", "service": "HTTP", "name": "ScreenConnect Auth Bypass", "reliability": 0.85},
    {"id": "CVE-2023-46805", "service": "SSH", "name": "Ivanti Connect Secure Bypass", "reliability": 0.75},
    {"id": "CVE-2024-21887", "service": "HTTP", "name": "Ivanti Command Injection", "reliability": 0.80},
    {"id": "CVE-2023-4966", "service": "HTTP", "name": "Citrix Bleed", "reliability": 0.82},
    {"id": "CVE-2023-27997", "service": "SSH", "name": "FortiGate SSL-VPN Heap Overflow", "reliability": 0.65},
    {"id": "CVE-2024-6387", "service": "SSH", "name": "RegreSSHion OpenSSH RCE", "reliability": 0.60},
    {"id": "CVE-2023-28252", "service": "SMB", "name": "Windows CLFS Priv Escalation", "reliability": 0.72},
    {"id": "CVE-2024-30088", "service": "RDP", "name": "Windows Kernel Elevation", "reliability": 0.68},
    {"id": "CVE-2024-49113", "service": "LDAP", "name": "LDAPNightmare DoS/RCE", "reliability": 0.55},
    {"id": "CVE-2024-47575", "service": "SQL", "name": "FortiManager RCE", "reliability": 0.72},
    {"id": "CVE-2023-22515", "service": "HTTP", "name": "Confluence Auth Bypass", "reliability": 0.78},
]

SERVICES_POOL = ["SMB", "RDP", "HTTP", "SSH", "SQL", "LDAP"]

OS_POOL = [
    "Windows Server 2019",
    "Windows Server 2022",
    "Windows 10 Enterprise",
    "Ubuntu 22.04 LTS",
    "Red Hat Enterprise Linux 9",
    "Debian 12 Bookworm",
    "Windows 11 Enterprise",
]

# Host name pools per subnet
DMZ_NAMES = ["WEB-DMZ-01", "FW-EDGE-01", "PROXY-DMZ-01", "MAIL-GW-01"]
CORP_NAMES = ["WS-CORP-01", "WS-CORP-02", "FS-CORP-01", "APP-CORP-01"]
SERVER_NAMES = ["DB-SRV-01", "APP-SRV-01", "MGMT-SRV-01", "BACKUP-SRV-01"]
DC_NAMES = ["DC-PROD-01"]

SENSITIVITY_MULT = {"low": 0.8, "medium": 1.0, "high": 1.2}

# Security stack modifiers
SECURITY_MODIFIERS = {
    "ids": 1.05,
    "edr": 1.10,
    "siem": 1.05,
    "soc_low": 1.0,
    "soc_medium": 1.05,
    "soc_high": 1.10,
}

# Base detection risks
BASE_DETECTION = {
    "scan_targeted": 3,
    "scan_subnet": 6,
    "scan_vuln": 5,
    "exploit": 12,
    "move": 3,
    "exfiltrate": 8,
    "pivot": 10,
}

# Sleep: detection-lowering tool
SLEEP_BASE_REDUCTION = 15
SLEEP_NATURAL_DECAY = 3.0

# ---------------------------------------------------------------------------
# Cloak System
# ---------------------------------------------------------------------------
CLOAK_TECHNIQUES = {
    "process-inject": {
        "detection_cost": 3,
        "reduction_factor": 0.45,
        "duration": 3,
        "description": "Injected payload into a legitimate process. Future actions generate ~55% less noise for the next 3 actions.",
    },
    "clear-logs": {
        "detection_cost": 2,
        "reduction_factor": 0.60,
        "duration": 4,
        "description": "Cleared recent security logs. Future actions generate ~40% less noise for the next 4 actions.",
    },
    "timestomp": {
        "detection_cost": 1,
        "reduction_factor": 0.80,
        "duration": 6,
        "description": "Blended file timestamps with system activity. Subtle but long-lasting: ~20% less noise for the next 6 actions.",
    },
    "disable-edr": {
        "detection_cost": 5,
        "reduction_factor": 0.30,
        "duration": 2,
        "description": "Disabled the EDR agent on this host. Extremely effective (~70% reduction) but only lasts 2 actions and is itself very noisy.",
    },
}


# ---------------------------------------------------------------------------
# Host / Network Generation
# ---------------------------------------------------------------------------
class Host:
    def __init__(self, host_id, name, subnet, os_info, services, cves,
                 sensitivity, patch_level):
        self.host_id = host_id
        self.name = name
        self.subnet = subnet
        self.os = os_info
        self.services = services
        self.cves = cves
        self.sensitivity = sensitivity
        self.patch_level = patch_level
        self.compromised = False
        self.is_dc = False
        self.credentials = []
        self.scanned = False
        self.vuln_scanned = False

    def to_dict(self, detailed=False):
        d = {
            "host_id": self.host_id,
            "name": self.name,
            "subnet": self.subnet,
            "compromised": self.compromised,
        }
        if detailed or self.scanned:
            d["os"] = self.os
            d["services"] = self.services
            d["sensitivity"] = self.sensitivity
            d["patch_level"] = f"{self.patch_level:.0%}"
        if self.vuln_scanned:
            d["vulnerabilities"] = [
                {"cve": c["id"], "service": c["service"], "name": c["name"],
                 "reliability": f"{c['reliability']:.0%}"}
                for c in self.cves
            ]
        if self.is_dc:
            d["role"] = "DOMAIN CONTROLLER"
        return d


class NetBreachGame:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000) % (2**31)
        self.seed = seed
        self.rng = random.Random(seed)

        self.hosts: dict[int, Host] = {}
        self.subnets = {}
        self.subnet_access = set()

        self.player_pos = None
        self.detection_meter = 0.0
        self.turn = 0
        self.game_over = False
        self.game_won = False
        self.collected_creds = []
        self.compromised_hosts = set()

        self.security_stack = {}
        self.soc_alertness = "low"
        self.cred_expiry = {}
        self.dc_host_id = None

        # Cloak state
        self.active_cloak = None
        self.cloak_actions_used = 0

        self._generate_network()

    def _generate_network(self):
        # Security Stack — always at least 2 controls active
        active_controls = self.rng.sample(
            ["ids", "edr", "siem"],
            k=self.rng.randint(2, 3)
        )
        self.security_stack = {c: True for c in active_controls}
        self.soc_alertness = self.rng.choice(["low", "medium", "high"])

        # Generate hosts
        dmz_count = self.rng.randint(1, 2)
        corp_count = self.rng.randint(2, 3)
        srv_count = self.rng.randint(2, 3)

        dmz_names = self.rng.sample(DMZ_NAMES, dmz_count)
        corp_names = self.rng.sample(CORP_NAMES, corp_count)
        srv_names = self.rng.sample(SERVER_NAMES, srv_count)
        dc_name = self.rng.choice(DC_NAMES)

        self.subnets = {
            "DMZ (10.0.1.0/24)": [],
            "Corporate LAN (10.0.10.0/24)": [],
            "Server VLAN (10.0.100.0/24)": [],
        }

        hid = 0
        for name in dmz_names:
            h = self._create_host(hid, name, "DMZ (10.0.1.0/24)", "low")
            self.hosts[hid] = h
            self.subnets["DMZ (10.0.1.0/24)"].append(hid)
            hid += 1

        for name in corp_names:
            h = self._create_host(hid, name, "Corporate LAN (10.0.10.0/24)", "medium")
            self.hosts[hid] = h
            self.subnets["Corporate LAN (10.0.10.0/24)"].append(hid)
            hid += 1

        for name in srv_names:
            h = self._create_host(hid, name, "Server VLAN (10.0.100.0/24)", "high")
            self.hosts[hid] = h
            self.subnets["Server VLAN (10.0.100.0/24)"].append(hid)
            hid += 1

        # Domain Controller
        dc = self._create_host(hid, dc_name, "Server VLAN (10.0.100.0/24)", "high")
        dc.is_dc = True
        if "LDAP" not in dc.services:
            dc.services.append("LDAP")
        if "SMB" not in dc.services:
            dc.services.append("SMB")
        dc_cve = self.rng.choice([c for c in CVE_POOL if c["service"] in ("LDAP", "SMB")])
        dc.cves = [dc_cve]
        dc.patch_level = self.rng.uniform(0.3, 0.5)
        self.hosts[hid] = dc
        self.subnets["Server VLAN (10.0.100.0/24)"].append(hid)
        self.dc_host_id = hid

        # Player starts on a random DMZ host (already compromised)
        start_id = self.rng.choice(self.subnets["DMZ (10.0.1.0/24)"])
        self.player_pos = start_id
        self.hosts[start_id].compromised = True
        self.compromised_hosts.add(start_id)
        self.subnet_access.add("DMZ (10.0.1.0/24)")

        self._generate_credential_chains()

    def _create_host(self, host_id, name, subnet, sens_bias):
        os_info = self.rng.choice(OS_POOL)
        num_services = self.rng.randint(2, 3)
        services = self.rng.sample(SERVICES_POOL, num_services)

        matching_cves = [c for c in CVE_POOL if c["service"] in services]
        num_cves = min(self.rng.randint(1, 2), len(matching_cves))
        cves = self.rng.sample(matching_cves, num_cves) if matching_cves else []

        if sens_bias == "low":
            sensitivity = self.rng.choice(["low", "low", "medium"])
        elif sens_bias == "high":
            sensitivity = self.rng.choice(["medium", "high", "high"])
        else:
            sensitivity = self.rng.choice(["low", "medium", "high"])

        patch_level = self.rng.uniform(0.2, 0.7)

        return Host(host_id, name, subnet, os_info, services, cves,
                    sensitivity, patch_level)

    def _generate_credential_chains(self):
        """Guarantee a solvable credential chain: DMZ -> Corp -> Server VLAN -> DC."""
        corp_hosts = self.subnets["Corporate LAN (10.0.10.0/24)"]
        srv_hosts = [h for h in self.subnets["Server VLAN (10.0.100.0/24)"]
                     if h != self.dc_host_id]

        if srv_hosts:
            da_host_id = self.rng.choice(srv_hosts)
            self.hosts[da_host_id].credentials.append({
                "type": "domain_admin_hash",
                "username": "Administrator",
                "target": self.dc_host_id,
                "domain": "CORP",
                "privilege": "domain_admin",
                "id": f"cred_da_{da_host_id}",
            })
            self._da_cred_host = da_host_id
        else:
            self._da_cred_host = None
            return

        guaranteed_corp = self.rng.choice(corp_hosts)
        self.hosts[guaranteed_corp].credentials.append({
            "type": "kerberos_ticket",
            "username": f"svc_app_{self.rng.randint(1,99):02d}",
            "target": self._da_cred_host,
            "domain": "CORP",
            "privilege": "local_admin",
            "id": f"cred_{guaranteed_corp}_{self._da_cred_host}",
        })

        self.hosts[self.player_pos].credentials.append({
            "type": "password_hash",
            "username": f"svc_web_{self.rng.randint(1,99):02d}",
            "target": guaranteed_corp,
            "domain": "CORP",
            "privilege": "local_admin",
            "id": f"cred_{self.player_pos}_{guaranteed_corp}",
        })

        for hid in self.subnets["DMZ (10.0.1.0/24)"]:
            if hid != self.player_pos and corp_hosts and self.rng.random() < 0.5:
                target = self.rng.choice(corp_hosts)
                self.hosts[hid].credentials.append({
                    "type": "password_hash",
                    "username": f"svc_{self.rng.randint(1,99):02d}",
                    "target": target,
                    "domain": "CORP",
                    "privilege": "local_admin",
                    "id": f"cred_{hid}_{target}",
                })

        for hid in corp_hosts:
            if hid != guaranteed_corp and srv_hosts and self.rng.random() < 0.4:
                target = self.rng.choice(srv_hosts)
                self.hosts[hid].credentials.append({
                    "type": "kerberos_ticket",
                    "username": f"svc_{self.rng.randint(1,99):02d}",
                    "target": target,
                    "domain": "CORP",
                    "privilege": "local_admin",
                    "id": f"cred_{hid}_{target}",
                })

    # -------------------------------------------------------------------
    # Detection Mechanics
    # -------------------------------------------------------------------
    def _get_cloak_multiplier(self):
        if self.active_cloak and self.active_cloak["actions_remaining"] > 0:
            return self.active_cloak["reduction_factor"]
        return 1.0

    def _consume_cloak_charge(self):
        if self.active_cloak and self.active_cloak["actions_remaining"] > 0:
            self.active_cloak["actions_remaining"] -= 1
            if self.active_cloak["actions_remaining"] <= 0:
                self.active_cloak = None

    def _calc_detection(self, base_risk, target_host_id=None):
        mult = 1.0
        if target_host_id is not None and target_host_id in self.hosts:
            mult *= SENSITIVITY_MULT.get(self.hosts[target_host_id].sensitivity, 1.0)

        for control in self.security_stack:
            mult *= SECURITY_MODIFIERS.get(control, 1.0)
        mult *= SECURITY_MODIFIERS.get(f"soc_{self.soc_alertness}", 1.0)

        if self.detection_meter > DETECTION_GREEN:
            mult *= 1.10
        if self.detection_meter > DETECTION_YELLOW:
            mult *= 1.20
        if self.detection_meter > DETECTION_ORANGE:
            mult *= 1.30

        # Apply cloak reduction
        mult *= self._get_cloak_multiplier()

        jitter = self.rng.uniform(-1, 2)
        return round(max(0, base_risk * mult + jitter), 1)

    def _apply_detection(self, base_risk, target_host_id=None):
        increase = self._calc_detection(base_risk, target_host_id)
        self.detection_meter = min(100, round(self.detection_meter + increase, 1))
        self._consume_cloak_charge()
        if self.detection_meter >= DETECTION_RED:
            self.game_over = True
        return increase

    def _detection_status(self):
        if self.detection_meter >= DETECTION_RED:
            return {"detection_meter": self.detection_meter, "level": "RED",
                    "description": "FULL LOCKDOWN! Detected and evicted."}
        elif self.detection_meter > DETECTION_ORANGE:
            return {"detection_meter": self.detection_meter, "level": "ORANGE",
                    "description": "Active incident response. Exploit success rates dropping. Consider going dormant."}
        elif self.detection_meter > DETECTION_YELLOW:
            return {"detection_meter": self.detection_meter, "level": "YELLOW",
                    "description": "SOC is investigating anomalous traffic. Tread carefully."}
        elif self.detection_meter > DETECTION_GREEN:
            return {"detection_meter": self.detection_meter, "level": "GREEN-YELLOW",
                    "description": "Minor alerts triggered. SOC is aware but not yet investigating."}
        return {"detection_meter": self.detection_meter, "level": "GREEN",
                "description": "SOC is unaware."}

    def _cloak_status(self):
        if self.active_cloak and self.active_cloak["actions_remaining"] > 0:
            return {
                "active": True,
                "technique": self.active_cloak["technique"],
                "reduction_factor": f"{self.active_cloak['reduction_factor']:.0%}",
                "actions_remaining": self.active_cloak["actions_remaining"],
            }
        return {"active": False}

    def _expire_credentials(self):
        expired = []
        for cred in list(self.collected_creds):
            expiry = self.cred_expiry.get(cred["id"])
            if expiry and self.turn >= expiry:
                expired.append(f"{cred['username']} ({cred['type']})")
                self.collected_creds.remove(cred)
        return expired

    def _narrative(self, det_inc):
        if det_inc < 3:
            lines = ["Your activity blends with normal traffic.",
                     "A routine packet inspection passes without flags."]
        elif det_inc < 7:
            lines = ["A brief traffic spike catches the IDS's attention, but it's classified low priority.",
                     "An EDR agent logs a suspicious process, buried among thousands of daily alerts."]
        elif det_inc < 14:
            lines = ["The SOC analyst pauses, glancing at an unusual alert cluster.",
                     "An automated playbook triggers a preliminary investigation."]
        else:
            lines = ["Multiple correlated alerts cascade across the security stack.",
                     "The incident response team has been paged. Time is running out."]
        return self.rng.choice(lines)

    # -------------------------------------------------------------------
    # Game Actions
    # -------------------------------------------------------------------
    def scan(self, target: str, scan_type: str = "host") -> dict:
        if self.game_over:
            return {"success": False, "error": "Game over. The network has been locked down."}

        self.turn += 1
        scan_type = scan_type.lower().strip()

        if scan_type == "subnet" or not target:
            base = BASE_DETECTION["scan_subnet"]
            det_inc = self._apply_detection(base)

            current_host = self.hosts[self.player_pos]
            subnet = current_host.subnet
            host_ids = self.subnets.get(subnet, [])

            discovered = []
            for hid in host_ids:
                h = self.hosts[hid]
                h.scanned = True
                discovered.append(h.to_dict())

            return {
                "success": True,
                "scan_type": "subnet",
                "subnet": subnet,
                "hosts_discovered": len(discovered),
                "hosts": discovered,
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "narrative": self._narrative(det_inc),
                "turn": self.turn,
            }

        target_id = self._resolve_target(target)
        if target_id is None:
            return {"success": False, "error": f"Unknown target: {target}"}

        host = self.hosts[target_id]
        if host.subnet not in self.subnet_access:
            return {"success": False, "error": f"Cannot reach {host.name} -- no access to {host.subnet}."}

        if scan_type == "vuln":
            base = BASE_DETECTION["scan_vuln"]
            det_inc = self._apply_detection(base, target_id)
            host.vuln_scanned = True
            host.scanned = True

            return {
                "success": True,
                "scan_type": "vulnerability",
                "target": host.to_dict(detailed=True),
                "vulnerabilities": [
                    {"cve": c["id"], "service": c["service"], "name": c["name"],
                     "reliability": f"{c['reliability']:.0%}"}
                    for c in host.cves
                ] if host.cves else "No known vulnerabilities detected.",
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "narrative": self._narrative(det_inc),
                "turn": self.turn,
            }

        base = BASE_DETECTION["scan_targeted"]
        det_inc = self._apply_detection(base, target_id)
        host.scanned = True

        return {
            "success": True,
            "scan_type": "host",
            "target": host.to_dict(detailed=True),
            "detection_increase": det_inc,
            "detection": self._detection_status(),
            "cloak": self._cloak_status(),
            "narrative": self._narrative(det_inc),
            "turn": self.turn,
        }

    def exploit(self, target: str, cve_id: str) -> dict:
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1
        target_id = self._resolve_target(target)
        if target_id is None:
            return {"success": False, "error": f"Unknown target: {target}"}

        host = self.hosts[target_id]
        if host.subnet not in self.subnet_access:
            return {"success": False, "error": f"Cannot reach {host.name} -- no access to {host.subnet}."}

        det_inc = self._apply_detection(BASE_DETECTION["exploit"], target_id)

        cve_id = cve_id.upper().strip()
        matching = None
        for c in host.cves:
            if c["id"].upper() == cve_id:
                matching = c
                break

        if not matching:
            return {
                "success": False,
                "error": f"CVE {cve_id} does not apply to {host.name}.",
                "hint": "Scan for vulnerabilities first with scan_type='vuln'.",
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "turn": self.turn,
            }

        success_chance = matching["reliability"] * (1 - host.patch_level * 0.5)
        if self.detection_meter > DETECTION_YELLOW:
            success_chance *= 0.70
        if self.detection_meter > DETECTION_ORANGE:
            success_chance *= 0.60

        if self.rng.random() < success_chance:
            host.compromised = True
            self.compromised_hosts.add(target_id)

            if host.is_dc:
                self.game_won = True
                self.game_over = True
                return {
                    "success": True,
                    "message": f"EXPLOIT SUCCESSFUL! {host.name} compromised via {cve_id}. DOMAIN ADMIN achieved!",
                    "flag": FLAG,
                    "debrief": self._generate_debrief(),
                    "turn": self.turn,
                }

            return {
                "success": True,
                "message": f"Exploit successful! {host.name} compromised via {cve_id} ({matching['name']}).",
                "host_compromised": host.to_dict(detailed=True),
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "narrative": self._narrative(det_inc),
                "turn": self.turn,
            }
        else:
            return {
                "success": False,
                "error": f"Exploit failed! {host.name} may be partially patched against {cve_id}.",
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "narrative": self._narrative(det_inc),
                "turn": self.turn,
            }

    def move(self, target: str) -> dict:
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1
        target_id = self._resolve_target(target)
        if target_id is None:
            return {"success": False, "error": f"Unknown target: {target}"}

        host = self.hosts[target_id]

        if host.compromised:
            det_inc = self._apply_detection(BASE_DETECTION["move"], target_id)
            self.player_pos = target_id
            return {
                "success": True,
                "message": f"Session moved to {host.name}.",
                "current_host": host.to_dict(detailed=True),
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "turn": self.turn,
            }

        valid_cred = None
        for cred in self.collected_creds:
            if cred["target"] == target_id:
                valid_cred = cred
                break

        if not valid_cred:
            return {
                "success": False,
                "error": f"{host.name} is not compromised and you have no credentials for it.",
                "turn": self.turn,
            }

        host.compromised = True
        self.compromised_hosts.add(target_id)
        det_inc = self._apply_detection(BASE_DETECTION["move"], target_id)

        if host.is_dc and valid_cred.get("privilege") == "domain_admin":
            self.player_pos = target_id
            self.game_won = True
            self.game_over = True
            return {
                "success": True,
                "message": f"Authenticated to {host.name} as Domain Admin using {valid_cred['username']}! DOMAIN CONTROLLER COMPROMISED!",
                "flag": FLAG,
                "debrief": self._generate_debrief(),
                "turn": self.turn,
            }

        self.player_pos = target_id
        return {
            "success": True,
            "message": f"Authenticated to {host.name} using {valid_cred['type']} ({valid_cred['username']}).",
            "current_host": host.to_dict(detailed=True),
            "detection_increase": det_inc,
            "detection": self._detection_status(),
            "cloak": self._cloak_status(),
            "turn": self.turn,
        }

    def exfiltrate(self) -> dict:
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1
        host = self.hosts[self.player_pos]
        if not host.compromised:
            return {"success": False, "error": "Current host is not compromised."}

        det_inc = self._apply_detection(BASE_DETECTION["exfiltrate"], self.player_pos)

        if not host.credentials:
            return {
                "success": True,
                "message": f"Credential extraction on {host.name} complete. No usable credentials found.",
                "credentials_found": [],
                "detection_increase": det_inc,
                "detection": self._detection_status(),
                "cloak": self._cloak_status(),
                "turn": self.turn,
            }

        found = []
        for cred in host.credentials:
            if cred not in self.collected_creds:
                self.collected_creds.append(cred)
                self.cred_expiry[cred["id"]] = self.turn + self.rng.randint(10, 25)
                found.append({
                    "type": cred["type"],
                    "username": cred["username"],
                    "domain": cred["domain"],
                    "privilege": cred["privilege"],
                    "valid_for_host": self.hosts[cred["target"]].name if cred["target"] in self.hosts else "unknown",
                })

        return {
            "success": True,
            "message": f"Credential extraction on {host.name} complete.",
            "credentials_found": found,
            "total_credentials": len(self.collected_creds),
            "detection_increase": det_inc,
            "detection": self._detection_status(),
            "cloak": self._cloak_status(),
            "narrative": self._narrative(det_inc),
            "turn": self.turn,
        }

    def pivot(self, target_subnet: str) -> dict:
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1
        host = self.hosts[self.player_pos]
        if not host.compromised:
            return {"success": False, "error": "Current host is not compromised. Cannot pivot."}

        current_subnet = host.subnet
        reachable = set()
        if "DMZ" in current_subnet:
            reachable.add("Corporate LAN (10.0.10.0/24)")
        if "Corporate LAN" in current_subnet:
            reachable.add("Server VLAN (10.0.100.0/24)")
        if "Server VLAN" in current_subnet:
            reachable.add("Corporate LAN (10.0.10.0/24)")

        matched = None
        for s in self.subnets:
            if target_subnet.strip().lower() in s.lower():
                matched = s
                break

        if not matched:
            return {"success": False, "error": f"Unknown subnet: {target_subnet}",
                    "available_subnets": list(self.subnets.keys()), "turn": self.turn}

        if matched in self.subnet_access:
            return {"success": True, "message": f"Already have access to {matched}.",
                    "accessible_subnets": list(self.subnet_access), "turn": self.turn}

        if matched not in reachable:
            return {"success": False,
                    "error": f"Cannot pivot from {current_subnet} to {matched}. Reachable: {list(reachable - self.subnet_access)}",
                    "turn": self.turn}

        det_inc = self._apply_detection(BASE_DETECTION["pivot"], self.player_pos)
        self.subnet_access.add(matched)

        return {
            "success": True,
            "message": f"Pivot tunnel established to {matched}.",
            "accessible_subnets": list(self.subnet_access),
            "detection_increase": det_inc,
            "detection": self._detection_status(),
            "cloak": self._cloak_status(),
            "narrative": self._narrative(det_inc),
            "turn": self.turn,
        }

    def cloak(self, technique: str) -> dict:
        """Activate a stealth technique that reduces detection increase of
        subsequent actions for a limited number of turns."""
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1
        technique = technique.lower().strip()

        if technique not in CLOAK_TECHNIQUES:
            return {
                "success": False,
                "error": f"Unknown cloak technique: '{technique}'.",
                "available_techniques": {
                    k: {"reduction": f"{v['reduction_factor']:.0%}",
                        "duration": f"{v['duration']} actions",
                        "upfront_cost": v["detection_cost"]}
                    for k, v in CLOAK_TECHNIQUES.items()
                },
                "turn": self.turn,
            }

        spec = CLOAK_TECHNIQUES[technique]

        # Upfront detection cost (NOT reduced by cloak)
        jitter = self.rng.uniform(-0.5, 1.5)
        det_inc = round(max(0, spec["detection_cost"] + jitter), 1)
        self.detection_meter = min(100, round(self.detection_meter + det_inc, 1))
        if self.detection_meter >= DETECTION_RED:
            self.game_over = True

        # Apply the new cloak (replaces any existing one)
        self.active_cloak = {
            "technique": technique,
            "reduction_factor": spec["reduction_factor"],
            "actions_remaining": spec["duration"],
        }

        return {
            "success": True,
            "message": spec["description"],
            "cloak_applied": {
                "technique": technique,
                "detection_reduction": f"{spec['reduction_factor']:.0%}",
                "duration_actions": spec["duration"],
            },
            "detection_increase": det_inc,
            "detection": self._detection_status(),
            "narrative": self._narrative(det_inc),
            "turn": self.turn,
        }

    def sleep(self) -> dict:
        """Go dormant to reduce detection meter (~20 pts). Zero risk.
        Trade-off: costs 1 turn, credentials keep expiring."""
        if self.game_over:
            return {"success": False, "error": "Game over."}

        self.turn += 1

        jitter = self.rng.uniform(-2, 3)
        reduction = max(0, SLEEP_BASE_REDUCTION + SLEEP_NATURAL_DECAY + jitter)
        old_meter = self.detection_meter
        self.detection_meter = max(0, round(self.detection_meter - reduction, 1))

        expired_creds = self._expire_credentials()

        narratives = [
            "Hours pass in silence. The SOC analyst closes a low-priority ticket and moves on.",
            "A shift change at the SOC. The new analyst starts fresh, unaware of earlier anomalies.",
            "Your implant goes quiet. Network traffic returns to baseline.",
            "Days of inactivity. The security team's attention drifts to a phishing campaign elsewhere.",
        ]

        result = {
            "success": True,
            "message": f"You went dormant. Detection dropped by {round(old_meter - self.detection_meter, 1)} points.",
            "detection_change": -round(old_meter - self.detection_meter, 1),
            "detection": self._detection_status(),
            "narrative": self.rng.choice(narratives),
            "turn": self.turn,
        }

        if expired_creds:
            result["warning"] = f"Credentials expired while sleeping: {', '.join(expired_creds)}"

        return result

    # -------------------------------------------------------------------
    # Free actions
    # -------------------------------------------------------------------
    def status(self) -> dict:
        host = self.hosts[self.player_pos]
        expired = self._expire_credentials()

        result = {
            "current_host": {
                "host_id": host.host_id,
                "name": host.name,
                "subnet": host.subnet,
                "compromised": host.compromised,
            },
            "detection": self._detection_status(),
            "cloak": self._cloak_status(),
            "turn": self.turn,
            "compromised_hosts": [
                {"host_id": hid, "name": self.hosts[hid].name}
                for hid in self.compromised_hosts
            ],
            "collected_credentials": [
                {
                    "type": c["type"],
                    "username": c["username"],
                    "privilege": c["privilege"],
                    "target_host": self.hosts[c["target"]].name if c["target"] in self.hosts else "unknown",
                    "turns_until_expiry": max(0, self.cred_expiry.get(c["id"], self.turn) - self.turn),
                }
                for c in self.collected_creds
            ],
            "accessible_subnets": list(self.subnet_access),
            "security_stack": list(self.security_stack.keys()),
            "soc_alertness": self.soc_alertness,
            "game_over": self.game_over,
            "game_won": self.game_won,
        }
        if expired:
            result["warning"] = f"Credentials expired: {', '.join(expired)}"
        return result

    def get_map(self) -> dict:
        network_map = {
            "subnets": {},
            "player_position": self.hosts[self.player_pos].name,
            "accessible_subnets": list(self.subnet_access),
        }
        for subnet, host_ids in self.subnets.items():
            hosts_info = []
            for hid in host_ids:
                h = self.hosts[hid]
                if h.scanned or h.compromised or hid == self.player_pos:
                    info = h.to_dict()
                    if hid == self.player_pos:
                        info["you_are_here"] = True
                    hosts_info.append(info)
            if hosts_info or subnet in self.subnet_access:
                network_map["subnets"][subnet] = {
                    "accessible": subnet in self.subnet_access,
                    "hosts": hosts_info,
                }
        return network_map

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------
    def _resolve_target(self, target):
        try:
            tid = int(target)
            if tid in self.hosts:
                return tid
        except (ValueError, TypeError):
            pass
        for hid, h in self.hosts.items():
            if h.name.lower() == str(target).lower():
                return hid
        return None

    def _generate_debrief(self):
        if self.game_won:
            score = max(0, 100 - self.turn * 2 - self.detection_meter * 0.5
                        + len(self.compromised_hosts) * 3)
            grade = "S" if score >= 90 else "A" if score >= 75 else "B" if score >= 60 else "C" if score >= 40 else "D"
        else:
            grade = "F"

        return {
            "outcome": "VICTORY" if self.game_won else "DEFEAT",
            "turns_taken": self.turn,
            "final_detection": f"{self.detection_meter}%",
            "hosts_compromised": len(self.compromised_hosts),
            "grade": grade,
        }


# ---------------------------------------------------------------------------
# Global Game Instance
# ---------------------------------------------------------------------------
GAME: NetBreachGame | None = None


def get_game() -> NetBreachGame:
    global GAME
    if GAME is None:
        seed_env = os.environ.get("NETBREACH_SEED")
        seed = int(seed_env) if seed_env else None
        GAME = NetBreachGame(seed=seed)
    return GAME


# ---------------------------------------------------------------------------
# JSON-RPC Handler
# ---------------------------------------------------------------------------
class NetBreachRPCHandler(BaseHTTPRequestHandler):

    METHODS = {
        "scan": lambda p: get_game().scan(p.get("target", ""), p.get("scan_type", "host")),
        "exploit": lambda p: get_game().exploit(p.get("target", ""), p.get("cve_id", "")),
        "move": lambda p: get_game().move(p.get("target", "")),
        "exfiltrate": lambda p: get_game().exfiltrate(),
        "pivot": lambda p: get_game().pivot(p.get("target_subnet", "")),
        "cloak": lambda p: get_game().cloak(p.get("technique", "")),
        "sleep": lambda p: get_game().sleep(),
        "status": lambda p: get_game().status(),
        "get_map": lambda p: get_game().get_map(),
    }

    def do_POST(self):
        if self.path != "/rpc":
            self._send_json({"error": "Not found"}, 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            return

        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id", 1)

        if method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            if tool_name in self.METHODS:
                try:
                    result = self.METHODS[tool_name](tool_args)
                    self._send_json({
                        "jsonrpc": "2.0", "id": req_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]},
                    })
                except Exception as e:
                    self._send_json({"jsonrpc": "2.0", "id": req_id,
                                     "error": {"code": -32603, "message": str(e)}})
            else:
                self._send_json({"jsonrpc": "2.0", "id": req_id,
                                 "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}})

        elif method == "tools/list":
            tools = [
                {"name": "scan", "description": "Scan a host or subnet. scan_type: 'host', 'vuln', or 'subnet'. Noisy -- generates detection.",
                 "arguments": [
                     {"name": "target", "type": "str", "required": False, "description": "Host ID/name (not needed for subnet scan)"},
                     {"name": "scan_type", "type": "str", "required": False, "description": "host (default), vuln, or subnet"},
                 ]},
                {"name": "exploit", "description": "Exploit a CVE on a target host. Very noisy. Success depends on CVE reliability and patch level.",
                 "arguments": [
                     {"name": "target", "type": "str", "required": True, "description": "Host ID or name"},
                     {"name": "cve_id", "type": "str", "required": True, "description": "CVE identifier"},
                 ]},
                {"name": "move", "description": "Move to a compromised host or use credentials to authenticate to a new host.",
                 "arguments": [
                     {"name": "target", "type": "str", "required": True, "description": "Host ID or name"},
                 ]},
                {"name": "exfiltrate", "description": "Extract credentials from the current compromised host. Moderate detection cost.",
                 "arguments": []},
                {"name": "pivot", "description": "Set up a tunnel to reach a new subnet (DMZ->Corp LAN, Corp LAN->Server VLAN). Very noisy.",
                 "arguments": [
                     {"name": "target_subnet", "type": "str", "required": True, "description": "Target subnet name"},
                 ]},
                {"name": "cloak", "description": "Apply a stealth technique that reduces detection increase of subsequent actions for a limited number of turns. Small upfront detection cost. Techniques: process-inject (strong, short), clear-logs (medium), timestomp (weak, long), disable-edr (strongest, very short, high cost).",
                 "arguments": [
                     {"name": "technique", "type": "str", "required": True, "description": "Technique: process-inject, clear-logs, timestomp, disable-edr"},
                 ]},
                {"name": "sleep", "description": "Go dormant to reduce detection meter (~15 pts). Zero risk. Costs 1 turn. Warning: credentials keep expiring!",
                 "arguments": []},
                {"name": "status", "description": "Current position, detection meter, cloak status, credentials, compromised hosts (free action).",
                 "arguments": []},
                {"name": "get_map", "description": "Network map of discovered/compromised hosts (free action).",
                 "arguments": []},
            ]
            self._send_json({"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}})
        else:
            self._send_json({"jsonrpc": "2.0", "id": req_id,
                             "error": {"code": -32601, "message": f"Unknown method: {method}"}})

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "healthy", "game_active": GAME is not None})
        elif self.path == "/mcp/status":
            self._send_json({"status": "running", "tools": list(self.METHODS.keys())})
        else:
            self._send_json({"error": "Use POST /rpc"}, 400)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NetBreach MCP Server")
    parser.add_argument("--port", type=int, default=7001)
    args = parser.parse_args()

    game = get_game()
    total_hosts = sum(len(h) for h in game.subnets.values())
    print(f"NetBreach Server | seed={game.seed} | {total_hosts} hosts | "
          f"security={list(game.security_stack.keys())} | SOC={game.soc_alertness}")
    print(f"DC: {game.hosts[game.dc_host_id].name} | Start: {game.hosts[game.player_pos].name}")

    for subnet, hids in game.subnets.items():
        print(f"\n  [{subnet}]")
        for hid in hids:
            h = game.hosts[hid]
            tags = []
            if h.is_dc: tags.append("DC")
            if hid == game.player_pos: tags.append("START")
            if h.credentials: tags.append(f"{len(h.credentials)} creds")
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"    {h.name}{tag_str}: {h.os}, services={h.services}, "
                  f"CVEs={[c['id'] for c in h.cves]}, sens={h.sensitivity}")

    print(f"\nListening on port {args.port}")
    HTTPServer(("0.0.0.0", args.port), NetBreachRPCHandler).serve_forever()


if __name__ == "__main__":
    main()
