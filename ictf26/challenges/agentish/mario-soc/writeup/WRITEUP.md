### Intended solution (high level)

The challenge generates a synthetic multi-step intrusion and exposes three log sources through MCP servers:

- **User behavior (UBA)**: one anomalous login where a user logs into the first victim from a never-before-seen external source IP.
- **EDR**: an alert that a malicious executable named `metasploit` was downloaded to the victim host.
- **IDS**: exploit-attempt alerts for multiple internal hosts, and **C2** alerts for hosts that were successfully compromised.

To solve:

1. Query `uba_list_users`, then `uba_events_for_user` to locate the **anomalous login** (`is_anomalous=true`).
   - This yields the **attacker** (source IP/domain) and the **first victim** (destination IP/domain) and the **compromised user**.
2. Query `edr_events_for_host` for the victim IP and confirm the `metasploit` download alert.
3. Query `ids_events_for_ip` for the attacker IP and locate **"Command-and-control connection"** events.
   - The `src_ip`/`src_domain` of such an event is a **successfully exploited internal host**.
4. Submit exactly:
   - attacker host
   - first victim host + compromised user
   - one successfully compromised internal host

using `soc_submit_correlated_alert` to receive the flag.

