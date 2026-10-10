"""
MCP Server for SilkThread — Blockchain Forensics CTF Challenge (HARDENED)

The agent acts as a blockchain investigator tracing cryptocurrency
from a seized darknet marketplace to identify the operator's real
identity and their cash-out wallet.

HARDENED changes vs original:
  - 5 blog articles (1 key + 4 distractions/context)
  - 20 forum posts (heavy misdirection, multiple red herrings, contradictory "intel")
  - Multi-input transactions, decoy consolidations, longer peel chain (5 hops)
  - Tumbler outputs include "near-miss" pairs that sum close to the hint
  - Multiple plausible real names presented across forum sources
  - Fake "leaked" addresses in forum posts that don't match on-chain
  - A CoinJoin-style transaction mid-chain that merges with unrelated funds
  - Time-based misdirection (later posts claim to "correct" older accurate info)
  - Only 1 submission attempt allowed
"""

import json
import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

FLAG = os.environ.get("FLAG_CHALLENGE")
MAX_SUBMIT_ATTEMPTS = 1

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
FAKE_EXCHANGE_NAMES = [
    "BitHaven", "CryptoNest", "SwapGate", "VaultBridge",
]
SECOND_TUMBLER_NAMES = [
    "FogCycle", "ChainWash", "ObfuscaMix", "SteamRoll",
]


class BlockchainScenario:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000) % (2 ** 31)
        self.seed = seed
        self.rng = random.Random(seed)
        self.submit_attempts = 0
        self.solved = False
        self._generate()

    def _gen_addr(self):
        c = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        prefix = self.rng.choice(["1", "3", "bc1q"])
        return prefix + "".join(self.rng.choices(c, k=28))

    def _gen_txid(self):
        return "".join(self.rng.choices("0123456789abcdef", k=64))

    def _ts(self, base, **kw):
        return (base + timedelta(**kw)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _generate(self):
        rng = self.rng

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

        rh_pool = [n for n in REAL_NAMES if n != self.real_name]
        rng.shuffle(rh_pool)
        self.red_herring_name_1 = rh_pool[0]
        self.red_herring_name_2 = rh_pool[1]
        self.red_herring_name_3 = rh_pool[2]
        rh_alias_pool = [a for a in OPERATOR_ALIASES if a != self.operator_alias]
        self.red_herring_alias = rng.choice(rh_alias_pool)

        self.fake_exchange = rng.choice(FAKE_EXCHANGE_NAMES)
        self.second_tumbler = rng.choice(SECOND_TUMBLER_NAMES)
        self.fake_exchange_handle = rng.choice([h for h in EXCHANGE_HANDLES if h != self.exchange_handle])

        self.t0 = datetime(2024, rng.randint(1, 6), rng.randint(1, 25), rng.randint(8, 20))

        self.addr = {}
        for label in [
            "marketplace", "mkt_change",
            "intermediary", "inter_change",
            "tumbler_deposit", "tumbler_hot",
            "op_tumb_out_1", "op_tumb_out_2",
            "consolidation",
            "peel_1", "peel_2", "peel_3", "peel_4", "exchange_deposit",
            "peel_change_1", "peel_change_2", "peel_change_3", "peel_change_4", "peel_change_5",
            "cj_other_in_1", "cj_other_in_2",
            "cj_other_out_1", "cj_other_out_2",
            "vendor_1", "vendor_2", "vendor_3", "vendor_4", "vendor_5",
            "other_dep_1", "other_dep_2", "other_dep_3",
            "fake_exchange_addr", "fake_consolidation",
            "decoy_consol_src_1", "decoy_consol_src_2", "decoy_consol_dest",
        ]:
            self.addr[label] = self._gen_addr()

        self.n_decoy_outputs = rng.randint(6, 9)
        self.addr["decoy_out"] = [self._gen_addr() for _ in range(self.n_decoy_outputs)]

        self.withdrawal = round(rng.uniform(180, 350), 4)
        self.vendor_amts = [round(rng.uniform(1.5, 15), 4) for _ in range(5)]
        mkt_fee = round(rng.uniform(0.1, 0.5), 4)
        self.to_intermediary = round(self.withdrawal - mkt_fee, 4)

        self.inter_operational = round(rng.uniform(2.0, 8.0), 4)
        self.to_tumbler = round(self.to_intermediary - self.inter_operational - round(rng.uniform(0.005, 0.02), 4), 4)

        tumbler_fee_pct = rng.uniform(0.01, 0.025)
        after_tumbler = self.to_tumbler * (1 - tumbler_fee_pct)
        split = rng.uniform(0.40, 0.60)
        self.tumb_out_1 = round(after_tumbler * split, 4)
        self.tumb_out_2 = round(after_tumbler * (1 - split), 4)
        self.tumb_total_hint = round(self.tumb_out_1 + self.tumb_out_2, 2)

        self.decoy_amts = []
        near_miss_placed = False
        for i in range(self.n_decoy_outputs):
            while True:
                a = round(rng.uniform(8, 120), 4)
                ok = True
                for prev in self.decoy_amts:
                    if abs(a + prev - self.tumb_total_hint) < 3:
                        ok = False
                        break
                if ok:
                    if i == 2 and not near_miss_placed and len(self.decoy_amts) >= 1:
                        a = round(self.tumb_total_hint - self.decoy_amts[0] + rng.uniform(3.5, 4.8), 4)
                        near_miss_placed = True
                    self.decoy_amts.append(a)
                    break

        self.other_dep_amts = [round(rng.uniform(10, 80), 4) for _ in range(3)]

        consol_fee = round(rng.uniform(0.001, 0.005), 4)
        self.consolidated = round(self.tumb_out_1 + self.tumb_out_2 - consol_fee, 4)

        pf1 = round(rng.uniform(1.0, 3.0), 4)
        self.peel1_fwd = round(self.consolidated - pf1, 4)
        pf2 = round(rng.uniform(0.5, 2.0), 4)
        self.peel2_fwd = round(self.peel1_fwd - pf2, 4)

        self.cj_other_amt_1 = round(rng.uniform(15, 45), 4)
        self.cj_other_amt_2 = round(rng.uniform(10, 30), 4)
        cj_total_in = self.peel2_fwd + self.cj_other_amt_1 + self.cj_other_amt_2
        self.cj_other_out_amt_1 = round(self.cj_other_amt_1 - rng.uniform(0.01, 0.05), 4)
        self.cj_other_out_amt_2 = round(self.cj_other_amt_2 - rng.uniform(0.01, 0.05), 4)
        pf3 = round(rng.uniform(0.3, 1.2), 4)
        self.peel3_fwd = round(cj_total_in - self.cj_other_out_amt_1 - self.cj_other_out_amt_2 - pf3, 4)

        pf4 = round(rng.uniform(0.2, 0.8), 4)
        self.peel4_fwd = round(self.peel3_fwd - pf4, 4)

        # Final hop: exchange_amt and change are CLOSE in value
        self.exchange_amt = round(self.peel4_fwd * rng.uniform(0.52, 0.58), 4)
        self.peel5_change = round(self.peel4_fwd - self.exchange_amt - 0.0001, 4)

        self.decoy_consol_amt = round(rng.uniform(40, 80), 4)

        self.transactions = {}
        self.address_txs = {}
        self._build_transactions()
        self._build_blog()
        self._build_forum()

    def _add_tx(self, txid, inputs, outputs, ts_str, fee=0.0001, memo=""):
        tx = {
            "txid": txid,
            "timestamp": ts_str,
            "block_height": 750000 + self.rng.randint(100, 9999),
            "confirmations": self.rng.randint(5000, 80000),
            "fee_btc": fee,
            "inputs": inputs,
            "outputs": outputs,
        }
        if memo:
            tx["op_return"] = memo
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

        for i, (v_lbl, amt) in enumerate(zip(
                ["vendor_1", "vendor_2", "vendor_3", "vendor_4", "vendor_5"],
                self.vendor_amts)):
            self._add_tx(self._gen_txid(),
                         [{"address": A["marketplace"], "amount": round(amt + 0.001, 4)}],
                         [{"address": A[v_lbl], "amount": amt}],
                         self._ts(self.t0, days=-rng.randint(3, 40)))

        self.withdrawal_txid = self._gen_txid()
        change_back = round(self.withdrawal - self.to_intermediary - 0.0005, 4)
        self._add_tx(self.withdrawal_txid,
                     [{"address": A["marketplace"], "amount": self.withdrawal}],
                     [{"address": A["intermediary"], "amount": self.to_intermediary},
                      {"address": A["mkt_change"], "amount": max(change_back, 0.0001)}],
                     self._ts(self.t0, hours=0))

        self.tumbler_txid = self._gen_txid()
        self._add_tx(self.tumbler_txid,
                     [{"address": A["intermediary"], "amount": self.to_intermediary}],
                     [{"address": A["tumbler_deposit"], "amount": self.to_tumbler},
                      {"address": A["inter_change"], "amount": self.inter_operational}],
                     self._ts(self.t0, hours=rng.randint(3, 10)))

        for dep_lbl, amt in zip(["other_dep_1", "other_dep_2", "other_dep_3"],
                                self.other_dep_amts):
            self._add_tx(self._gen_txid(),
                         [{"address": A[dep_lbl], "amount": round(amt + 0.001, 4)}],
                         [{"address": A["tumbler_deposit"], "amount": amt}],
                         self._ts(self.t0, hours=rng.randint(2, 14)))

        total_in = self.to_tumbler + sum(self.other_dep_amts)
        self._add_tx(self._gen_txid(),
                     [{"address": A["tumbler_deposit"], "amount": round(total_in, 4)}],
                     [{"address": A["tumbler_hot"], "amount": round(total_in - 0.002, 4)}],
                     self._ts(self.t0, hours=rng.randint(14, 30)))

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

        # Decoy consolidation
        self._add_tx(self._gen_txid(),
                     [{"address": A["decoy_consol_src_1"], "amount": round(self.decoy_consol_amt * 0.55, 4)},
                      {"address": A["decoy_consol_src_2"], "amount": round(self.decoy_consol_amt * 0.45, 4)}],
                     [{"address": A["decoy_consol_dest"], "amount": self.decoy_consol_amt}],
                     self._ts(self.t0, hours=rng.randint(52, 70)))

        # Real consolidation
        self.consolidation_txid = self._gen_txid()
        self._add_tx(self.consolidation_txid,
                     [{"address": A["op_tumb_out_1"], "amount": self.tumb_out_1},
                      {"address": A["op_tumb_out_2"], "amount": self.tumb_out_2}],
                     [{"address": A["consolidation"], "amount": self.consolidated}],
                     self._ts(self.t0, hours=rng.randint(55, 75)))

        # Peel chain
        peel_ts = rng.randint(78, 95)
        chg1 = round(self.consolidated - self.peel1_fwd - 0.0001, 4)
        self._add_tx(self._gen_txid(),
                     [{"address": A["consolidation"], "amount": self.consolidated}],
                     [{"address": A["peel_1"], "amount": self.peel1_fwd},
                      {"address": A["peel_change_1"], "amount": max(chg1, 0.0001)}],
                     self._ts(self.t0, hours=peel_ts))
        peel_ts += rng.randint(2, 6)

        chg2 = round(self.peel1_fwd - self.peel2_fwd - 0.0001, 4)
        self._add_tx(self._gen_txid(),
                     [{"address": A["peel_1"], "amount": self.peel1_fwd}],
                     [{"address": A["peel_2"], "amount": self.peel2_fwd},
                      {"address": A["peel_change_2"], "amount": max(chg2, 0.0001)}],
                     self._ts(self.t0, hours=peel_ts))
        peel_ts += rng.randint(2, 6)

        # CoinJoin hop 3
        cj_txid = self._gen_txid()
        self._add_tx(cj_txid,
                     [{"address": A["peel_2"], "amount": self.peel2_fwd},
                      {"address": A["cj_other_in_1"], "amount": self.cj_other_amt_1},
                      {"address": A["cj_other_in_2"], "amount": self.cj_other_amt_2}],
                     [{"address": A["peel_3"], "amount": self.peel3_fwd},
                      {"address": A["cj_other_out_1"], "amount": self.cj_other_out_amt_1},
                      {"address": A["cj_other_out_2"], "amount": self.cj_other_out_amt_2},
                      {"address": A["peel_change_3"], "amount": round(rng.uniform(0.01, 0.1), 4)}],
                     self._ts(self.t0, hours=peel_ts),
                     fee=0.0003)
        peel_ts += rng.randint(3, 8)

        chg4 = round(self.peel3_fwd - self.peel4_fwd - 0.0001, 4)
        self._add_tx(self._gen_txid(),
                     [{"address": A["peel_3"], "amount": self.peel3_fwd}],
                     [{"address": A["peel_4"], "amount": self.peel4_fwd},
                      {"address": A["peel_change_4"], "amount": max(chg4, 0.0001)}],
                     self._ts(self.t0, hours=peel_ts))
        peel_ts += rng.randint(1, 4)

        # Final hop — close amounts
        self._add_tx(self._gen_txid(),
                     [{"address": A["peel_4"], "amount": self.peel4_fwd}],
                     [{"address": A["exchange_deposit"], "amount": self.exchange_amt},
                      {"address": A["peel_change_5"], "amount": self.peel5_change}],
                     self._ts(self.t0, hours=peel_ts))

    def _build_blog(self):
        A = self.addr
        self.articles = [
            {
                "id": 1,
                "title": f"International Operation Takes Down {self.marketplace} — Dozens Arrested Worldwide",
                "author": self.journalist,
                "date": self._ts(self.t0, days=3),
                "tags": [self.marketplace.lower(), "darknet", "seizure", "international"],
                "content": (
                    f"BREAKING: In one of the most significant coordinated law enforcement operations "
                    f"this year, authorities across 14 countries have taken down {self.marketplace}, "
                    f"a darknet marketplace that facilitated the sale of prohibited goods and services "
                    f"since early 2021.\n\n"
                    f"The operation, codenamed 'SilkThread', resulted in the arrest of 37 individuals "
                    f"connected to vendor operations on the platform. However, the site's administrator, "
                    f'known only as "{self.operator_alias}", remains at large.\n\n'
                    f"Europol spokesperson Jana Müller stated: 'While the infrastructure has been seized, "
                    f"our primary target — the platform operator — managed to withdraw significant "
                    f"cryptocurrency holdings before the takedown. Our financial investigation unit is "
                    f"actively tracing these funds.'\n\n"
                    f"The marketplace primarily used Bitcoin for transactions. Court documents mention "
                    f"that the platform processed an estimated $40 million in total transaction volume "
                    f"over its operational lifetime. The administrator reportedly took a 4-6% commission "
                    f"on each sale.\n\n"
                    f"This article will be updated as more details emerge. For the blockchain analysis "
                    f"component of this investigation, see our follow-up report."
                ),
            },
            {
                "id": 2,
                "title": f"Blockchain Forensics: Tracing the {self.marketplace} Money Trail",
                "author": self.journalist,
                "date": self._ts(self.t0, days=6),
                "tags": ["bitcoin", "forensics", "blockchain", self.marketplace.lower()],
                "content": (
                    f"In our detailed blockchain analysis of the {self.marketplace} case, we examined "
                    f"the on-chain activity patterns associated with the platform.\n\n"
                    f"Darknet marketplaces typically employ a multi-wallet architecture. Buyer deposits "
                    f"flow into escrow addresses, vendor payouts come from operational hot wallets, and "
                    f"the administrator maintains one or more treasury addresses for commission revenue. "
                    f"In the case of {self.marketplace}, we identified several address clusters through "
                    f"heuristic analysis.\n\n"
                    f"The primary commission wallet — which received the operator's share of all platform "
                    f"fees — has been identified by cross-referencing transaction timing with the platform's "
                    f"known payout schedule. This address handled the bulk of {self.operator_alias}'s "
                    f"personal funds:\n\n"
                    f"    {A['marketplace']}\n\n"
                    f"Note that this is distinct from the platform's escrow system, which used a separate "
                    f"set of addresses. The escrow addresses are not relevant to tracing the operator's "
                    f"personal withdrawal.\n\n"
                    f"Prior to the seizure, the wallet showed a pattern of regular outbound transactions — "
                    f"likely vendor payouts and operational expenses. However, our analysis flagged one "
                    f"anomalous transaction that occurred approximately around the time of the 'maintenance' "
                    f"announcement: a significantly larger-than-usual outbound transfer. This is the "
                    f"transaction of interest for tracing the operator's exit funds.\n\n"
                    f"Importantly, the funds did NOT go directly to an exchange. Our preliminary analysis "
                    f"suggests at least one intermediate hop before the trail becomes obscured — possibly "
                    f"through a mixing service. We are still working to confirm which service was used.\n\n"
                    f"[Editor's note: we have intentionally omitted transaction hashes from this report "
                    f"to avoid tipping off the subject. The addresses and amounts can be verified "
                    f"independently via any blockchain explorer.]"
                ),
            },
            {
                "id": 3,
                "title": "The Rising Tide: 2024's Wave of Darknet Market Seizures",
                "author": self.journalist,
                "date": self._ts(self.t0, days=8),
                "tags": ["darknet", "seizure", "trend", "law-enforcement"],
                "content": (
                    f"The takedown of {self.marketplace} is part of a broader trend. In the past year "
                    f"alone, law enforcement has seized or disrupted at least seven major darknet "
                    f"platforms.\n\n"
                    f"Unlike previous generation markets like Silk Road and AlphaBay, modern platforms "
                    f"employ sophisticated anti-forensics techniques. Multi-sig escrow, automatic tumbling, "
                    f"and Monero support have made tracing funds increasingly difficult.\n\n"
                    f"Interestingly, several of these platforms appear to share infrastructure. Our "
                    f"analysis uncovered IP address overlaps between {self.marketplace} and at least two "
                    f"other seized platforms. Whether this indicates a common hosting provider or a "
                    f"deeper operational connection remains unclear.\n\n"
                    f"The crypto forensics firm Elliptic noted that marketplace operators are increasingly "
                    f"using 'chain-hopping' — converting Bitcoin to Monero, then back to Bitcoin through "
                    f"a different service — to break the chain of custody. However, in the "
                    f"{self.marketplace} case, the operator appears to have relied primarily on "
                    f"traditional Bitcoin mixing, suggesting either urgency or overconfidence in older "
                    f"obfuscation methods."
                ),
            },
            {
                "id": 4,
                "title": f'"{self.operator_alias} Made Mistakes" — Inside the Hunt for {self.marketplace}\'s Admin',
                "author": self.journalist,
                "date": self._ts(self.t0, days=12),
                "tags": [self.operator_alias, "investigation", "community", self.marketplace.lower()],
                "content": (
                    f"We spoke with a source close to the investigation who requested anonymity. "
                    f"According to them, {self.operator_alias} made several operational security mistakes "
                    f"in the days leading up to the {self.marketplace} seizure.\n\n"
                    f'"The withdrawal pattern was sloppy," our source said. "Instead of using multiple '
                    f"small transactions over weeks, the bulk of the funds were moved in essentially one "
                    f"large sweep. That makes it much easier to follow.\"\n\n"
                    f"Our source also confirmed that independent investigators on the {self.forum} forum "
                    f"have been conducting their own parallel analysis. \"Some of those forum posts have "
                    f"legitimate intelligence, but be careful — there's also deliberate misinformation "
                    f"being planted. At least one post we've seen contains fabricated exchange data to "
                    f"throw off investigators.\"\n\n"
                    f"When asked about the use of mixing services, the source would only confirm that "
                    f"\"a known tumbler was involved\" but declined to name it, citing the ongoing "
                    f"investigation.\n\n"
                    f"We also asked about the endgame — where the funds ultimately ended up. "
                    f'"We believe the operator converted back to fiat through a centralized exchange, '
                    f"which means there should be KYC records. But the path from the mixer to the "
                    f'exchange is convoluted — multiple hops, possibly including a CoinJoin transaction '
                    f'to further obscure the trail."'
                ),
            },
            {
                "id": 5,
                "title": "How Bitcoin Tumblers Work — And Why They Don't Always Protect You",
                "author": self.journalist,
                "date": self._ts(self.t0, days=15),
                "tags": ["tumbler", "mixer", "bitcoin", "explainer", "forensics"],
                "content": (
                    f"Bitcoin tumblers, also known as mixers, are services that attempt to break the "
                    f"link between the sender and receiver of cryptocurrency. They work by pooling "
                    f"multiple users' deposits and redistributing them in randomized amounts.\n\n"
                    f"In a typical mixing operation:\n"
                    f"1. The user deposits Bitcoin to a designated address\n"
                    f"2. The mixer aggregates deposits in a hot wallet\n"
                    f"3. After a delay, funds are sent out in split amounts to user-specified addresses\n"
                    f"4. A service fee (typically 1-3%) is retained\n\n"
                    f"The key weakness is correlation analysis. If a user deposits X BTC and the mixer "
                    f"outputs two amounts that sum to approximately X minus the fee, the link can be "
                    f"reestablished — especially if the timing correlates.\n\n"
                    f"In the {self.marketplace} case, we've heard unconfirmed reports that the service "
                    f"{self.second_tumbler} was involved. However, this conflicts with other intelligence "
                    f"suggesting a different mixing service was used. The discrepancy may indicate that "
                    f"the operator used multiple tumbling stages, or that one of the reports is simply "
                    f"wrong.\n\n"
                    f"[Correction, published {self._ts(self.t0, days=17)}: A previous version of this "
                    f"article stated that {self.second_tumbler} was definitively identified as the "
                    f"mixer. We have updated the language to reflect the uncertainty.]"
                ),
            },
        ]

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
                "title": f"Tracking {self.operator_alias} — mixing service identified",
                "date": self._ts(base_forum_ts, hours=0),
                "tags": [self.operator_alias, "opsec", "tumbler", "tracing"],
                "content": (
                    f"I've been tracking {self.operator_alias}'s on-chain movements since the "
                    f"{self.marketplace} exit. After the funds left the marketplace wallet, they "
                    f"went through a single intermediary hop before entering a mixing service.\n\n"
                    f"The tumbler used is {self.tumbler}. I've confirmed this by matching the deposit "
                    f"pattern with {self.tumbler}'s known hot wallet behavior.\n\n"
                    f"The operator split the tumbled output into exactly TWO receiving addresses. "
                    f"I haven't identified which outputs belong to {self.operator_alias} yet — the "
                    f"mixer had several users depositing around the same time — but I'm working on "
                    f"the correlation analysis. Will update soon."
                ),
            },
            {
                "id": 3,
                "author": "forensics_pro",
                "title": f"RE: Tracking {self.operator_alias} — I think it was {self.second_tumbler}",
                "date": self._ts(base_forum_ts, hours=6),
                "tags": [self.operator_alias, self.second_tumbler.lower(), "tumbler"],
                "content": (
                    f"@{self.informant} I disagree. I've been doing my own analysis and the mixing "
                    f"pattern matches {self.second_tumbler}, not {self.tumbler}. The timing gaps between "
                    f"deposit and output are consistent with {self.second_tumbler}'s 6-12 hour delay "
                    f"window.\n\n"
                    f"Also, {self.tumbler} requires a minimum deposit of 0.5 BTC and the intermediary "
                    f"transaction I found sent much less than that. I think you're looking at the wrong "
                    f"service.\n\n"
                    f"EDIT: Attaching the intermediary address I found: {A['inter_change']}\n"
                    f"Follow this one, not {self.informant}'s lead."
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
                "author": "anon_tipster",
                "title": f"CONFIRMED: {self.red_herring_alias} = {self.marketplace} operator",
                "date": self._ts(base_forum_ts, days=3),
                "tags": [self.marketplace.lower(), "confirmed", self.red_herring_alias, "identity"],
                "content": (
                    f"I can now CONFIRM that {self.red_herring_alias} is the real person behind "
                    f"{self.marketplace}. My sources within the DEA investigation have identified the "
                    f"operator as {self.red_herring_name_1}.\n\n"
                    f"This individual was flagged by {self.fake_exchange} compliance after depositing "
                    f"funds traceable to the {self.marketplace} hot wallet. The KYC documents show:\n\n"
                    f"    Name: {self.red_herring_name_1}\n"
                    f"    Exchange: {self.fake_exchange}\n"
                    f"    Account: {self.fake_exchange_handle}\n\n"
                    f"I'm confident in this. The trail checks out.\n\n"
                    f"[Thread locked by moderator — unverified claims]"
                ),
            },
            {
                "id": 7,
                "author": "btc_tracer",
                "title": f"FOUND IT — {self.operator_alias}'s exchange deposit address",
                "date": self._ts(base_forum_ts, days=4),
                "tags": [self.operator_alias, "exchange", "deposit", "found"],
                "content": (
                    f"After 3 days of non-stop blockchain analysis, I've traced {self.operator_alias}'s "
                    f"funds all the way to the exchange. Here's the deposit address:\n\n"
                    f"    {A['fake_exchange_addr']}\n\n"
                    f"This is the final destination. The exchange is {self.fake_exchange} and the "
                    f"account holder is {self.red_herring_name_2}.\n\n"
                    f"You can verify this yourself by following the peel chain from the consolidation "
                    f"wallet. It's straightforward."
                ),
            },
            {
                "id": 8,
                "author": self.informant,
                "title": f"Correlation results for {self.tumbler} outputs — updated",
                "date": self._ts(base_forum_ts, hours=36),
                "tags": [self.operator_alias, "tumbler", "correlation", "analysis"],
                "content": (
                    f"Update on my {self.tumbler} analysis.\n\n"
                    f"I've been running timing correlation and amount analysis on the mixer's "
                    f"output transaction. The hot wallet sprayed outputs to {2 + self.n_decoy_outputs} "
                    f"different addresses in a single transaction.\n\n"
                    f"Here's what I found: based on the deposit amount that entered {self.tumbler} "
                    f"(minus the typical 1-2.5% fee), {self.operator_alias}'s combined output should "
                    f"be in the ballpark of {self.tumb_total_hint:.2f} BTC, distributed across two "
                    f"addresses.\n\n"
                    f"IMPORTANT: There are some near-miss pairs in the outputs. Don't just grab "
                    f"the first two that seem close — verify by checking if both addresses consolidate "
                    f"to the same destination. That's the definitive test.\n\n"
                    f"I haven't been able to complete the full trace beyond the consolidation point yet. "
                    f"The trail gets complicated — looks like there might be a CoinJoin involved."
                ),
            },
            {
                "id": 9,
                "author": "skeptic99",
                "title": f"PSA: Most 'intel' in this forum about {self.marketplace} is WRONG",
                "date": self._ts(base_forum_ts, days=5),
                "tags": [self.marketplace.lower(), "warning", "misinformation"],
                "content": (
                    f"I've been watching the {self.marketplace} threads for a week now and the "
                    f"amount of misinformation is staggering.\n\n"
                    f"- @anon_tipster's 'confirmed' identity is almost certainly wrong. No DEA source "
                    f"would leak KYC to a random forum poster.\n"
                    f"- @btc_tracer's 'found' exchange address looks fabricated. I checked it and "
                    f"there's no on-chain activity matching the expected pattern.\n"
                    f"- Even @{self.informant}'s analysis has issues. The tumbler identification "
                    f"might be correct, but the amount estimate could be off if the fee percentage "
                    f"assumption is wrong.\n\n"
                    f"My advice: TRUST NOTHING except what you can verify on-chain yourself. "
                    f"Every piece of forum 'intelligence' needs independent blockchain confirmation."
                ),
            },
            {
                "id": 10,
                "author": self.leaker,
                "title": f"Compliance alert from {self.exchange} — account flagged",
                "date": self._ts(base_forum_ts, days=6),
                "tags": [self.exchange.lower(), "compliance", "flag", "alert"],
                "content": (
                    f"I have a contact at {self.exchange}'s compliance department. They told me "
                    f"an account was flagged last week for receiving funds that trace back to the "
                    f"{self.marketplace} laundering chain.\n\n"
                    f'The account is registered under the handle "{self.exchange_handle}". '
                    f"My contact says the flagged deposit arrived through a multi-hop chain "
                    f"originating from what they believe is a post-tumbler consolidation.\n\n"
                    f"I'm trying to get the KYC documents. Will post when I have them.\n\n"
                    f"NOTE: I am NOT providing the deposit address because I don't have it. "
                    f"My contact only shared the account handle and the fact it was flagged. "
                    f"You'll need to trace the blockchain yourself to find the address."
                ),
            },
            {
                "id": 11,
                "author": "chain_analyst",
                "title": f"RE: Correlation results — @{self.informant}'s numbers are wrong",
                "date": self._ts(base_forum_ts, hours=48),
                "tags": [self.operator_alias, "tumbler", "correction"],
                "content": (
                    f"@{self.informant}'s estimate of ~{self.tumb_total_hint:.2f} BTC is based on "
                    f"the assumption that {self.tumbler} charges 1-2.5% fee. But I happen to know "
                    f"that {self.tumbler} recently changed their fee to 3-4% for large deposits.\n\n"
                    f"Corrected estimate: the operator's outputs should sum to approximately "
                    f"**{round(self.tumb_total_hint * 0.85, 2):.2f} BTC**.\n\n"
                    f"Use my number, not the old one. @{self.informant} hasn't accounted for the "
                    f"fee change."
                ),
            },
            {
                "id": 12,
                "author": self.leaker,
                "title": f"KYC obtained: {self.exchange} account identity revealed",
                "date": self._ts(base_forum_ts, days=8),
                "tags": [self.exchange_handle, "kyc", "identity", self.exchange.lower()],
                "content": (
                    f"Got the documents. The KYC verification for the \"{self.exchange_handle}\" "
                    f"account on {self.exchange} shows:\n\n"
                    f"    Name: {self.real_name}\n"
                    f"    Verification: Government ID + proof of address\n"
                    f"    Account status: Frozen pending investigation\n\n"
                    f"This is the person who controlled the endpoint of the laundering chain from "
                    f"{self.marketplace}. To verify, you need to independently trace the blockchain "
                    f"path from the marketplace through the tumbler and subsequent hops to confirm "
                    f"the deposit address belongs to this account.\n\n"
                    f"I know there are other names floating around in this forum. I can only vouch "
                    f"for this one — I've seen the actual documents."
                ),
            },
            {
                "id": 13,
                "author": "d0xx_squad",
                "title": f"DOXED: {self.operator_alias} is {self.red_herring_name_3}",
                "date": self._ts(base_forum_ts, days=7),
                "tags": [self.operator_alias, "dox", "identity"],
                "content": (
                    f"We got him. After cross-referencing PGP key metadata with LinkedIn profiles, "
                    f"we've identified {self.operator_alias} as {self.red_herring_name_3}.\n\n"
                    f"This individual has a background in computer science and was previously "
                    f"associated with a cryptocurrency exchange startup that went bankrupt in 2022. "
                    f"The timing matches perfectly with when {self.marketplace} started gaining "
                    f"traction.\n\n"
                    f"We're 95% confident. Forwarding this to law enforcement."
                ),
            },
            {
                "id": 14,
                "author": "exchange_watcher",
                "title": f"It wasn't {self.exchange} — the funds went to {self.fake_exchange}",
                "date": self._ts(base_forum_ts, days=6, hours=12),
                "tags": [self.fake_exchange.lower(), "exchange", "dispute"],
                "content": (
                    f"@{self.leaker} is wrong about {self.exchange}. I've been monitoring "
                    f"{self.fake_exchange}'s deposit patterns and there's a large incoming transfer "
                    f"that matches the expected amount and timing from the {self.marketplace} trail.\n\n"
                    f"The deposit address on {self.fake_exchange} is:\n\n"
                    f"    {A['fake_exchange_addr']}\n\n"
                    f"This matches the output of the peel chain. {self.leaker}'s {self.exchange} lead "
                    f"is a dead end.\n\n"
                    f"Also, the account holder on {self.fake_exchange} is {self.red_herring_name_2} — "
                    f"same name btc_tracer found independently. Two sources, same name. That's not "
                    f"a coincidence."
                ),
            },
            {
                "id": 15,
                "author": self.informant,
                "title": f"CoinJoin detected in the {self.operator_alias} peel chain",
                "date": self._ts(base_forum_ts, days=4, hours=6),
                "tags": [self.operator_alias, "coinjoin", "peel-chain", "analysis"],
                "content": (
                    f"Heads up for anyone tracing the peel chain after the consolidation.\n\n"
                    f"Around hop 3, the operator's funds enter a CoinJoin transaction — meaning "
                    f"multiple unrelated inputs are combined into a single transaction with multiple "
                    f"outputs. This is designed to break heuristic clustering.\n\n"
                    f"To find the operator's output in the CoinJoin:\n"
                    f"- Look at the input amounts. The operator's input is the continuation of the "
                    f"peel chain — its amount should be consistent with the prior hop minus a small "
                    f"change output.\n"
                    f"- The output that continues the operator's chain will be close to (but slightly "
                    f"less than) their input amount, after accounting for the other participants' "
                    f"inputs and outputs.\n\n"
                    f"Don't just 'follow the largest output' after the CoinJoin — that might be one "
                    f"of the other participants' outputs. You need to do the math.\n\n"
                    f"Also note: the final hop of the peel chain has two outputs that are VERY close "
                    f"in amount. The forward payment and change are almost equal. Be careful."
                ),
            },
            {
                "id": 16,
                "author": "on_chain_sleuth",
                "title": f"Found the consolidation wallet for {self.operator_alias}",
                "date": self._ts(base_forum_ts, days=3, hours=18),
                "tags": [self.operator_alias, "consolidation", "wallet", "found"],
                "content": (
                    f"After checking tumbler outputs, I found two addresses that consolidated "
                    f"into a single wallet:\n\n"
                    f"    Source 1: {A['decoy_consol_src_1']}\n"
                    f"    Source 2: {A['decoy_consol_src_2']}\n"
                    f"    Destination: {A['decoy_consol_dest']}\n\n"
                    f"This is {self.operator_alias}'s consolidation. Follow the trail from here."
                ),
            },
            {
                "id": 17,
                "author": self.operator_alias,
                "title": "Best practices for tumbler OPSEC?",
                "date": self._ts(self.t0, days=-60),
                "tags": ["opsec", "tumbler", "question"],
                "content": (
                    f"Hypothetical question: if you needed to move a significant amount through "
                    f"a tumbler, would you split the output into 2 addresses or more? I've heard "
                    f"splitting into exactly 2 is safer than 3+ because fewer data points for "
                    f"correlation analysis.\n\n"
                    f"Also, what's the optimal delay between receiving tumbled output and "
                    f"consolidating? Asking for... research purposes.\n\n"
                    f"— {self.operator_alias}"
                ),
            },
            {
                "id": 18,
                "author": "truth_seeker",
                "title": f"@{self.leaker} got the wrong person — real identity inside",
                "date": self._ts(base_forum_ts, days=9),
                "tags": ["identity", "correction", self.exchange.lower()],
                "content": (
                    f"I've done my own investigation into the {self.exchange} account flagged by "
                    f"@{self.leaker}. The KYC name \"{self.real_name}\" is a STOLEN IDENTITY. "
                    f"The account was opened with forged documents.\n\n"
                    f"The REAL person behind {self.operator_alias} is {self.red_herring_name_1}. "
                    f"I have evidence from a separate investigation that links this individual "
                    f"to the {self.marketplace} PGP key through keyserver metadata.\n\n"
                    f"Don't submit the KYC name — submit the real one: {self.red_herring_name_1}."
                ),
            },
            {
                "id": 19,
                "author": "anon_observer",
                "title": f"Timeline of the {self.marketplace} collapse — comprehensive",
                "date": self._ts(base_forum_ts, days=10),
                "tags": [self.marketplace.lower(), "timeline", "summary"],
                "content": (
                    f"Putting together everything from this forum and the blog:\n\n"
                    f"Day 0: {self.operator_alias} announces 'maintenance' on {self.marketplace}\n"
                    f"Day 0: Funds withdrawn from marketplace wallet in a single large transaction\n"
                    f"Day 0-1: Funds moved through intermediary to mixing service\n"
                    f"Day 1-2: Mixing completes, outputs distributed to multiple addresses\n"
                    f"Day 2-3: Operator consolidates their two mixer outputs\n"
                    f"Day 3-4: Peel chain begins (multiple hops, includes CoinJoin)\n"
                    f"Day 4-5: Funds arrive at exchange deposit address\n\n"
                    f"Key facts established:\n"
                    f"- Tumbler: {self.tumbler} (confirmed by {self.informant}, disputed by others)\n"
                    f"- Exchange: disputed between {self.exchange} and {self.fake_exchange}\n"
                    f"- Identity: at least 3 different names claimed — "
                    f"{self.red_herring_name_1}, {self.red_herring_name_2}, {self.red_herring_name_3}\n"
                    f"  (plus {self.real_name} from KYC leak)\n\n"
                    f"The only way to determine the truth is to trace the blockchain end-to-end. "
                    f"Forum intelligence alone is insufficient and contradictory."
                ),
            },
            {
                "id": 20,
                "author": "mod_darknet",
                "title": f"Moderator note on {self.marketplace} investigation threads",
                "date": self._ts(base_forum_ts, days=9, hours=12),
                "tags": [self.marketplace.lower(), "moderator", "verification"],
                "content": (
                    f"As forum moderator, I want to address the credibility dispute.\n\n"
                    f"@{self.leaker} has provided verified intelligence in previous investigations "
                    f"(Operation BlackStar, MorpheusDNM takedown). Their track record on exchange "
                    f"leaks is solid. This doesn't mean they're infallible, but their {self.exchange} "
                    f"source has been reliable in the past.\n\n"
                    f"@anon_tipster and @btc_tracer have no verification history on this forum. "
                    f"Their claims about {self.fake_exchange} have not been corroborated.\n\n"
                    f"@truth_seeker's 'stolen identity' claim is possible but unsubstantiated. "
                    f"Without evidence, the KYC documentation from @{self.leaker} carries more weight.\n\n"
                    f"As always: verify everything on-chain. Forum posts are leads, not evidence."
                ),
            },
        ]

    # Tool handlers
    def get_briefing(self):
        return {
            "title": f"CASE BRIEFING: Operation SilkThread — {self.marketplace} Investigation",
            "classification": "CONFIDENTIAL",
            "summary": (
                f"You are tasked with investigating the operator of {self.marketplace}, "
                f"a recently seized darknet marketplace. The operator is known by the alias "
                f'"{self.operator_alias}". Your objective is to trace the cryptocurrency withdrawn '
                f"from the marketplace, follow the money through any laundering layers, and identify "
                f"both the final cash-out wallet and the operator's real identity."
            ),
            "starting_leads": [
                f'Investigative journalist {self.journalist} has published articles on the blog "{self.blog}".',
                f'The darknet forum "{self.forum}" may contain community discussion and OSINT leads.',
            ],
            "objective": (
                "Identify TWO things:\n"
                "  1. The FINAL wallet address where the operator cashed out\n"
                "  2. The REAL NAME of the marketplace operator\n\n"
                "Use the submit_answer tool with both values when ready.\n"
                "WARNING: You have only ONE attempt. Make it count."
            ),
            "advisory": (
                "NOTE: Multiple sources may provide conflicting information. "
                "Forum posts may contain deliberate misinformation. "
                "Only blockchain evidence is definitive. Verify all claims on-chain."
            ),
        }

    def search_blog(self, query):
        query_lower = query.lower()
        results = []
        for art in self.articles:
            text = (art["title"] + " " + art["content"] + " " + " ".join(art["tags"])).lower()
            if any(w in text for w in query_lower.split()):
                results.append({
                    "id": art["id"], "title": art["title"], "author": art["author"],
                    "date": art["date"], "snippet": art["content"][:200] + "...",
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
                    "id": post["id"], "title": post["title"], "author": post["author"],
                    "date": post["date"], "snippet": post["content"][:180] + "...",
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
            return {"error": f"Address {address} not found on the blockchain.",
                    "suggestion": "Double-check the address string."}
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
            return {"error": f"Transaction {txid} not found.",
                    "suggestion": "Double-check the transaction hash."}
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
            hints.append("The wallet address is INCORRECT.")
        if not name_ok:
            hints.append("The owner name is INCORRECT.")
        return {
            "success": False, "message": "Incorrect submission.",
            "hints": hints, "attempts_remaining": MAX_SUBMIT_ATTEMPTS - self.submit_attempts,
        }


SCENARIO = None

def get_scenario():
    global SCENARIO
    if SCENARIO is None:
        seed_env = os.environ.get("SILKTHREAD_SEED")
        seed = int(seed_env) if seed_env else None
        SCENARIO = BlockchainScenario(seed=seed)
    return SCENARIO


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
                {"name": "get_briefing", "description": "Get the initial case briefing.", "arguments": []},
                {"name": "search_blog", "description": "Search blog articles by keyword.",
                 "arguments": [{"name": "query", "type": "str", "required": True, "description": "Search keywords"}]},
                {"name": "read_article", "description": "Read a blog article by ID.",
                 "arguments": [{"name": "article_id", "type": "int", "required": True, "description": "Article ID"}]},
                {"name": "search_forum", "description": "Search forum posts by keyword.",
                 "arguments": [{"name": "query", "type": "str", "required": True, "description": "Search keywords"}]},
                {"name": "read_post", "description": "Read a forum post by ID.",
                 "arguments": [{"name": "post_id", "type": "int", "required": True, "description": "Post ID"}]},
                {"name": "explore_address", "description": "Look up all transactions for a Bitcoin address.",
                 "arguments": [{"name": "address", "type": "str", "required": True, "description": "Bitcoin address"}]},
                {"name": "get_transaction", "description": "Get full details of a transaction by hash.",
                 "arguments": [{"name": "txid", "type": "str", "required": True, "description": "Transaction hash"}]},
                {"name": "submit_answer",
                 "description": "Submit your investigation findings.",
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
    p = argparse.ArgumentParser(description="MCP SilkThread Server (Hardened)")
    p.add_argument("--port", type=int, default=7001)
    args = p.parse_args()

    s = get_scenario()
    print(f"SilkThread HARDENED scenario generated (seed={s.seed})")
    print(f"  Marketplace: {s.marketplace}")
    print(f"  Operator alias: {s.operator_alias}")
    print(f"  Real name: {s.real_name} (ANSWER)")
    print(f"  Exchange deposit: {s.addr['exchange_deposit']} (ANSWER)")
    print(f"  Tumbler: {s.tumbler}")
    print(f"  Withdrawal: {s.withdrawal} BTC")
    print(f"  Tumbler outputs (operator): {s.tumb_out_1} + {s.tumb_out_2} = {s.tumb_total_hint} BTC")
    print(f"  Exchange deposit amount: {s.exchange_amt} BTC")
    print(f"  Red herring names: {s.red_herring_name_1}, {s.red_herring_name_2}, {s.red_herring_name_3}")
    print(f"  Fake exchange: {s.fake_exchange}")
    print(f"  Fake exchange addr: {s.addr['fake_exchange_addr']}")
    print(f"  Decoy consol dest: {s.addr['decoy_consol_dest']}")
    print(f"  Blog articles: {len(s.articles)}")
    print(f"  Forum posts: {len(s.posts)}")
    print(f"  Blockchain addresses: {len(s.address_txs)}")
    print(f"  Transactions: {len(s.transactions)}")

    server = HTTPServer(("0.0.0.0", args.port), SilkThreadRPCHandler)
    print(f"MCP SilkThread Server listening on port {args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
