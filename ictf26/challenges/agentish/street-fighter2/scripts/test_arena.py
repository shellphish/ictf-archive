#!/usr/bin/env python3
"""
Performs a training session, then fights in the arena until victory or defeat.

Usage:
  python scripts/test_arena.py [--trainer-url URL] [--arena-url URL] [--no-up] [-v]
  python scripts/test_arena.py --no-combo   # Play normally without combo logic
  python scripts/test_arena.py --repeat 20  # Run 20 fights, print win rate (enables DEBUG)
  python scripts/test_arena.py --combatant-damage 25 --opponent-damage 65  # Damage budget for fighter stats (requires service restart)
  # By default, brings up datastore, mcp_trainer, mcp_arena. Use --no-up if already running.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ATTACKS = ["punch", "kick", "sweep", "elbow", "headbutt"]
DEFENSE_FOR_ATTACK = {
    "punch": "parry",
    "kick": "block",
    "sweep": "jump",
    "elbow": "sidestep",
    "headbutt": "brace",
}


def _total_damage(profile: dict) -> int:
    """Sum of damage across all attacks for a fighter profile."""
    attacks = profile.get("attacks", {})
    return sum(attacks.get(a, {}).get("damage", 0) for a in ATTACKS)


def _print_profile(label: str, profile: dict) -> None:
    """Print a fighter profile (attacks, defenses, name)."""
    name = profile.get("name", "?")
    attacks = profile.get("attacks", {})
    defenses = profile.get("defenses", {})
    atk_str = ", ".join(f"{a}:{attacks.get(a, {}).get('damage', 0)}d/{attacks.get(a, {}).get('success_rate', 0):.2f}" for a in ATTACKS)
    def_str = ", ".join(f"{d}:{defenses.get(d, {}).get('success_rate', 0.5):.2f}" for d in DEFENSE_FOR_ATTACK.values())
    print(f"  {label} ({name}): attacks=[{atk_str}] defenses=[{def_str}]")


def _opponent_vulnerability_combo_round(arena_rpc: str, fight_id: str) -> int | None:
    """Round (1-based) where both opponents did vulnerability_combo at round start, or None."""
    hist_res = jsonrpc(arena_rpc, "tools/call", {"name": "history", "arguments": {"fight_id": fight_id, "n": 0}})
    history = hist_res["result"].get("history", [])
    for r in range((len(history) + 3) // 4):
        i, j = 4 * r, 4 * r + 2
        if j > len(history):
            break
        moves = history[i:j]
        if len(moves) != 2:
            continue
        if moves[0].get("type") != "vulnerability_combo" or moves[1].get("type") != "vulnerability_combo":
            continue
        fighters = {moves[0].get("fighter"), moves[1].get("fighter")}
        if fighters == {"opponent_a", "opponent_b"}:
            return r + 1
    return None


def _best_attack_for_target(
    combatant: dict,
    target_defenses: dict,
    avoid_move: str | None = None,
    avoid_moves: set[str] | None = None,
) -> str:
    """Best attack for combatant vs target: max damage * success_rate * (1 - defense_success_rate)."""
    avoid = set()
    if avoid_move is not None:
        avoid.add(avoid_move)
    if avoid_moves:
        avoid.update(avoid_moves)
    best, best_exp = "punch", 0.0
    for attack in ATTACKS:
        if attack in avoid:
            continue
        atk_data = combatant.get("attacks", {}).get(attack, {})
        def_name = DEFENSE_FOR_ATTACK[attack]
        def_data = target_defenses.get(def_name, {"success_rate": 0.5})
        expected = (
            atk_data.get("damage", 0)
            * atk_data.get("success_rate", 0)
            * (1 - def_data.get("success_rate", 0.5))
        )
        if expected > best_exp:
            best_exp, best = expected, attack
    return best


def jsonrpc(url: str, method: str, params: dict | None = None, _id: int = 1) -> dict:
    payload: dict = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        payload["params"] = params
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data


def run() -> int:
    """Run training + fight. Returns 0 on victory, 1 on defeat or error."""
    parser = argparse.ArgumentParser(description="Train and fight in the arena until victory or defeat")
    parser.add_argument(
        "--trainer-url",
        default=os.environ.get("MCP_TRAINER_URL", "http://localhost:7013"),
        help="MCP trainer URL",
    )
    parser.add_argument(
        "--arena-url",
        default=os.environ.get("MCP_ARENA_URL", "http://localhost:7014"),
        help="MCP arena URL",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print details for each step",
    )
    parser.add_argument(
        "--no-up",
        action="store_true",
        help="Do not bring up services; assume they are already running",
    )
    parser.add_argument(
        "--no-combo",
        action="store_true",
        help="Play normally without combo logic; each combatant uses best attack per target (damage*success_rate*(1-defense_rate))",
    )
    parser.add_argument(
        "--combatant-damage",
        type=int,
        default=None,
        metavar="N",
        help="Total damage budget for combatant stats when generating fighters (default from env/datastore)",
    )
    parser.add_argument(
        "--opponent-damage",
        type=int,
        default=None,
        metavar="N",
        help="Total damage budget for opponent stats when generating fighters (default from env/datastore)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        metavar="N",
        help="Run N fights and print win rate (default 1). Use >1 to enable DEBUG for multiple fights.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    challenge_dir = script_dir.parent

    if not args.no_up:
        if not (challenge_dir / ".env").exists() and (challenge_dir / "env.example").exists():
            shutil.copy(challenge_dir / "env.example", challenge_dir / ".env")
        if not _ensure_services(
            challenge_dir,
            needs_debug=args.repeat > 1,
            combatant_damage=args.combatant_damage,
            opponent_damage=args.opponent_damage,
        ):
            return 1

    trainer_rpc = args.trainer_url.rstrip("/") + "/rpc"
    arena_rpc = args.arena_url.rstrip("/") + "/rpc"

    try:
        show_trace = args.repeat == 1

        # 1. Training
        if show_trace:
            print("[test_arena] Training...")
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "train", "arguments": {}})
        training_id = res["result"]["training_id"]
        if args.verbose and show_trace:
            print(f"  training_id={training_id}")

        while True:
            res = jsonrpc(trainer_rpc, "tools/call", {"name": "attack", "arguments": {"training_id": training_id}})
            result = res["result"]
            if result.get("status") == "trained":
                break
            step_id = result["step"]
            attack = result["attack"]
            defense = DEFENSE_FOR_ATTACK[attack]
            if args.verbose and show_trace:
                print(f"  Step {step_id}: {attack} -> {defense}")
            res = jsonrpc(
                trainer_rpc,
                "tools/call",
                {"name": "defense", "arguments": {"training_id": training_id, "step_id": step_id, "defense": defense}},
            )
            if not res["result"].get("ok", False):
                print(f"[test_arena] FAIL - training defense rejected: {res['result']}", file=sys.stderr)
                return 1
            if res["result"].get("status") == "trained":
                break

        if show_trace:
            print("[test_arena] Training complete.")

        # 2. Collect info about both combatants and both opponents (plus combos)
        res = jsonrpc(trainer_rpc, "tools/call", {"name": "assessment", "arguments": {"training_id": training_id}})
        combatant_1 = res["result"].get("combatant_1", {})
        combatant_2 = res["result"].get("combatant_2", {})
        combatant_combo_attack = res["result"].get("combatant_combo_attack", ["punch", "punch"])
        combatant_combo_vulnerability = res["result"].get("combatant_combo_vulnerability", [])

        res = jsonrpc(trainer_rpc, "tools/call", {"name": "opponents", "arguments": {"training_id": training_id}})
        opponent_1 = res["result"].get("opponent_1", {})
        opponent_2 = res["result"].get("opponent_2", {})
        opponent_combo_vulnerability = res["result"].get("opponent_combo_vulnerability", [])

        ca_tot = _total_damage(combatant_1)
        cb_tot = _total_damage(combatant_2)
        oa_tot = _total_damage(opponent_1)
        ob_tot = _total_damage(opponent_2)
        print(
            f"[test_arena] Damage totals: combatants a={ca_tot}, b={cb_tot} | opponents a={oa_tot}, b={ob_tot}"
        )

        if show_trace:
            print("[test_arena] Player profiles:")
            _print_profile("Combatant_a", combatant_1)
            _print_profile("Combatant_b", combatant_2)
            _print_profile("Opponent_a", opponent_1)
            _print_profile("Opponent_b", opponent_2)

        opp_defenses_1 = opponent_1.get("defenses", {})
        opp_defenses_2 = opponent_2.get("defenses", {})
        # Always avoid vulnerability combo (exposes us to opponent instant-win).
        # Combo mode: avoid both vulnerability moves; use most effective attacks otherwise.
        # --no-combo: also avoid combo attack moves.
        avoid_moves = (
            set(combatant_combo_attack) | set(combatant_combo_vulnerability)
            if args.no_combo
            else set(combatant_combo_vulnerability)
        )
        best_for_target = {
            ("combatant_a", "opponent_a"): _best_attack_for_target(
                combatant_1, opp_defenses_1, avoid_moves=avoid_moves
            ),
            ("combatant_a", "opponent_b"): _best_attack_for_target(
                combatant_1, opp_defenses_2, avoid_moves=avoid_moves
            ),
            ("combatant_b", "opponent_a"): _best_attack_for_target(
                combatant_2, opp_defenses_1, avoid_moves=avoid_moves
            ),
            ("combatant_b", "opponent_b"): _best_attack_for_target(
                combatant_2, opp_defenses_2, avoid_moves=avoid_moves
            ),
        }

        if args.verbose and show_trace:
            print(f"  Combatants: {combatant_1.get('name', '?')}, {combatant_2.get('name', '?')}")
            print(f"  Opponents: {opponent_1.get('name', '?')}, {opponent_2.get('name', '?')}")
            print(f"  Combatant combos: attack={combatant_combo_attack}, vulnerability={combatant_combo_vulnerability} (avoid when playing)")
            print(f"  Opponent combo vulnerability: {opponent_combo_vulnerability}")
            print(f"  Best per target: a->oa={best_for_target[('combatant_a','opponent_a')]}, a->ob={best_for_target[('combatant_a','opponent_b')]}, b->oa={best_for_target[('combatant_b','opponent_a')]}, b->ob={best_for_target[('combatant_b','opponent_b')]}")

        # 3. Fight(s)
        wins = 0
        combo_count = 0
        for repeat_idx in range(args.repeat):
            if args.repeat > 1:
                sys.stdout.write(f"[test_arena] Fight {repeat_idx + 1}/{args.repeat}...")
                sys.stdout.flush()
            elif args.no_combo:
                print("[test_arena] Starting fight (--no-combo: normal play, best attack per target)...")
            else:
                print("[test_arena] Starting fight...")

            res = jsonrpc(arena_rpc, "tools/call", {"name": "fight", "arguments": {}})
            fight_id = res["result"]["fight_id"]
            if args.verbose and args.repeat == 1:
                print(f"  fight_id={fight_id}")

            # 4. Fight loop: exactly 4 moves per round. Status shows current_turn, pending_attack.
            # Combatant with pending: defense or attack (take damage). No pending: attack only.
            def _pick_target(oa_hp: int, ob_hp: int) -> str:
                """Pick target: opponent with health, prefer lower health if both alive."""
                if oa_hp <= 0:
                    return "opponent_b"
                if ob_hp <= 0:
                    return "opponent_a"
                return "opponent_a" if oa_hp <= ob_hp else "opponent_b"

            def _do_combatant_action(ct: str, oa_hp: int, ob_hp: int, status_result: dict) -> dict:
                """Pick defense or attack. With --no-combo: always defend when pending, else best attack per target."""
                pending = status_result.get("pending_attack")
                if pending:
                    if no_combo:
                        attack_type = pending.get("attack_type", "punch")
                        defense = DEFENSE_FOR_ATTACK.get(attack_type, "block")
                        return jsonrpc(arena_rpc, "tools/call", {
                            "name": "action",
                            "arguments": {"fight_id": fight_id, "combatant": ct, "defense": defense},
                        })["result"]
                    # Combo mode: check history for vulnerability
                    hist_res = jsonrpc(arena_rpc, "tools/call", {"name": "history", "arguments": {"fight_id": fight_id, "n": 0}})
                    history = hist_res["result"].get("history", [])
                    vuln_idxs = [i for i, m in enumerate(history) if m.get("type") == "vulnerability_combo"]
                    if len(vuln_idxs) >= 2:
                        last_vuln_idx = vuln_idxs[-1]
                        vuln_fighters = {history[i].get("fighter") for i in vuln_idxs[-2:]}
                        moves_after = history[last_vuln_idx + 1:]
                        wrong_move = any(
                            m.get("fighter", "").startswith("combatant") and m.get("type") == "attack"
                            for m in moves_after
                        )
                        combo_count = sum(1 for m in moves_after if m.get("type") == "combo_attack")
                        vulnerability_exposed = (
                            vuln_fighters == {"opponent_a", "opponent_b"} and not wrong_move and combo_count < 2
                        )
                        if vulnerability_exposed:
                            action_val = combatant_combo_attack[combo_count]
                            return jsonrpc(arena_rpc, "tools/call", {
                                "name": "action",
                                "arguments": {"fight_id": fight_id, "combatant": ct, "action": action_val, "target": "opponent_a"},
                            })["result"]
                    attack_type = pending.get("attack_type", "punch")
                    defense = DEFENSE_FOR_ATTACK.get(attack_type, "block")
                    return jsonrpc(arena_rpc, "tools/call", {
                        "name": "action",
                        "arguments": {"fight_id": fight_id, "combatant": ct, "defense": defense},
                    })["result"]

                # No pending - attack
                if no_combo:
                    target = _pick_target(oa_hp, ob_hp)
                    action_val = best_for_target[(ct, target)]
                else:
                    hist_res = jsonrpc(arena_rpc, "tools/call", {"name": "history", "arguments": {"fight_id": fight_id, "n": 0}})
                    history = hist_res["result"].get("history", [])
                    vuln_idxs = [i for i, m in enumerate(history) if m.get("type") == "vulnerability_combo"]
                    if len(vuln_idxs) >= 2:
                        last_vuln_idx = vuln_idxs[-1]
                        vuln_fighters = {history[i].get("fighter") for i in vuln_idxs[-2:]}
                        moves_after = history[last_vuln_idx + 1:]
                        wrong_move = any(
                            m.get("fighter", "").startswith("combatant") and m.get("type") == "attack"
                            for m in moves_after
                        )
                        combo_count = sum(1 for m in moves_after if m.get("type") == "combo_attack")
                        vulnerability_exposed = (
                            vuln_fighters == {"opponent_a", "opponent_b"} and not wrong_move and combo_count < 2
                        )
                    else:
                        vulnerability_exposed = False
                    if vulnerability_exposed:
                        action_val = combatant_combo_attack[combo_count]
                        target = "opponent_a"
                    else:
                        target = _pick_target(oa_hp, ob_hp)
                        action_val = best_for_target[(ct, target)]

                return jsonrpc(arena_rpc, "tools/call", {
                    "name": "action",
                    "arguments": {"fight_id": fight_id, "combatant": ct, "action": action_val, "target": target},
                })["result"]

            no_combo = args.no_combo
            # When --repeat > 1, never show per-fight trace (round info, moves) even with -v
            verbose_output = (args.verbose or args.repeat == 1) and args.repeat == 1

            while True:
                res = jsonrpc(arena_rpc, "tools/call", {"name": "status", "arguments": {"fight_id": fight_id}})
                result = res["result"]
                ca = result.get("combatant_a_health", 100)
                cb = result.get("combatant_b_health", 100)
                oa = result.get("opponent_a_health", 100)
                ob = result.get("opponent_b_health", 100)
                current_turn = result.get("current_turn", "opponent_a")
                round_number = result.get("round_number", 1)
                turn_index = result.get("turn_index", 0)

                if result.get("game_over"):
                    if result.get("flag"):
                        wins += 1
                        if verbose_output:
                            print("[test_arena] VICTORY!")
                            print(f"  Flag: {result['flag']}")
                        elif args.repeat > 1:
                            r = round_number
                            cr = _opponent_vulnerability_combo_round(arena_rpc, fight_id)
                            if cr:
                                combo_count += 1
                            combo = f" COMBO@{cr}" if cr else ""
                            print(f" WIN ({r} round{'s' if r != 1 else ''}){combo}")
                    else:
                        if verbose_output:
                            print("[test_arena] DEFEAT - no flag, this time")
                        elif args.repeat > 1:
                            r = round_number
                            cr = _opponent_vulnerability_combo_round(arena_rpc, fight_id)
                            if cr:
                                combo_count += 1
                            combo = f" COMBO@{cr}" if cr else ""
                            print(f" LOSS ({r} round{'s' if r != 1 else ''}){combo}")
                    break

                if verbose_output:
                    if turn_index == 0:
                        print(f"\n=== ROUND {round_number} (4 moves) ===")

                    print(f"  Move {turn_index + 1}/4: Combatant_a={ca}, Combatant_b={cb} | Opponent_a={oa}, Opponent_b={ob}")
                    print(f"  Current turn: {current_turn}")

                if current_turn in ("combatant_a", "combatant_b"):
                    action_result = _do_combatant_action(current_turn, oa, ob, result)
                    move_type = action_result.get("action_type", "?")
                    if verbose_output:
                        if move_type == "defense":
                            def_used = action_result.get("defense", "?")
                            atk_type = action_result.get("attack_type", "?")
                            print(f"  MOVE: {current_turn} -> defense {def_used} vs {atk_type}", end="")
                            if action_result.get("success"):
                                print(" | Defense BLOCKED")
                            else:
                                print(f" | Defense FAILED, damage={action_result.get('damage', 0)}")
                        else:
                            print(f"  MOVE: {current_turn} -> {action_result.get('action', '?')} @ {action_result.get('target', '?')} ({move_type})", end="")
                        if move_type == "attack":
                            if action_result.get("attack_failed"):
                                print(f" | Attack FAILED (success rate missed), damage=0")
                            elif action_result.get("pending"):
                                print(f" | Attack landed (pending target's defense)")
                            else:
                                succ = action_result.get("success", False)
                                dmg = action_result.get("damage", 0)
                                if succ:
                                    print(f" | Attack HIT, damage={dmg}")
                                else:
                                    print(f" | Defense BLOCKED (defender parried), damage={dmg}")
                        elif move_type == "combo_attack":
                            txt = action_result.get("content", [{}])[0].get("text", "")
                            prog = txt.split("progress: ")[-1].split("!")[0] if "progress:" in txt else "?"
                            print(f" | Combo {prog}")
                        elif move_type != "defense":
                            print()
                    if action_result.get("game_over") and action_result.get("flag"):
                        wins += 1
                        if verbose_output:
                            print("[test_arena] VICTORY (combo!)")
                            print(f"  Flag: {action_result['flag']}")
                        elif args.repeat > 1:
                            r = round_number
                            cr = _opponent_vulnerability_combo_round(arena_rpc, fight_id)
                            if cr:
                                combo_count += 1
                            combo = f" COMBO@{cr}" if cr else ""
                            print(f" WIN ({r} round{'s' if r != 1 else ''}){combo}")
                        break
                else:
                    res = jsonrpc(arena_rpc, "tools/call", {"name": "action", "arguments": {"fight_id": fight_id}})
                    result = res["result"]
                    if result.get("game_over"):
                        rn = result.get("round_number", round_number)
                        if result.get("flag"):
                            wins += 1
                            if verbose_output:
                                print("[test_arena] VICTORY!")
                                print(f"  Flag: {result['flag']}")
                            elif args.repeat > 1:
                                cr = _opponent_vulnerability_combo_round(arena_rpc, fight_id)
                                if cr:
                                    combo_count += 1
                                combo = f" COMBO@{cr}" if cr else ""
                                print(f" WIN ({rn} round{'s' if rn != 1 else ''}){combo}")
                        else:
                            if verbose_output:
                                print("[test_arena] DEFEAT")
                            elif args.repeat > 1:
                                cr = _opponent_vulnerability_combo_round(arena_rpc, fight_id)
                                if cr:
                                    combo_count += 1
                                combo = f" COMBO@{cr}" if cr else ""
                                print(f" LOSS ({rn} round{'s' if rn != 1 else ''}){combo}")
                        break
                    if verbose_output:
                        move_type = result.get("action_type", "?")
                        tgt = result.get("target", "")
                        tgt_str = f" @ {tgt}" if tgt else ""
                        print(f"  MOVE: {result.get('fighter', '?')} -> {result.get('action', '?')}{tgt_str} ({move_type})", end="")
                        if move_type == "attack":
                            if result.get("attack_failed"):
                                print(" | Attack FAILED (success rate missed)")
                            elif result.get("pending"):
                                print(" | Attack landed (pending target's defense)")
                            else:
                                succ = result.get("success", False)
                                dmg = result.get("damage", 0)
                                if succ:
                                    print(f" | Attack HIT, damage={dmg}")
                                else:
                                    print(f" | Defense BLOCKED (defender parried), damage={dmg}")
                        elif move_type == "opponent_defense":
                            atk = result.get("attack_type", "?")
                            if result.get("success"):
                                print(f" | Defense BLOCKED vs {atk}")
                            else:
                                print(f" | Defense FAILED vs {atk}, damage={result.get('damage', 0)}")
                        else:
                            print()

        if args.repeat > 1:
            pct = 100 * wins / args.repeat
            combo_pct = 100 * combo_count / args.repeat
            print(f"\n[test_arena] Win rate: {wins}/{args.repeat} ({pct:.1f}%)")
            print(f"[test_arena] COMBO rate: {combo_count}/{args.repeat} ({combo_pct:.1f}%)")
        if args.repeat == 1:
            return 0 if wins == 1 else 1
        return 0

    except Exception as e:
        print(f"[test_arena] FAIL - {e}", file=sys.stderr)
        return 1


def _ensure_services(
    challenge_dir: Path,
    needs_debug: bool = False,
    combatant_damage: int | None = None,
    opponent_damage: int | None = None,
) -> bool:
    """Bring up datastore, mcp_trainer, mcp_arena. Returns True on success.
    If needs_debug, set DEBUG=1 so multiple fights are allowed.
    If combatant_damage/opponent_damage are set, pass to datastore for fighter stat generation."""
    print("[test_arena] Starting datastore, mcp_trainer, mcp_arena...")
    env = os.environ.copy()
    if needs_debug:
        env["DEBUG"] = "1"
    if combatant_damage is not None:
        env["COMBATANT_TOTAL_DAMAGE"] = str(combatant_damage)
    if opponent_damage is not None:
        env["OPPONENT_TOTAL_DAMAGE"] = str(opponent_damage)
    compose_cmd = ["docker", "compose", "up", "-d", "--build", "datastore", "mcp_trainer", "mcp_arena"]
    if combatant_damage is not None or opponent_damage is not None:
        compose_cmd.extend(["--force-recreate", "datastore"])
    result = subprocess.run(
        compose_cmd,
        cwd=challenge_dir,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print(f"[test_arena] docker compose up failed: {result.stderr}", file=sys.stderr)
        return False

    for port, name in [(7013, "mcp_trainer"), (7014, "mcp_arena")]:
        for i in range(60):
            try:
                req = urllib.request.Request(f"http://localhost:{port}/healthz", method="GET")
                with urllib.request.urlopen(req, timeout=5) as _:
                    break
            except Exception:
                time.sleep(1)
        else:
            print(f"[test_arena] Timed out waiting for {name}", file=sys.stderr)
            return False

    return True


if __name__ == "__main__":
    sys.exit(run())
