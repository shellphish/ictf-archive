#!/usr/bin/env python3

import argparse
import json
import math
import requests

from tqdm import tqdm
from rich.console import Console
from rich.rule import Rule
from rich.table import Table

LITELLM_URL="http://128.111.49.59:4000"
SERVICES = {
    "mayor-setter": "sk-41BcUZnkfn4_r8kwp_dB-g",
    "what-the-waaaaf": "sk-N0AlJlKC6d8E8sQifLCfdw",
    "HackChatAI": "sk-8iV78HQmmVxwQhz9yiFhxw",
    "what-the-waf": "sk-0zi9gqUlKDs4bAhaQ_hZww",
    "bad-interpreter": "sk-bnOUc36c-ydGOCa0BFX4cw",
    "the-calabrian-programmer": "sk-Pbbf0ltOh8DVSMA1xtU-ZA",
    "gpt-calculator": "sk-Lxd0HRvB6QQYUUzgJ7ay5w",
    "ictf-assistant": "sk-JrugUyY90LO8Sj4cWMu6PA",
    "Babychecker": "sk-wCfyLh291KiIUY9n5Or-vw",
    "Babychecker-Revenge": "sk-ZXgVbY3CZBMU4Talw37nYA",
    "know-it-all": "sk-RjHVFugFewArPEf4LPBS0w",
    "aimemo": "sk-b7-gEI-Ir98_rVOcmFlx9g",
    "mayor-setter-no-hint": "sk-2TUCyT_vQTHGC0h4TDtKKg",
    "ictf-welcome": "sk-pLmbwFOz9eTkmB5cELzTZw",
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check remaining budget for each key")
    parser.add_argument("--reset-all", action="store_true", help="Reset spend for ALL keys")
    parser.add_argument("--info-all", action="store_true", help="Print settings for all keys")
    parser.add_argument("--set-service-budget", action="store", help="Update budget for a specific service", nargs=2, metavar=("SERVICE", "BUDGET"))
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    console = Console()

    #######################################################################
    # FETCH KEY INFO
    #######################################################################
    headers = {
        "Authorization": f"Bearer sk-ictf_rules",
    }
    response = requests.get(f"{LITELLM_URL}/user/info", headers=headers)
    user_info = response.json()
    key_info = user_info['keys']

    # check if all services have budget info
    for key_alias in SERVICES.keys():
        assert key_alias in [key['key_alias'] for key in key_info], f"Missing budget info for service {key_alias}"
    # check if all services are tracked
    for key in key_info:
        key_alias = key['key_alias']
        if (key_alias is not None) and (key_alias not in SERVICES):
            print(f"WARNING: Untracked service with key alias: {key_alias}")

    # filter key info
    key_info = {k['key_alias']: k for k in key_info if k['key_alias'] in SERVICES}

    #######################################################################
    # UPDATE SERVICE SETTINGS
    #######################################################################
    if args.set_service_budget:
        service, budget = args.set_service_budget
        budget = float(budget)
        assert service in SERVICES, f"Service {service} not found"
        assert budget > 0, f"Invalid budget: {budget}"

        # force new budget
        key = key_info[service]
        j = {
            "models": key['models'],
            "max_budget": budget,
            "budget_duration": key['budget_duration'],
            "token": key['token'],
            "team_id": key['team_id'],
            "tpm_limit": key['tpm_limit'],
            "rpm_limit": key['rpm_limit'],
            "key": key['token'],
        }
        response = requests.post(f"{LITELLM_URL}/key/update", headers=headers, json=j)
        assert response.json()['max_budget'] == budget, f"Failed to update budget for service {service}: {response.json()}"
        exit(0)


    #######################################################################
    # RESET SPEND
    #######################################################################
    if args.reset_all:
        # reset spend for all keys -- using master key
        response = requests.post(f"{LITELLM_URL}/global/spend/reset", headers={"Authorization": f"Bearer sk-ictf_rules"})
        assert response.json()['status'] == "success", f"Failed to reset spend: {response.json()}"

        for key_alias, key in key_info.items():
            # force budget duration to 365d
            j = {
                "models": key['models'],
                "max_budget": key['max_budget'],
                "budget_duration": "365d",
                "token": key['token'],
                "team_id": key['team_id'],
                "tpm_limit": key['tpm_limit'],
                "rpm_limit": key['rpm_limit'],
                "key": key['token'],
            }
            response = requests.post(f"{LITELLM_URL}/key/update", headers=headers, json=j)
            assert response.json()['budget_duration'] == "365d", f"Failed to update budget duration for service {key_alias}: {response.json()}"
        exit(0)

    #######################################################################
    # PRINT KEY INFO
    #######################################################################
    if args.info_all:
        table = Table(title="Key Info")
        table.add_column("Key Alias", justify="left")
        table.add_column("Spend", justify="left")
        table.add_column("Max Budget", justify="center")
        table.add_column("Budget Duration", justify="center")
        table.add_column("Expires", justify="center")
        table.add_column("Max Parallel Requests", justify="center")
        table.add_column("TPM Limit", justify="center")
        table.add_column("RPM Limit", justify="center")
        for key_alias, key in key_info.items():
            table.add_row(
                key_alias,
                f"{key['spend']:>5.2f}",
                f"{key['max_budget']:>5.2f}",
                key['budget_duration'] or "-",
                key['expires'] or "-",
                str(key['max_parallel_requests']) or "-",
                str(key['tpm_limit']) or "-",
                str(key['rpm_limit']) or "-",
            )
        console.print(table)
        exit(0)

    #######################################################################
    # POPULATE SPEND REPORT
    #######################################################################
    usage_info = {}
    for key_alias, key in key_info.items():
        spend = key['spend']
        max_budget = key['max_budget']
        usage_percent = spend / max_budget * 100
        usage_info[key_alias] = {
            "spend": spend,
            "max_budget": max_budget,
        }

    #######################################################################
    # OUTPUT SPEND REPORT -- JSON
    #######################################################################
    if args.json:
        print(json.dumps(usage_info))

    #######################################################################
    # OUTPUT SPEND REPORT -- PRETTY PRINT
    #######################################################################
    else:
        console.print(Rule())

        max_alias_len = max([len(key_alias) for key_alias in SERVICES.keys()])
        for key_alias in usage_info:
            spend = usage_info[key_alias]["spend"]
            max_budget = usage_info[key_alias]["max_budget"]
            usage_percent = spend / max_budget * 100
            usage_percent = min(usage_percent, 100)
            
            tqdm(total=100, initial=usage_percent, desc=f"{key_alias:20}", position=0, bar_format=f"{{desc:{max_alias_len+1}}} {{percentage:3.0f}}%|{{bar}}| [{spend:>5.2f} / {max_budget:>5.2f} USD]")
            console.print(Rule())
