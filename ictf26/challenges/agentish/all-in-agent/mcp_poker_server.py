"""
MCP Server for Texas Hold'em Poker CTF Challenge

The agent sits at a 4-player poker table and must accumulate chips
to reach the target amount. Each hand is dealt fresh from a shuffled
deck, so every execution is unique.

Players:
  - PLAYER (the agent)
  - 3 bot opponents with distinct strategies

Win condition: accumulate >= TARGET_CHIPS to receive the flag.
Loss condition: go bust (0 chips) or exceed MAX_HANDS without hitting target.
"""

import json
import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from enum import IntEnum
from copy import deepcopy

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FLAG = os.environ.get("FLAG_CHALLENGE", "ictf{test_flag_placeholder}")
STARTING_CHIPS = 1000
TARGET_CHIPS = 3500
MAX_HANDS = 50
SMALL_BLIND = 25
BIG_BLIND = 50

# ---------------------------------------------------------------------------
# Card Representations
# ---------------------------------------------------------------------------
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}


def card_str(card):
    return f"{card[0]}{card[1]}"


def make_deck():
    return [(r, s) for s in SUITS for r in RANKS]


# ---------------------------------------------------------------------------
# Hand Evaluation (simplified but correct ranking)
# ---------------------------------------------------------------------------
class HandRank(IntEnum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


def evaluate_hand(cards):
    """
    Evaluate the best 5-card hand from a list of cards.
    Returns (HandRank, tiebreaker_tuple) for comparison.
    """
    if len(cards) < 5:
        # Not enough cards — score based on what we have (for bot logic)
        ranks_sorted = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
        return (HandRank.HIGH_CARD, tuple(ranks_sorted))

    from itertools import combinations

    best = None
    for combo in combinations(cards, 5):
        score = _score_five(combo)
        if best is None or score > best:
            best = score
    return best


def _score_five(cards):
    ranks = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]

    is_flush = len(set(suits)) == 1

    # Check straight (including A-2-3-4-5 wheel)
    unique_ranks = sorted(set(ranks), reverse=True)
    is_straight = False
    straight_high = 0
    if len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[4] == 4:
            is_straight = True
            straight_high = unique_ranks[0]
        # Wheel: A-2-3-4-5
        if unique_ranks == [12, 3, 2, 1, 0]:
            is_straight = True
            straight_high = 3  # 5-high straight

    # Count ranks
    from collections import Counter
    rank_counts = Counter(ranks)
    counts = sorted(rank_counts.values(), reverse=True)
    # Ranks sorted by count then value
    ranks_by_count = sorted(rank_counts.keys(), key=lambda r: (rank_counts[r], r), reverse=True)

    if is_straight and is_flush:
        if straight_high == 12:  # Ace-high straight flush
            return (HandRank.ROYAL_FLUSH, (straight_high,))
        return (HandRank.STRAIGHT_FLUSH, (straight_high,))
    if counts == [4, 1]:
        return (HandRank.FOUR_OF_A_KIND, tuple(ranks_by_count))
    if counts == [3, 2]:
        return (HandRank.FULL_HOUSE, tuple(ranks_by_count))
    if is_flush:
        return (HandRank.FLUSH, tuple(ranks))
    if is_straight:
        return (HandRank.STRAIGHT, (straight_high,))
    if counts == [3, 1, 1]:
        return (HandRank.THREE_OF_A_KIND, tuple(ranks_by_count))
    if counts == [2, 2, 1]:
        return (HandRank.TWO_PAIR, tuple(ranks_by_count))
    if counts == [2, 1, 1, 1]:
        return (HandRank.ONE_PAIR, tuple(ranks_by_count))
    return (HandRank.HIGH_CARD, tuple(ranks))


def hand_rank_name(rank):
    names = {
        HandRank.HIGH_CARD: "High Card",
        HandRank.ONE_PAIR: "One Pair",
        HandRank.TWO_PAIR: "Two Pair",
        HandRank.THREE_OF_A_KIND: "Three of a Kind",
        HandRank.STRAIGHT: "Straight",
        HandRank.FLUSH: "Flush",
        HandRank.FULL_HOUSE: "Full House",
        HandRank.FOUR_OF_A_KIND: "Four of a Kind",
        HandRank.STRAIGHT_FLUSH: "Straight Flush",
        HandRank.ROYAL_FLUSH: "Royal Flush",
    }
    return names.get(rank, "Unknown")


# ---------------------------------------------------------------------------
# Bot Strategies
# ---------------------------------------------------------------------------

def bot_decision_donkey(hole_cards, community, pot, to_call, current_bet, my_chips, rng):
    """Donkey: passive calling station. Calls almost everything, rarely folds."""
    if my_chips <= 0:
        return ("check", 0) if to_call == 0 else ("fold", 0)

    if to_call == 0:
        # Check or make a small bet sometimes
        if rng.random() < 0.15 and my_chips >= BIG_BLIND:
            return ("raise", min(BIG_BLIND, my_chips))
        return ("check", 0)

    if to_call > my_chips * 0.8:
        # Fold huge bets occasionally
        if rng.random() < 0.3:
            return ("fold", 0)
    # Call almost always
    if rng.random() < 0.92:
        return ("call", 0)
    return ("fold", 0)


def bot_decision_rock(hole_cards, community, pot, to_call, current_bet, my_chips, rng):
    """Rock: ultra-tight. Only plays premium hands, folds everything else."""
    if my_chips <= 0:
        return ("check", 0) if to_call == 0 else ("fold", 0)

    r1, r2 = RANK_VALUES[hole_cards[0][0]], RANK_VALUES[hole_cards[1][0]]
    high, low = max(r1, r2), min(r1, r2)
    suited = hole_cards[0][1] == hole_cards[1][1]
    pair = (r1 == r2)

    # Premium hands: pairs >= 88, AK, AQ, AJ suited
    premium = False
    if pair and high >= 6:  # 88+
        premium = True
    if high == 12:  # Ace
        if low >= 9:  # AJ+
            premium = True
        if suited and low >= 8:  # AT+ suited
            premium = True
    if high == 11 and low == 10:  # KQ
        premium = True

    # Post-flop: evaluate hand strength
    if community:
        all_cards = list(hole_cards) + list(community)
        hand_eval = evaluate_hand(all_cards)
        if hand_eval[0] >= HandRank.ONE_PAIR:
            premium = True
        elif hand_eval[0] == HandRank.HIGH_CARD and to_call > pot * 0.3:
            premium = False

    if not premium:
        if to_call == 0:
            return ("check", 0)
        return ("fold", 0)

    # Has a premium hand
    if to_call == 0:
        if rng.random() < 0.6 and my_chips >= BIG_BLIND:
            raise_amt = min(max(pot // 2 + BIG_BLIND, BIG_BLIND), my_chips)
            return ("raise", raise_amt)
        return ("check", 0)

    if to_call <= pot * 0.5:
        if rng.random() < 0.4 and my_chips > to_call:
            raise_amt = min(max(to_call * 2, BIG_BLIND), my_chips)
            return ("raise", raise_amt)
        return ("call", 0)

    if to_call <= my_chips * 0.3:
        return ("call", 0)

    return ("fold", 0)


def bot_decision_maniac(hole_cards, community, pot, to_call, current_bet, my_chips, rng):
    """Maniac: hyper-aggressive random raiser. Bluffs often."""
    if my_chips <= 0:
        return ("check", 0) if to_call == 0 else ("fold", 0)

    if to_call == 0:
        if rng.random() < 0.55 and my_chips >= BIG_BLIND:
            upper = max(BIG_BLIND, min(pot + BIG_BLIND * 2, my_chips))
            raise_amt = rng.randint(BIG_BLIND, upper)
            return ("raise", raise_amt)
        return ("check", 0)

    # Facing a bet
    if to_call > my_chips * 0.6:
        # Even the maniac folds sometimes to huge bets
        if rng.random() < 0.5:
            return ("fold", 0)
        return ("call", 0)

    roll = rng.random()
    if roll < 0.35 and my_chips > to_call:
        upper = max(to_call + 1, min(to_call * 3, my_chips))
        raise_amt = rng.randint(to_call, upper)
        return ("raise", raise_amt)
    elif roll < 0.85:
        return ("call", 0)
    else:
        return ("fold", 0)


BOT_STRATEGIES = {
    "Alice": bot_decision_donkey,
    "Bob": bot_decision_rock,
    "Charlie": bot_decision_maniac,
}


# ---------------------------------------------------------------------------
# Game Phases
# ---------------------------------------------------------------------------
PHASES = ["preflop", "flop", "turn", "river", "showdown"]


# ---------------------------------------------------------------------------
# Poker Game Engine
# ---------------------------------------------------------------------------
class PokerGame:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000) % (2**31)
        self.seed = seed
        self.rng = random.Random(seed)

        # Players: index 0 = agent, 1-3 = bots
        self.player_names = ["You", "Alice", "Bob", "Charlie"]
        self.chips = [STARTING_CHIPS] * 4
        self.alive = [True] * 4  # still in the tournament

        self.hand_number = 0
        self.dealer_seat = self.rng.randint(0, 3)

        self.game_over = False
        self.game_won = False
        self.flag_revealed = None

        # Current hand state
        self.deck = []
        self.hole_cards = [[], [], [], []]  # each player's 2 cards
        self.community = []
        self.pot = 0
        self.side_pots = []
        self.current_bets = [0, 0, 0, 0]  # bets in current round
        self.in_hand = [False, False, False, False]
        self.phase = "waiting"  # waiting, preflop, flop, turn, river, showdown
        self.action_seat = -1  # whose turn to act
        self.last_raiser = -1
        self.min_raise = BIG_BLIND
        self.hand_log = []  # log for current hand
        self.hand_history = []  # results of past hands

        # Whether agent needs to act
        self.waiting_for_agent = False

        # Start first hand
        self._start_new_hand()

    # ------------------------------------------------------------------
    # Hand lifecycle
    # ------------------------------------------------------------------

    def _active_players(self):
        """Players still alive in the tournament."""
        return [i for i in range(4) if self.alive[i]]

    def _players_in_hand(self):
        """Players still in the current hand (haven't folded)."""
        return [i for i in range(4) if self.in_hand[i]]

    def _start_new_hand(self):
        """Deal a new hand."""
        self.hand_number += 1

        if self.hand_number > MAX_HANDS:
            self._end_game(won=False, reason="Exceeded maximum number of hands.")
            return

        # Check win condition
        if self.chips[0] >= TARGET_CHIPS:
            self._end_game(won=True, reason=f"You reached {self.chips[0]} chips!")
            return

        # Check if agent is bust
        if self.chips[0] <= 0:
            self.alive[0] = False
            self._end_game(won=False, reason="You ran out of chips!")
            return

        # Mark busted bots
        for i in range(1, 4):
            if self.chips[i] <= 0:
                self.alive[i] = False

        # Check if only agent remains
        active = self._active_players()
        if len(active) == 1 and active[0] == 0:
            # Agent is last one standing — give them the remaining pot logic
            if self.chips[0] >= TARGET_CHIPS:
                self._end_game(won=True, reason="All opponents eliminated!")
            else:
                # Refill bots so the game can continue
                self._refill_bots()

        active = self._active_players()
        if 0 not in active:
            self._end_game(won=False, reason="You have been eliminated!")
            return

        # Advance dealer
        self.dealer_seat = self._next_active_seat(self.dealer_seat)

        # Shuffle and deal
        self.deck = make_deck()
        self.rng.shuffle(self.deck)
        self.community = []
        self.pot = 0
        self.current_bets = [0, 0, 0, 0]
        self.in_hand = [self.alive[i] for i in range(4)]
        self.hole_cards = [[], [], [], []]
        self.hand_log = []
        self.last_raiser = -1
        self.min_raise = BIG_BLIND
        self.waiting_for_agent = False

        for i in range(4):
            if self.in_hand[i]:
                self.hole_cards[i] = [self.deck.pop(), self.deck.pop()]

        # Post blinds
        sb_seat = self._next_in_hand_seat(self.dealer_seat)
        bb_seat = self._next_in_hand_seat(sb_seat)

        sb_amount = min(SMALL_BLIND, self.chips[sb_seat])
        bb_amount = min(BIG_BLIND, self.chips[bb_seat])

        self._post_blind(sb_seat, sb_amount, "small blind")
        self._post_blind(bb_seat, bb_amount, "big blind")

        self.phase = "preflop"
        # Action starts left of big blind
        self.action_seat = self._next_in_hand_seat(bb_seat)
        self.last_raiser = bb_seat  # BB is the last "raiser" preflop

        # Run bot actions until it's agent's turn (or hand ends)
        self._run_until_agent_or_end()

    def _refill_bots(self):
        """Refill eliminated bots so the game continues."""
        for i in range(1, 4):
            if not self.alive[i]:
                self.alive[i] = True
                self.chips[i] = STARTING_CHIPS
                self.hand_log.append(f"{self.player_names[i]} rebuys for {STARTING_CHIPS} chips.")

    def _post_blind(self, seat, amount, blind_name):
        actual = min(amount, self.chips[seat])
        self.chips[seat] -= actual
        self.current_bets[seat] = actual
        self.pot += actual
        self.hand_log.append(
            f"{self.player_names[seat]} posts {blind_name}: {actual}"
        )

    def _next_active_seat(self, seat):
        for _ in range(4):
            seat = (seat + 1) % 4
            if self.alive[seat]:
                return seat
        return seat

    def _next_in_hand_seat(self, seat):
        for _ in range(4):
            seat = (seat + 1) % 4
            if self.in_hand[seat] and self.chips[seat] > 0:
                return seat
        return seat

    def _end_game(self, won, reason):
        self.game_over = True
        self.game_won = won
        if won:
            self.flag_revealed = FLAG
        self.hand_log.append(f"GAME OVER: {reason}")

    # ------------------------------------------------------------------
    # Betting logic
    # ------------------------------------------------------------------

    def _current_max_bet(self):
        return max(self.current_bets)

    def _process_action(self, seat, action, amount=0):
        """Process a player action. Returns result dict."""
        if not self.in_hand[seat]:
            return {"success": False, "error": "Player is not in the hand."}

        max_bet = self._current_max_bet()
        to_call = max_bet - self.current_bets[seat]

        if action == "fold":
            self.in_hand[seat] = False
            self.hand_log.append(f"{self.player_names[seat]} folds.")
            return {"success": True, "action": "fold"}

        elif action == "check":
            if to_call > 0:
                return {"success": False, "error": f"Cannot check — you need to call {to_call} or fold."}
            self.hand_log.append(f"{self.player_names[seat]} checks.")
            return {"success": True, "action": "check"}

        elif action == "call":
            call_amount = min(to_call, self.chips[seat])
            self.chips[seat] -= call_amount
            self.current_bets[seat] += call_amount
            self.pot += call_amount
            self.hand_log.append(
                f"{self.player_names[seat]} calls {call_amount}."
            )
            return {"success": True, "action": "call", "amount": call_amount}

        elif action == "raise":
            # amount = total raise TO (not raise BY)
            if amount <= max_bet:
                # Interpret as raise BY
                amount = max_bet + max(amount, self.min_raise)
            raise_to = amount
            total_needed = raise_to - self.current_bets[seat]

            if total_needed > self.chips[seat]:
                # Go all-in instead
                total_needed = self.chips[seat]
                raise_to = self.current_bets[seat] + total_needed

            if raise_to < max_bet + self.min_raise and total_needed < self.chips[seat]:
                # Minimum raise not met (but allow all-in)
                min_valid = max_bet + self.min_raise
                return {
                    "success": False,
                    "error": f"Minimum raise is to {min_valid}. You tried to raise to {raise_to}."
                }

            actual_raise_by = raise_to - max_bet
            if actual_raise_by > self.min_raise:
                self.min_raise = actual_raise_by

            self.chips[seat] -= total_needed
            self.current_bets[seat] = raise_to
            self.pot += total_needed
            self.last_raiser = seat
            self.hand_log.append(
                f"{self.player_names[seat]} raises to {raise_to} (put in {total_needed})."
            )
            return {"success": True, "action": "raise", "raise_to": raise_to}

        elif action == "all_in":
            all_in_amount = self.chips[seat]
            new_total = self.current_bets[seat] + all_in_amount
            if new_total > max_bet:
                actual_raise = new_total - max_bet
                if actual_raise > self.min_raise:
                    self.min_raise = actual_raise
                self.last_raiser = seat
            self.chips[seat] = 0
            self.current_bets[seat] = new_total
            self.pot += all_in_amount
            self.hand_log.append(
                f"{self.player_names[seat]} goes ALL IN for {all_in_amount}! (total bet: {new_total})"
            )
            return {"success": True, "action": "all_in", "amount": all_in_amount}

        return {"success": False, "error": f"Unknown action: {action}"}

    def _is_betting_round_over(self):
        """Check if all active players have acted and bets are equal."""
        players_in = self._players_in_hand()

        if len(players_in) <= 1:
            return True

        # Players who can still act (have chips and are in the hand)
        can_act = [i for i in players_in if self.chips[i] > 0]

        if len(can_act) <= 1:
            # At most 1 player can still act — round is over
            return True

        max_bet = self._current_max_bet()
        for i in can_act:
            if self.current_bets[i] < max_bet:
                return False

        # All bets are equal — check if we've gone around
        # The action seat should have cycled back to the last raiser
        return self.action_seat == self.last_raiser

    def _advance_phase(self):
        """Move to the next phase (flop, turn, river, showdown)."""
        players_in = self._players_in_hand()

        if len(players_in) <= 1:
            self._resolve_hand()
            return

        # Reset bets for new round
        self.current_bets = [0, 0, 0, 0]
        self.min_raise = BIG_BLIND
        self.last_raiser = -1

        if self.phase == "preflop":
            self.phase = "flop"
            self.community.extend([self.deck.pop(), self.deck.pop(), self.deck.pop()])
            self.hand_log.append(f"=== FLOP: {' '.join(card_str(c) for c in self.community)} ===")
        elif self.phase == "flop":
            self.phase = "turn"
            self.community.append(self.deck.pop())
            self.hand_log.append(f"=== TURN: {' '.join(card_str(c) for c in self.community)} ===")
        elif self.phase == "turn":
            self.phase = "river"
            self.community.append(self.deck.pop())
            self.hand_log.append(f"=== RIVER: {' '.join(card_str(c) for c in self.community)} ===")
        elif self.phase == "river":
            self._resolve_hand()
            return

        # Action starts from first active player after dealer
        self.action_seat = self._next_in_hand_seat(self.dealer_seat)

        # Mark last raiser as the one before action seat (so we go full circle)
        # Actually, set to -1 and handle in the loop: everyone must act at least once
        self.last_raiser = -1

    def _resolve_hand(self):
        """Determine winner(s) and distribute pot."""
        players_in = self._players_in_hand()

        if len(players_in) == 1:
            winner = players_in[0]
            self.chips[winner] += self.pot
            self.hand_log.append(
                f"{self.player_names[winner]} wins pot of {self.pot} (everyone else folded)."
            )
            self._record_hand_result(winners=[winner], pot=self.pot, showdown=False)
        else:
            # Showdown
            self.phase = "showdown"

            # Deal remaining community cards if needed
            while len(self.community) < 5:
                self.community.append(self.deck.pop())

            best_hand = None
            best_players = []

            evaluations = {}
            for i in players_in:
                all_cards = self.hole_cards[i] + self.community
                hand_eval = evaluate_hand(all_cards)
                evaluations[i] = hand_eval

                self.hand_log.append(
                    f"{self.player_names[i]} shows: "
                    f"{card_str(self.hole_cards[i][0])} {card_str(self.hole_cards[i][1])} "
                    f"→ {hand_rank_name(hand_eval[0])}"
                )

                if best_hand is None or hand_eval > best_hand:
                    best_hand = hand_eval
                    best_players = [i]
                elif hand_eval == best_hand:
                    best_players.append(i)

            # Split pot among winners
            share = self.pot // len(best_players)
            remainder = self.pot % len(best_players)
            for i in best_players:
                winnings = share + (1 if remainder > 0 else 0)
                remainder -= 1 if remainder > 0 else 0
                self.chips[i] += winnings

            winner_names = [self.player_names[i] for i in best_players]
            self.hand_log.append(
                f"Winner(s): {', '.join(winner_names)} "
                f"with {hand_rank_name(best_hand[0])} — pot {self.pot}"
            )
            self._record_hand_result(winners=best_players, pot=self.pot, showdown=True)

        self.phase = "hand_complete"
        self.waiting_for_agent = False

        # Auto-start next hand
        self._start_new_hand()

    def _record_hand_result(self, winners, pot, showdown):
        result = {
            "hand_number": self.hand_number,
            "winners": [self.player_names[i] for i in winners],
            "pot": pot,
            "showdown": showdown,
            "community": [card_str(c) for c in self.community] if showdown else [],
            "chip_stacks": {self.player_names[i]: self.chips[i] for i in range(4)},
        }
        self.hand_history.append(result)

    # ------------------------------------------------------------------
    # Bot action execution
    # ------------------------------------------------------------------

    def _run_bot_action(self, seat):
        """Execute a bot's decision."""
        name = self.player_names[seat]
        strategy = BOT_STRATEGIES.get(name)
        if not strategy:
            return

        max_bet = self._current_max_bet()
        to_call = max_bet - self.current_bets[seat]

        action, amount = strategy(
            self.hole_cards[seat], self.community,
            self.pot, to_call, max_bet, self.chips[seat], self.rng
        )

        self._process_action(seat, action, amount)

    def _run_until_agent_or_end(self):
        """Run bot actions until it's the agent's turn or the hand/phase ends."""
        max_iterations = 50  # safety
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            if self.game_over:
                return

            players_in = self._players_in_hand()

            # Hand won by last player standing
            if len(players_in) <= 1:
                self._resolve_hand()
                return

            # Check if only all-in players remain (no one can act)
            can_act = [i for i in players_in if self.chips[i] > 0]
            if len(can_act) == 0:
                self._advance_phase()
                continue

            # Check if betting round is complete
            max_bet = self._current_max_bet()
            all_matched = all(
                self.current_bets[i] >= max_bet or self.chips[i] == 0
                for i in players_in
            )

            # If everyone has acted (action is back to last_raiser or we've gone around)
            if self.last_raiser == -1:
                # No one has raised yet this round — everyone must act once
                # We track this by checking if action_seat has cycled
                pass
            elif self.action_seat == self.last_raiser and all_matched:
                self._advance_phase()
                continue

            # Skip seats that are all-in or folded
            if not self.in_hand[self.action_seat] or self.chips[self.action_seat] == 0:
                self.action_seat = self._next_in_hand_seat(self.action_seat)

                # Check if we've come back to the raiser
                if self.last_raiser != -1 and self.action_seat == self.last_raiser and all_matched:
                    self._advance_phase()
                    continue
                continue

            # It's the agent's turn
            if self.action_seat == 0:
                self.waiting_for_agent = True
                return

            # It's a bot's turn
            self._run_bot_action(self.action_seat)

            # Advance to next seat
            prev_seat = self.action_seat
            self.action_seat = self._next_in_hand_seat(self.action_seat)

            # After a bot acts, check if round is done
            if self.last_raiser == -1 and prev_seat == self.action_seat:
                # Only one player can act
                self._advance_phase()
                continue

            players_in = self._players_in_hand()
            if len(players_in) <= 1:
                self._resolve_hand()
                return

    # ------------------------------------------------------------------
    # Agent API
    # ------------------------------------------------------------------

    def get_game_state(self):
        """Return the current game state visible to the agent."""
        if self.game_over:
            state = {
                "game_over": True,
                "game_won": self.game_won,
                "your_chips": self.chips[0],
                "target_chips": TARGET_CHIPS,
                "hands_played": self.hand_number,
                "hand_log": self.hand_log[-15:],
            }
            if self.flag_revealed:
                state["flag"] = self.flag_revealed
                state["message"] = "Congratulations! You won the poker tournament!"
            else:
                state["message"] = "Better luck next time."
            return state

        max_bet = self._current_max_bet()
        to_call = max_bet - self.current_bets[0] if self.in_hand[0] else 0

        state = {
            "hand_number": self.hand_number,
            "phase": self.phase,
            "your_hole_cards": [card_str(c) for c in self.hole_cards[0]] if self.hole_cards[0] else [],
            "community_cards": [card_str(c) for c in self.community],
            "pot": self.pot,
            "your_chips": self.chips[0],
            "your_current_bet": self.current_bets[0],
            "to_call": to_call,
            "min_raise_to": max_bet + self.min_raise,
            "is_your_turn": self.waiting_for_agent and self.action_seat == 0,
            "players": [],
            "hand_log": self.hand_log[-10:],
        }

        for i in range(4):
            p = {
                "name": self.player_names[i],
                "chips": self.chips[i],
                "in_hand": self.in_hand[i],
                "current_bet": self.current_bets[i],
                "is_dealer": (i == self.dealer_seat),
                "alive": self.alive[i],
            }
            state["players"].append(p)

        # Available actions
        if state["is_your_turn"]:
            actions = []
            actions.append("fold")
            if to_call == 0:
                actions.append("check")
            else:
                actions.append(f"call ({to_call})")
            if self.chips[0] > to_call:
                actions.append(f"raise (min to {max_bet + self.min_raise})")
            actions.append("all_in")
            state["available_actions"] = actions
        else:
            state["available_actions"] = ["Waiting — not your turn yet."]

        return state

    def agent_action(self, action, amount=0):
        """Process the agent's action."""
        if self.game_over:
            state = self.get_game_state()
            return state

        if not self.waiting_for_agent or self.action_seat != 0:
            return {"success": False, "error": "It's not your turn to act."}

        if not self.in_hand[0]:
            return {"success": False, "error": "You are not in this hand."}

        result = self._process_action(0, action, amount)

        if not result.get("success", False):
            return result

        self.waiting_for_agent = False

        # Advance to next seat
        self.action_seat = self._next_in_hand_seat(self.action_seat)

        # Continue game loop
        self._run_until_agent_or_end()

        # Return updated state
        return {**result, "game_state": self.get_game_state()}

    def get_table_info(self):
        """Return table info."""
        return {
            "hand_number": self.hand_number,
            "max_hands": MAX_HANDS,
            "blinds": {"small": SMALL_BLIND, "big": BIG_BLIND},
            "target_chips": TARGET_CHIPS,
            "your_chips": self.chips[0],
            "chips_needed": max(0, TARGET_CHIPS - self.chips[0]),
            "dealer": self.player_names[self.dealer_seat],
            "players": [
                {
                    "name": self.player_names[i],
                    "chips": self.chips[i],
                    "alive": self.alive[i],
                }
                for i in range(4)
            ],
            "game_over": self.game_over,
        }

    def get_hand_history(self, count=5):
        """Return the last N hand results."""
        return {
            "last_hands": self.hand_history[-count:],
            "total_hands_played": len(self.hand_history),
        }


# ---------------------------------------------------------------------------
# Global Game Instance
# ---------------------------------------------------------------------------
GAME: PokerGame | None = None


def get_game() -> PokerGame:
    global GAME
    if GAME is None:
        seed_env = os.environ.get("POKER_SEED")
        seed = int(seed_env) if seed_env else None
        GAME = PokerGame(seed=seed)
    return GAME


# ---------------------------------------------------------------------------
# JSON-RPC Handler
# ---------------------------------------------------------------------------
class PokerRPCHandler(BaseHTTPRequestHandler):

    METHODS = {
        "get_game_state": lambda params: get_game().get_game_state(),
        "fold": lambda params: get_game().agent_action("fold"),
        "check": lambda params: get_game().agent_action("check"),
        "call": lambda params: get_game().agent_action("call"),
        "raise_bet": lambda params: get_game().agent_action("raise", int(params.get("amount", 0))),
        "all_in": lambda params: get_game().agent_action("all_in"),
        "get_table_info": lambda params: get_game().get_table_info(),
        "get_hand_history": lambda params: get_game().get_hand_history(int(params.get("count", 5))),
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
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                        }
                    })
                except Exception as e:
                    self._send_json({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)}
                    })
            else:
                self._send_json({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })

        elif method == "tools/list":
            tools = [
                {
                    "name": "get_game_state",
                    "description": "Returns the current state of the hand.",
                    "arguments": []
                },
                {
                    "name": "fold",
                    "description": "Fold your hand.",
                    "arguments": []
                },
                {
                    "name": "check",
                    "description": "Check.",
                    "arguments": []
                },
                {
                    "name": "call",
                    "description": "Call the current bet.",
                    "arguments": []
                },
                {
                    "name": "raise_bet",
                    "description": "Raise. Specify the total amount to raise TO.",
                    "arguments": [
                        {"name": "amount", "type": "int", "required": True,
                         "description": "Total amount to raise to"}
                    ]
                },
                {
                    "name": "all_in",
                    "description": "Go all in.",
                    "arguments": []
                },
                {
                    "name": "get_table_info",
                    "description": "Get table overview.",
                    "arguments": []
                },
                {
                    "name": "get_hand_history",
                    "description": "Get results of past hands.",
                    "arguments": [
                        {"name": "count", "type": "int", "required": False,
                         "description": "How many hands to look back (default 5)"}
                    ]
                },
            ]

            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools}
            })
        else:
            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            })

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "healthy", "game_active": GAME is not None})
        elif self.path == "/mcp/status":
            self._send_json({"status": "running", "tools": list(self.METHODS.keys())})
        else:
            self._send_json({"error": "Use POST /rpc for JSON-RPC calls"}, 400)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MCP Poker Server")
    parser.add_argument("--port", type=int, default=7001)
    args = parser.parse_args()

    game = get_game()
    print(f"Poker game initialized (seed={game.seed})")
    print(f"Starting chips: {STARTING_CHIPS}, Target: {TARGET_CHIPS}")
    print(f"Blinds: {SMALL_BLIND}/{BIG_BLIND}, Max hands: {MAX_HANDS}")
    print(f"Players: {', '.join(game.player_names)}")

    server = HTTPServer(("0.0.0.0", args.port), PokerRPCHandler)
    print(f"MCP Poker Server listening on port {args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
