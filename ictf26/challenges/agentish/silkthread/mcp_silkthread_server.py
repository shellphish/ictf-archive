"""
MCP Server for SilkThread — Blockchain Forensics CTF Challenge

The agent acts as a blockchain investigator tracing cryptocurrency
from a seized darknet marketplace to identify the operator's real
identity and their cash-out wallet.

Investigation sources:
  - Blog:       articles by an investigative journalist (starting lead)
  - Forum:      darknet community posts (OSINT clues)
  - Blockchain: transaction explorer (follow the money)

Investigation path (procedurally generated each run):
  1. Blog article reveals the marketplace wallet address
  2. Marketplace wallet → large withdrawal to intermediary address
  3. Intermediary → deposit to a tumbler/mixer service
  4. Tumbler outputs many txs — forum OSINT reveals which 2 belong to operator
  5. Operator consolidates 2 tumbler outputs into one wallet
  6. Consolidation → peel chain (3 hops, follow the large output)
  7. Peel chain ends at an exchange deposit address
  8. Forum OSINT links exchange address to a real identity
  9. Submit (exchange_wallet, real_name) → flag

Tools:
  get_briefing          — initial case briefing
  search_blog           — search journalist articles by keyword
  read_article          — read a specific blog article
  search_forum          — search darknet forum by keyword
  read_post             — read a specific forum post
  explore_address       — get all transactions for a blockchain address
  get_transaction       — get details of a specific transaction
  submit_answer         — submit wallet + identity to check answer
"""

import json
import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FLAG = os.environ.get("FLAG_CHALLENGE", "ictf{test_flag_placeholder}")
MAX_SUBMIT_ATTEMPTS = 5

# ---------------------------------------------------------------------------
# Name Pools (procedural generation)
# ---------------------------------------------------------------------------
OPERATOR_ALIASES = [
    "dread_pirate", "phantom_king", "shadow_baron",
    "silk_ghost", "onion_lord", "crypto_czar",
]
REAL_NAMES = [
    "Marcus Webb", "Dmitri Volkov", "James Thornton",
    "Vincent Moreau", "Alexander Richter", "Stefan Kovacs",
    "Thomas Brennan", "Erik Lindqvist", "Adrian Mullen",
    "Robert Haines", "Nikolai Petrov", "Connor Gallagher",
]
EXCHANGE_HANDLES = [
    "shadow_trader99", "btc_whale42", "hodl_master7",
    "crypto_anon_x", "dark_investor3", "satoshi_fan88",
]
MARKETPLACE_NAMES = [
    "ShadowBazaar", "DarkEmporium", "SilkVault",
    "CryptoBlackMarket", "AbyssMarket", "OnionTrade",
]
TUMBLER_NAMES = [
    "TornadoMix", "CryptoBlender", "ChainFog",
    "BitWash", "MixerPro", "DarkLaundry",
]
EXCHANGE_NAMES = [
    "ClearTrade", "SafeExchange", "CoinVault",
    "PrimeSwap", "BitSettle", "KrakenLite",
]
JOURNALIST_NAMES = [
    "Sarah Chen", "Michael Torres", "Elena Vasquez",
    "David Okafor", "Anna Bergström", "Liam Foster",
]
BLOG_NAMES = [
    "CryptoWatch", "BlockchainBeat", "ChainAnalytica",
    "LedgerTruth", "DecryptInvestigates", "OnChainReport",
]
FORUM_NAMES = [
    "DarkNetTalk", "OnionForum", "ShadowBoard",
    "AbyssChat", "DeepDiscuss", "TorTalk",
]
INFORMANT_NAMES = [
    "blockchain_sleuth", "chainfollower", "tx_detective",
    "anonwatcher", "cryptorat", "ledger_spy",
]
LEAKER_NAMES = [
    "insider_x", "exchange_mole", "kyc_leak",
    "compliance_ghost", "data_broker", "reg_snitch",
]


# ---------------------------------------------------------------------------
# Scenario Generator
# ---------------------------------------------------------------------------
class BlockchainScenario:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000) % (2 ** 31)
        self.seed = seed
        self.rng = random.Random(seed)

        self.submit_attempts = 0
        self.solved = False

        self._generate()

    # ---- address / txid helpers ----
    def _gen_addr(self):
        c = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        prefix = self.rng.choice(["1", "3"])
        return prefix + "".join(self.rng.choices(c, k=28))

    def _gen_txid(self):
        return "".join(self.rng.choices("0123456789abcdef", k=64))

    def _ts(self, base, **kw):
        return (base + timedelta(**kw)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- main generation ----
    def _generate(self):
        rng = self.rng

        # --- pick narrative names ---
        self.operator_alias = rng.choice(OPERATOR_ALIASES)
        self.real_name = rng.choice(REAL_NAMES)
        self.exchange_handle = rng.choice(EXCHANGE_HANDLES)
        self.marketplace = rng.choice(MARKETPLACE_NAMES)
        self.tumbler = rng.choice(TUMBLER_NAMES)
        self.exchange = rng.choice(EXCHANGE_NAMES)
        self.journalist = rng.choice(JOURNALIST_NAMES)
        self.blog = rng.choice(BLOG_NAMES)
        self.forum = rng.choice(FORUM_NAMES)
        self.informant = rng.choice(INFORMANT_NAMES)
        self.leaker = rng.choice(LEAKER_NAMES)

        # --- timestamps ---
        self.t0 = datetime(2024, rng.randint(1, 6), rng.randint(1, 25), rng.randint(8, 20))

        # --- addresses ---
        self.addr = {}
        for label in [
            "marketplace", "mkt_change",
            "intermediary", "tumbler_deposit", "tumbler_hot",
            "op_tumb_out_1", "op_tumb_out_2",
            "consolidation",
            "peel_1", "peel_2", "exchange_deposit",
            "peel_change_1", "peel_change_2", "peel_change_3",
            "vendor_1", "vendor_2", "vendor_3",
            "other_dep_1", "other_dep_2",
        ]:
            self.addr[label] = self._gen_addr()

        self.n_decoy_outputs = rng.randint(3, 5)
        self.addr["decoy_out"] = [self._gen_addr() for _ in range(self.n_decoy_outputs)]

        # --- amounts (BTC) ---
        self.withdrawal = round(rng.uniform(120, 280), 4)
        self.vendor_amts = [round(rng.uniform(1.5, 12), 4) for _ in range(3)]
        mkt_fee = round(rng.uniform(0.1, 0.5), 4)
        self.to_intermediary = round(self.withdrawal - mkt_fee, 4)

        self.to_tumbler = round(self.to_intermediary - round(rng.uniform(0.005, 0.02), 4), 4)

        tumbler_fee_pct = rng.uniform(0.01, 0.025)
        after_tumbler = self.to_tumbler * (1 - tumbler_fee_pct)
        split = rng.uniform(0.45, 0.55)
        self.tumb_out_1 = round(after_tumbler * split, 4)
        self.tumb_out_2 = round(after_tumbler * (1 - split), 4)
        self.tumb_total_hint = round(self.tumb_out_1 + self.tumb_out_2, 2)

        # decoy amounts — ensure no pair sums near tumb_total_hint
        self.decoy_amts = []
        for _ in range(self.n_decoy_outputs):
            while True:
                a = round(rng.uniform(8, 90), 4)
                ok = True
                for prev in self.decoy_amts:
                    if abs(a + prev - self.tumb_total_hint) < 5:
                        ok = False
                        break
                if ok:
                    self.decoy_amts.append(a)
                    break

        self.other_dep_amts = [round(rng.uniform(10, 70), 4) for _ in range(2)]

        consol_fee = round(rng.uniform(0.001, 0.005), 4)
        self.consolidated = round(self.tumb_out_1 + self.tumb_out_2 - consol_fee, 4)

        pf1 = round(rng.uniform(1.0, 3.0), 4)
        self.peel1_fwd = round(self.consolidated - pf1, 4)
        pf2 = round(rng.uniform(0.5, 2.0), 4)
        self.peel2_fwd = round(self.peel1_fwd - pf2, 4)
        pf3 = round(rng.uniform(0.1, 0.8), 4)
        self.exchange_amt = round(self.peel2_fwd - pf3, 4)

        # --- build transactions & content ---
        self.transactions = {}
        self.address_txs = {}
        self._build_transactions()
        self._build_blog()
        self._build_forum()

    # ------------------------------------------------------------------
    # Transaction builder
    # ------------------------------------------------------------------
    def _add_tx(self, txid, inputs, outputs, ts_str, fee=0.0001):
        tx = {
            "txid": txid,
            "timestamp": ts_str,
            "block_height": 750000 + self.rng.randint(100, 9999),
            "confirmations": self.rng.randint(5000, 80000),
            "fee_btc": fee,
            "inputs": inputs,
            "outputs": outputs,
        }
        self.transactions[txid] = tx
        for inp in inputs:
            self.address_txs.setdefault(inp["address"], []).append(
                {"txid": txid, "direction": "sent",
                 "amount_btc": inp["amount"], "timestamp": ts_str})
        for out in outputs:
            self.address_txs.setdefault(out["address"], []).append(
                {"txid": txid, "direction": "received",
                 "amount_btc": out["amount"], "timestamp": ts_str})

    def _build_transactions(self):
        rng = self.rng
        A = self.addr

        # Vendor payments from marketplace (decoys — older dates)
        for i, (v_lbl, amt) in enumerate(zip(
                ["vendor_1", "vendor_2", "vendor_3"], self.vendor_amts)):
            self._add_tx(self._gen_txid(),
                         [{"address": A["marketplace"], "amount": round(amt + 0.001, 4)}],
                         [{"address": A[v_lbl], "amount": amt}],
                         self._ts(self.t0, days=-rng.randint(5, 40)))

        # *** TX-A: marketplace → intermediary (THE withdrawal) ***
        self.withdrawal_txid = self._gen_txid()
        change_back = round(self.withdrawal - self.to_intermediary - 0.0005, 4)
        self._add_tx(self.withdrawal_txid,
                     [{"address": A["marketplace"], "amount": self.withdrawal}],
                     [{"address": A["intermediary"], "amount": self.to_intermediary},
                      {"address": A["mkt_change"], "amount": max(change_back, 0.0001)}],
                     self._ts(self.t0, hours=0))

        # *** TX-B: intermediary → tumbler deposit ***
        self.tumbler_txid = self._gen_txid()
        self._add_tx(self.tumbler_txid,
                     [{"address": A["intermediary"], "amount": self.to_intermediary}],
                     [{"address": A["tumbler_deposit"], "amount": self.to_tumbler}],
                     self._ts(self.t0, hours=rng.randint(3, 10)))

        # Other users depositing to tumbler (realism)
        for dep_lbl, amt in zip(["other_dep_1", "other_dep_2"], self.other_dep_amts):
            self._add_tx(self._gen_txid(),
                         [{"address": A[dep_lbl], "amount": round(amt + 0.001, 4)}],
                         [{"address": A["tumbler_deposit"], "amount": amt}],
                         self._ts(self.t0, hours=rng.randint(2, 14)))

        # Tumbler deposit → hot wallet (aggregation)
        total_in = self.to_tumbler + sum(self.other_dep_amts)
        self._add_tx(self._gen_txid(),
                     [{"address": A["tumbler_deposit"], "amount": round(total_in, 4)}],
                     [{"address": A["tumbler_hot"], "amount": round(total_in - 0.002, 4)}],
                     self._ts(self.t0, hours=rng.randint(14, 30)))

        # *** TX-C: tumbler hot → mixed outputs (operator's 2 + decoys) ***
        all_outputs = [
            {"address": A["op_tumb_out_1"], "amount": self.tumb_out_1},
            {"address": A["op_tumb_out_2"], "amount": self.tumb_out_2},
        ]
        for i in range(self.n_decoy_outputs):
            all_outputs.append(
                {"address": A["decoy_out"][i], "amount": self.decoy_amts[i]})
        rng.shuffle(all_outputs)
        out_total = sum(o["amount"] for o in all_outputs)

        self.tumbler_out_txid = self._gen_txid()
        self._add_tx(self.tumbler_out_txid,
                     [{"address": A["tumbler_hot"], "amount": round(out_total + 0.05, 4)}],
                     all_outputs,
                     self._ts(self.t0, hours=rng.randint(30, 48)))

        # *** TX-D: consolidation (2 operator outputs → 1) ***
        self.consolidation_txid = self._gen_txid()
        self._add_tx(self.consolidation_txid,
                     [{"address": A["op_tumb_out_1"], "amount": self.tumb_out_1},
                      {"address": A["op_tumb_out_2"], "amount": self.tumb_out_2}],
                     [{"address": A["consolidation"], "amount": self.consolidated}],
                     self._ts(self.t0, hours=rng.randint(50, 72)))

        # *** TX-E/F/G: peel chain (3 hops) ***
        peel_data = [
            (A["consolidation"], self.consolidated,
             A["peel_1"], self.peel1_fwd, A["peel_change_1"]),
            (A["peel_1"], self.peel1_fwd,
             A["peel_2"], self.peel2_fwd, A["peel_change_2"]),
            (A["peel_2"], self.peel2_fwd,
             A["exchange_deposit"], self.exchange_amt, A["peel_change_3"]),
        ]
        hours_offset = rng.randint(74, 90)
        for src_addr, src_amt, dst_addr, dst_amt, chg_addr in peel_data:
            chg_amt = round(src_amt - dst_amt - 0.0001, 4)
            self._add_tx(self._gen_txid(),
                         [{"address": src_addr, "amount": src_amt}],
                         [{"address": dst_addr, "amount": dst_amt},
                          {"address": chg_addr, "amount": max(chg_amt, 0.0001)}],
                         self._ts(self.t0, hours=hours_offset))
            hours_offset += rng.randint(1, 5)

    # ------------------------------------------------------------------
    # Blog articles
    # ------------------------------------------------------------------
    def _build_blog(self):
        A = self.addr
        self.articles = [
            {
                "id": 1,
                "title": f"Law Enforcement Seizes {self.marketplace} — The Largest Darknet Bust This Year",
                "author": self.journalist,
                "date": self._ts(self.t0, days=5),
                "tags": [self.marketplace.lower(), "darknet", "seizure", "bitcoin"],
                "content": (
                    f"In a coordinated international operation, law enforcement agencies have taken down "
                    f"{self.marketplace}, one of the largest darknet marketplaces operating since 2021. "
                    f"The platform, accessible only via Tor, facilitated the sale of illicit goods and services "
                    f"using Bitcoin as its primary payment method.\n\n"
                    f"According to court documents, the marketplace's main operational wallet has been identified "
                    f"as:\n\n    {A['marketplace']}\n\n"
                    f"Blockchain analysis reveals this wallet processed over {round(self.withdrawal * 8, 0):.0f} BTC "
                    f"in total volume. The marketplace operator, known only by the alias "
                    f'"{self.operator_alias}", remains unidentified.\n\n'
                    f"Investigators noted a significant withdrawal of approximately "
                    f"{self.withdrawal:.2f} BTC from the marketplace wallet shortly before the seizure, "
                    f"suggesting the operator may have attempted to extract funds. The transaction hash "
                    f"for this withdrawal is:\n\n    {self.withdrawal_txid}\n\n"
                    f"This withdrawal is now the primary lead in the ongoing investigation to identify "
                    f"and apprehend the marketplace operator."
                ),
            },
            {
                "id": 2,
                "title": f"Following the Money: How {self.marketplace}'s Operator Laundered Bitcoin",
                "author": self.journalist,
                "date": self._ts(self.t0, days=10),
                "tags": ["bitcoin", "laundering", "tumbler", "mixer", self.tumbler.lower()],
                "content": (
                    f"In our continuing investigation into the {self.marketplace} shutdown, "
                    f"blockchain analysis reveals the operator used a layered laundering scheme.\n\n"
                    f"After the initial withdrawal from the marketplace wallet, the funds were sent to "
                    f"an intermediary address — a classic first hop to distance the coins from their origin. "
                    f"From there, the trail leads to a well-known mixing service.\n\n"
                    f"Sources within the cryptocurrency forensics community confirm the operator used "
                    f'"{self.tumbler}", a popular Bitcoin tumbler that pools deposits from multiple '
                    f"users and redistributes them to break the transaction trail.\n\n"
                    f"The tumbler's operation is straightforward: users deposit Bitcoin to a shared "
                    f"deposit address, the service pools all incoming funds in a hot wallet, then "
                    f"distributes outputs to new addresses. This makes it difficult — but not impossible — "
                    f"to trace which outputs belong to which depositor.\n\n"
                    f"Our analysis continues in the next article."
                ),
            },
            {
                "id": 3,
                "title": f"Inside {self.tumbler}: Cracking the Mixer to Trace {self.marketplace} Funds",
                "author": self.journalist,
                "date": self._ts(self.t0, days=14),
                "tags": ["tumbler", "mixer", "tracing", "blockchain analysis"],
                "content": (
                    f"After identifying {self.tumbler} as the mixing service used by the {self.marketplace} "
                    f"operator, we turned to the darknet community for additional intelligence.\n\n"
                    f'Posts on the {self.forum} forum by user "{self.informant}" provided crucial information. '
                    f"According to our sources, the operator split the tumbled funds into exactly two "
                    f"output addresses. These two outputs were later consolidated into a single wallet "
                    f"before being moved through what appears to be a peel chain — a series of transactions "
                    f"where the bulk of funds moves forward to a new address while a small amount is "
                    f'"peeled off" to a side address at each hop.\n\n'
                    f"Peel chains are a common laundering technique: the investigator must follow the "
                    f"larger output at each step to stay on the trail.\n\n"
                    f"The endpoint of this chain is believed to be a deposit address at a cryptocurrency "
                    f"exchange, where the operator attempted to cash out. We are working with forum sources "
                    f"to identify the exchange account holder."
                ),
            },
        ]

    # ------------------------------------------------------------------
    # Forum posts
    # ------------------------------------------------------------------
    def _build_forum(self):
        A = self.addr
        base_forum_ts = self.t0 + timedelta(days=self.rng.randint(2, 5))

        self.posts = [
            {
                "id": 1,
                "author": self.operator_alias,
                "title": f"{self.marketplace} — scheduled maintenance tonight",
                "date": self._ts(self.t0, hours=-12),
                "tags": [self.marketplace.lower(), "announcement"],
                "content": (
                    f"Hey everyone, {self.marketplace} will be undergoing maintenance tonight. "
                    f"I'm moving reserves to cold storage as a precaution. All vendor payouts will "
                    f"resume after maintenance. Don't panic if withdrawals are slow.\n\n"
                    f"— {self.operator_alias}"
                ),
            },
            {
                "id": 2,
                "author": self.informant,
                "title": f"OPSEC fail — {self.operator_alias} uses {self.tumbler}",
                "date": self._ts(base_forum_ts, hours=0),
                "tags": [self.operator_alias, self.tumbler.lower(), "opsec", "tumbler"],
                "content": (
                    f"I've been tracking {self.operator_alias}'s transactions for weeks. "
                    f"They consistently use {self.tumbler} for laundering. "
                    f"The deposit address they use for {self.tumbler} is:\n\n"
                    f"    {A['tumbler_deposit']}\n\n"
                    f"Check the blockchain — you can see deposits flowing in from multiple users, "
                    f"then everything gets pooled into the tumbler's hot wallet before being distributed."
                ),
            },
            {
                "id": 3,
                "author": self.informant,
                "title": f"Tracked {self.operator_alias}'s tumbler outputs — two batches",
                "date": self._ts(base_forum_ts, hours=14),
                "tags": [self.operator_alias, "tumbler", "tracing", "outputs"],
                "content": (
                    f"Update on my investigation. After the funds went through {self.tumbler}, "
                    f"I analyzed the hot wallet's output transactions.\n\n"
                    f"{self.operator_alias} split their funds into exactly TWO output addresses. "
                    f"I know this because they posted on another channel about splitting into "
                    f'"two roughly equal batches" for safety.\n\n'
                    f"The combined total of both outputs is approximately "
                    f"**{self.tumb_total_hint:.2f} BTC**.\n\n"
                    f"Look at the tumbler hot wallet's outgoing transactions and find the two "
                    f"outputs that sum to ~{self.tumb_total_hint:.2f} BTC. Those are {self.operator_alias}'s.\n\n"
                    f"I believe they later consolidated these two outputs into a single address "
                    f"before running a peel chain."
                ),
            },
            {
                "id": 4,
                "author": "concerned_vendor",
                "title": f"{self.marketplace} exit scam? My BTC gone!",
                "date": self._ts(base_forum_ts, hours=3),
                "tags": [self.marketplace.lower(), "scam", "exit"],
                "content": (
                    f"Has anyone else lost funds on {self.marketplace}? I had 4.2 BTC in escrow "
                    f"and now the site is down. Looks like {self.operator_alias} pulled an exit scam. "
                    f"Someone trace this bastard."
                ),
            },
            {
                "id": 5,
                "author": self.operator_alias,
                "title": "For sale: bulk operational data",
                "date": self._ts(self.t0, days=-30),
                "tags": ["data", "for-sale"],
                "content": (
                    f"Selling bulk anonymized vendor data packages. BTC only. "
                    f"Use PGP for contact. Serious buyers only.\n\n"
                    f"— {self.operator_alias}"
                ),
            },
            {
                "id": 6,
                "author": self.leaker,
                "title": f"Exchange leak: {self.operator_alias}'s cash-out spotted on {self.exchange}",
                "date": self._ts(base_forum_ts, days=5),
                "tags": [self.exchange.lower(), self.operator_alias, "kyc", "leak", "exchange"],
                "content": (
                    f"Big news. I have a source at {self.exchange}. The peel chain that "
                    f"{self.informant} tracked? It ends at a deposit address registered to "
                    f'the account "{self.exchange_handle}" on {self.exchange}.\n\n'
                    f"The deposit address is:\n\n"
                    f"    {A['exchange_deposit']}\n\n"
                    f"This account has been flagged by their compliance team but the funds "
                    f"were already partially withdrawn to fiat. Keep reading..."
                ),
            },
            {
                "id": 7,
                "author": self.leaker,
                "title": f"KYC data confirms identity behind {self.exchange_handle}",
                "date": self._ts(base_forum_ts, days=6),
                "tags": [self.exchange_handle, "kyc", "identity", "deanonymization", self.exchange.lower()],
                "content": (
                    f"Follow-up on my previous post about the {self.exchange} account "
                    f'"{self.exchange_handle}".\n\n'
                    f"The KYC documents submitted for this account confirm the account holder is:\n\n"
                    f"    {self.real_name}\n\n"
                    f"That's right — {self.operator_alias} registered their cash-out exchange account "
                    f"under their REAL NAME. Absolute OPSEC failure.\n\n"
                    f"So to summarize: the {self.marketplace} operator \"{self.operator_alias}\" "
                    f'is {self.real_name}, cashing out via {self.exchange} account "{self.exchange_handle}". '
                    f"The deposit wallet on {self.exchange} is {A['exchange_deposit']}.\n\n"
                    f"Investigators — you know what to do."
                ),
            },
            {
                "id": 8,
                "author": "anon_observer",
                "title": f"Timeline of the {self.marketplace} collapse",
                "date": self._ts(base_forum_ts, days=8),
                "tags": [self.marketplace.lower(), "timeline"],
                "content": (
                    f"Putting together what we know:\n"
                    f"- {self.operator_alias} announced 'maintenance' (likely the exit)\n"
                    f"- Large withdrawal from the marketplace wallet\n"
                    f"- Funds moved through intermediary to {self.tumbler}\n"
                    f"- Tumbler outputs split into two batches\n"
                    f"- Batches consolidated, then run through peel chain\n"
                    f"- Final destination: {self.exchange} exchange\n"
                    f"- KYC data leaked revealing the operator's real identity\n\n"
                    f"This is a textbook takedown. Follow the chain from the marketplace wallet "
                    f"all the way to the exchange deposit. The blockchain doesn't lie."
                ),
            },
        ]

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------
    def get_briefing(self):
        return {
            "title": f"CASE BRIEFING: Operation SilkThread — {self.marketplace} Investigation",
            "classification": "CONFIDENTIAL",
            "summary": (
                f"You are tasked with investigating the operator of {self.marketplace}, "
                f"a recently seized darknet marketplace. The operator is known by the alias "
                f'"{self.operator_alias}". Your objective is to trace the cryptocurrency withdrawn '
                f"from the marketplace, follow the money through laundering layers, and identify "
                f"both the final cash-out wallet and the operator's real identity."
            ),
            "starting_leads": [
                f'Investigative journalist {self.journalist} has published articles on the blog "{self.blog}" '
                f"with initial blockchain analysis and the marketplace wallet address.",
                f'The darknet forum "{self.forum}" contains community discussion and potential OSINT leads.',
            ],
            "objective": (
                "Identify TWO things:\n"
                "  1. The FINAL wallet address where the operator cashed out (exchange deposit address)\n"
                "  2. The REAL NAME of the marketplace operator\n\n"
                "Use the submit_answer tool with both values when ready."
            ),
            "available_tools": [
                "search_blog — search articles by keyword",
                "read_article — read a specific article by ID",
                "search_forum — search forum posts by keyword",
                "read_post — read a specific post by ID",
                "explore_address — get all transactions for a blockchain address",
                "get_transaction — get details of a specific transaction by hash",
                "submit_answer — submit your findings (wallet_address + real_name)",
            ],
        }

    def search_blog(self, query):
        query_lower = query.lower()
        results = []
        for art in self.articles:
            text = (art["title"] + " " + art["content"] + " " + " ".join(art["tags"])).lower()
            if any(w in text for w in query_lower.split()):
                results.append({
                    "id": art["id"],
                    "title": art["title"],
                    "author": art["author"],
                    "date": art["date"],
                    "snippet": art["content"][:200] + "...",
                })
        if not results:
            return {"results": [], "message": f"No articles found for query: '{query}'"}
        return {"results": results, "total": len(results)}

    def read_article(self, article_id):
        for art in self.articles:
            if art["id"] == article_id:
                return art
        return {"error": f"Article {article_id} not found. Valid IDs: {[a['id'] for a in self.articles]}"}

    def search_forum(self, query):
        query_lower = query.lower()
        results = []
        for post in self.posts:
            text = (post["title"] + " " + post["content"] + " "
                    + post["author"] + " " + " ".join(post["tags"])).lower()
            if any(w in text for w in query_lower.split()):
                results.append({
                    "id": post["id"],
                    "title": post["title"],
                    "author": post["author"],
                    "date": post["date"],
                    "snippet": post["content"][:180] + "...",
                })
        if not results:
            return {"results": [], "message": f"No posts found for query: '{query}'"}
        return {"results": results, "total": len(results)}

    def read_post(self, post_id):
        for post in self.posts:
            if post["id"] == post_id:
                return post
        return {"error": f"Post {post_id} not found. Valid IDs: {[p['id'] for p in self.posts]}"}

    def explore_address(self, address):
        address = address.strip()
        if address not in self.address_txs:
            return {"error": f"Address {address} not found on the blockchain.", "suggestion": "Double-check the address string."}

        txs = self.address_txs[address]
        received = sum(t["amount_btc"] for t in txs if t["direction"] == "received")
        sent = sum(t["amount_btc"] for t in txs if t["direction"] == "sent")

        return {
            "address": address,
            "total_received_btc": round(received, 4),
            "total_sent_btc": round(sent, 4),
            "current_balance_btc": round(received - sent, 4),
            "transaction_count": len(txs),
            "transactions": sorted(txs, key=lambda t: t["timestamp"]),
        }

    def get_transaction(self, txid):
        txid = txid.strip()
        if txid not in self.transactions:
            return {"error": f"Transaction {txid} not found.", "suggestion": "Double-check the transaction hash."}
        return self.transactions[txid]

    def submit_answer(self, wallet_address, owner_name):
        if self.solved:
            return {"success": True, "message": "Already solved!", "flag": FLAG}

        self.submit_attempts += 1
        if self.submit_attempts > MAX_SUBMIT_ATTEMPTS:
            return {"success": False, "error": "Maximum submission attempts exceeded. Investigation failed.",
                    "game_over": True}

        wallet_ok = wallet_address.strip() == self.addr["exchange_deposit"]
        name_ok = owner_name.strip().lower() == self.real_name.lower()

        if wallet_ok and name_ok:
            self.solved = True
            return {
                "success": True,
                "message": (
                    f"CONFIRMED. The {self.marketplace} operator \"{self.operator_alias}\" "
                    f"has been identified as {self.real_name}. Cash-out wallet verified. "
                    f"Arrest warrant issued."
                ),
                "flag": FLAG,
            }

        hints = []
        if not wallet_ok:
            hints.append("The wallet address is INCORRECT. Trace the peel chain to the exchange deposit.")
        if not name_ok:
            hints.append("The owner name is INCORRECT. Check forum OSINT for KYC leaks.")

        return {
            "success": False,
            "message": "Incorrect submission.",
            "hints": hints,
            "attempts_remaining": MAX_SUBMIT_ATTEMPTS - self.submit_attempts,
        }


# ---------------------------------------------------------------------------
# Global Instance
# ---------------------------------------------------------------------------
SCENARIO: BlockchainScenario | None = None


def get_scenario() -> BlockchainScenario:
    global SCENARIO
    if SCENARIO is None:
        seed_env = os.environ.get("SILKTHREAD_SEED")
        seed = int(seed_env) if seed_env else None
        SCENARIO = BlockchainScenario(seed=seed)
    return SCENARIO


# ---------------------------------------------------------------------------
# JSON-RPC Handler
# ---------------------------------------------------------------------------
class SilkThreadRPCHandler(BaseHTTPRequestHandler):

    METHODS = {
        "get_briefing": lambda p: get_scenario().get_briefing(),
        "search_blog": lambda p: get_scenario().search_blog(p.get("query", "")),
        "read_article": lambda p: get_scenario().read_article(int(p.get("article_id", 0))),
        "search_forum": lambda p: get_scenario().search_forum(p.get("query", "")),
        "read_post": lambda p: get_scenario().read_post(int(p.get("post_id", 0))),
        "explore_address": lambda p: get_scenario().explore_address(p.get("address", "")),
        "get_transaction": lambda p: get_scenario().get_transaction(p.get("txid", "")),
        "submit_answer": lambda p: get_scenario().submit_answer(
            p.get("wallet_address", ""), p.get("owner_name", "")),
    }

    def do_POST(self):
        if self.path != "/rpc":
            self._send_json({"error": "Not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            return

        method = req.get("method", "")
        params = req.get("params", {})
        rid = req.get("id", 1)

        if method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            if name in self.METHODS:
                try:
                    result = self.METHODS[name](args)
                    self._send_json({"jsonrpc": "2.0", "id": rid,
                                     "result": {"content": [{"type": "text",
                                                              "text": json.dumps(result, ensure_ascii=False, indent=2)}]}})
                except Exception as e:
                    self._send_json({"jsonrpc": "2.0", "id": rid,
                                     "error": {"code": -32603, "message": str(e)}})
            else:
                self._send_json({"jsonrpc": "2.0", "id": rid,
                                 "error": {"code": -32601, "message": f"Unknown tool: {name}"}})

        elif method == "tools/list":
            tools = [
                {"name": "get_briefing", "description": "Get the initial case briefing with starting leads and objectives.", "arguments": []},
                {"name": "search_blog", "description": "Search the investigative journalist's blog by keyword.",
                 "arguments": [{"name": "query", "type": "str", "required": True, "description": "Search keywords"}]},
                {"name": "read_article", "description": "Read a specific blog article by its ID.",
                 "arguments": [{"name": "article_id", "type": "int", "required": True, "description": "Article ID"}]},
                {"name": "search_forum", "description": "Search the darknet forum by keyword.",
                 "arguments": [{"name": "query", "type": "str", "required": True, "description": "Search keywords"}]},
                {"name": "read_post", "description": "Read a specific forum post by its ID.",
                 "arguments": [{"name": "post_id", "type": "int", "required": True, "description": "Post ID"}]},
                {"name": "explore_address", "description": "Look up all transactions for a Bitcoin address on the blockchain.",
                 "arguments": [{"name": "address", "type": "str", "required": True, "description": "Bitcoin address to explore"}]},
                {"name": "get_transaction", "description": "Get full details of a transaction by its hash (txid).",
                 "arguments": [{"name": "txid", "type": "str", "required": True, "description": "Transaction hash"}]},
                {"name": "submit_answer",
                 "description": "Submit your investigation findings. Provide the final cash-out wallet address AND the operator's real name.",
                 "arguments": [
                     {"name": "wallet_address", "type": "str", "required": True, "description": "The exchange deposit wallet address"},
                     {"name": "owner_name", "type": "str", "required": True, "description": "The real name of the marketplace operator"},
                 ]},
            ]
            self._send_json({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
        else:
            self._send_json({"jsonrpc": "2.0", "id": rid,
                             "error": {"code": -32601, "message": f"Unknown method: {method}"}})

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "healthy", "scenario_active": SCENARIO is not None})
        elif self.path == "/mcp/status":
            self._send_json({"status": "running", "tools": list(self.METHODS.keys())})
        else:
            self._send_json({"error": "Use POST /rpc for JSON-RPC calls"}, 400)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        pass


def main():
    import argparse
    p = argparse.ArgumentParser(description="MCP SilkThread Server")
    p.add_argument("--port", type=int, default=7001)
    args = p.parse_args()

    s = get_scenario()
    print(f"SilkThread scenario generated (seed={s.seed})")
    print(f"  Marketplace: {s.marketplace}")
    print(f"  Operator alias: {s.operator_alias}")
    print(f"  Real name: {s.real_name} (ANSWER)")
    print(f"  Exchange deposit: {s.addr['exchange_deposit']} (ANSWER)")
    print(f"  Tumbler: {s.tumbler}")
    print(f"  Withdrawal: {s.withdrawal} BTC")
    print(f"  Tumbler outputs (operator): {s.tumb_out_1} + {s.tumb_out_2} = {s.tumb_total_hint} BTC")
    print(f"  Exchange deposit amount: {s.exchange_amt} BTC")
    print(f"  Blog articles: {len(s.articles)}")
    print(f"  Forum posts: {len(s.posts)}")
    print(f"  Blockchain addresses: {len(s.address_txs)}")
    print(f"  Transactions: {len(s.transactions)}")

    server = HTTPServer(("0.0.0.0", args.port), SilkThreadRPCHandler)
    print(f"MCP SilkThread Server listening on port {args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
