# All-In Agent — Writeup (Hardened Version)

## Panoramica della Challenge

La challenge presenta un tavolo di Texas Hold'em a 4 giocatori dove un agente AI deve accumulare **3,500 chips** partendo da **1,000** in un massimo di **50 mani**. I tre avversari (Alice, Bob, Charlie) hanno strategie distinte ma **nessuna informazione viene fornita** al risolutore riguardo al loro stile di gioco.

### Differenze dalla versione originale

| Parametro | Originale | Hardened |
|-----------|-----------|----------|
| Target chips | 2,500 | 3,500 |
| Mani massime | 80 | 50 |
| Nomi bot | Donkey, Rock, Maniac | Alice, Bob, Charlie |
| Style hints in `get_table_info` | Sì | No |
| Strategy Tips nel README | Sì | No |
| Descrizione bot in challengish.yml | Esplicita | Nessuna |
| Descrizioni tool | Verbose con suggerimenti | Minimali |

### Cosa rende la challenge difficile

1. **Nessuna informazione sugli avversari**: i nomi (Alice, Bob, Charlie) non suggeriscono lo stile di gioco. Il campo `style_hint` è stato rimosso da `get_table_info`.
2. **Budget temporale stretto**: guadagnare +2,500 chips netti in 50 mani con blind 25/50 richiede un win rate aggressivo (~50 chips/mano netti).
3. **L'agente deve dedurre le strategie**: usando `get_hand_history` e osservando i pattern nel `hand_log`, l'agente deve capire chi è il calling station, chi è tight e chi è aggressivo.

---

## Profili Nascosti dei Bot (dalla sorgente)

L'agente non riceve queste informazioni — deve scoprirle dall'osservazione.

### Alice (ex-Donkey) — Passive Calling Station
- **Preflop**: check/small bet. Quando affronta una puntata, calla il 92% delle volte.
- **Fold rate**: bassissimo. Folda solo su puntate enormi (>80% del suo stack) con 30% di probabilità.
- **Exploit**: value bet aggressivo con qualsiasi mano decente. Non bluffare mai — Alice non folda.

### Bob (ex-Rock) — Ultra-Tight
- **Preflop**: gioca solo mani premium (88+, AJ+, KQ). Folda tutto il resto.
- **Postflop**: se ha pair+, continua. Con high card e bet alta, folda.
- **Exploit**: rubare i suoi blind con raise leggeri. Quando Bob rilancia, ha una mano forte → fold.

### Charlie (ex-Maniac) — Hyper-Aggressive
- **Preflop**: rilancia il 55% delle volte anche senza bet da affrontare.
- **Facing a bet**: rilancia 35%, calla 50%, folda 15%. Folda di più su bet enormi.
- **Exploit**: trappolare con mani forti. Chiamare i suoi raise e lasciare che bluffi nelle street successive.

---

## Strategia Risolutiva

### Fase 1: Ricognizione (Scout)
L'agente deve:
1. Chiamare `get_table_info` per i parametri base (blinds, target, stacks)
2. Chiamare `get_game_state` per vedere la prima mano
3. **NON ricevere alcuna informazione sullo stile** — deve costruirsi un modello dagli eventi

### Fase 2: Gioco e Osservazione (Player)
L'agente deve giocare e simultaneamente osservare:
- Chi calla quasi sempre → Alice (calling station)
- Chi folda quasi sempre preflop → Bob (tight)
- Chi rilancia frequentemente, anche con mani deboli → Charlie (aggressive)

### Fase 3: Exploit Adattivo
Dopo 5-10 mani di osservazione:
- **Contro Alice**: value bet qualsiasi pair o meglio. Mai bluffare.
- **Contro Bob**: raise per rubare blind. Fold se Bob re-raise.
- **Contro Charlie**: trap con mani forti. Chiamare i suoi bluff.

### Preflop Hand Chart

**Tier 1 — PREMIUM** (raise 3x BB = 150):
- Pairs: AA, KK, QQ, JJ, TT
- Broadway: AK, AQs

**Tier 2 — STRONG** (raise 2.5x BB = 125):
- Pairs: 99, 88
- Broadway: AQo, AJs, KQs

**Tier 3 — PLAYABLE** (call 1 BB, fold a raise grande):
- Pairs: 77, 66, 55
- Suited connectors: QJs, JTs, T9s, 98s, 87s

**Tier 4 — JUNK**: fold.

### Postflop Framework

| Forza mano | Azione |
|------------|--------|
| Monster (two pair+) | Bet/raise aggressivo, all-in se il pot è grosso |
| Strong (top pair, buon kicker) | Bet 50-75% pot |
| Medium (middle/bottom pair) | Check/call piccole bet |
| Draw (4 to flush/straight) | Call se prezzo < 25% pot |
| Nothing | Check/fold |

---

## Architettura della Soluzione (ASL Bundle)

### Struttura del Workflow

```
EntryPoint → SCOUT (LLMNode) → ScoutWorker (WorkerNode)
                               → PLAYER (LLMNode)
```

**3 nodi + 1 entry point:**

1. **EntryPoint**: inizializza lo state (`strategy`, `flag`, `game_report`)
2. **SCOUT** (LLMNode): orchestra la ricognizione e produce un briefing strategico
3. **ScoutWorker** (WorkerNode): esegue `get_table_info` + `get_game_state` + `get_hand_history`
4. **PLAYER** (LLMNode): gioca la partita usando la strategia e i tool di azione

### Differenze chiave dalla soluzione originale

Nella versione hardened, il PLAYER deve:
- **Dedurre gli stili di gioco** dal `hand_log` e da `get_hand_history` invece di riceverli
- Avere un framework decisionale che funzioni **anche senza conoscere gli avversari**
- Essere più aggressivo dato il budget ridotto (50 mani vs 80)
- Usare periodicamente `get_hand_history` per costruire profili comportamentali

Lo SCOUT non può più leggere style hints, quindi il suo briefing si basa solo su:
- Parametri del tavolo (blinds, stacks, target)
- Lo stato della prima mano
- Un'istruzione per il PLAYER di osservare e adattarsi

---

## Prompt dei Nodi (versione hardened)

### SCOUT — System Prompt

```
# Your Role
You are the poker table scout. Gather intelligence and produce a strategy briefing.

# Your Task
1. Instruct the worker to call get_table_info, get_game_state, and get_hand_history.
2. Synthesize a Strategy Briefing containing:
   a) Game Parameters: chips, target, blinds, max hands.
   b) Opponent Notes: names and chip counts — you do NOT know their styles yet.
      The Player must observe their behavior and adapt.
   c) Core Strategy: Tight-Aggressive (TAG) — play few hands aggressively.
   d) Current table state from the first hand.

# Critical Note
You do NOT have information about opponent playing styles. Do NOT guess or invent
style profiles. Tell the Player to observe patterns in the hand_log and hand_history
to build their own model of each opponent.
```

### ScoutWorker — System Prompt

```
You are a poker table scout worker. Gather information for the Scout.
Call each tool the Scout asks for and report ALL data back completely.
Do not take any game actions. Only gather information.
Tools: get_table_info, get_game_state, get_hand_history.
```

### PLAYER — System Prompt

(Vedi file `writeup/player_hardened.md` per il prompt completo)

Il prompt del Player è il cuore della soluzione. Deve contenere:
1. Il game loop (get_game_state → decide → act → repeat)
2. Il preflop hand chart
3. Il postflop framework
4. **Un sistema di profiling degli avversari basato sull'osservazione**
5. Le regole di base del poker (che l'LLM conosce, ma è meglio esplicitare)

---

## Come testare la soluzione

```bash
cd all-in-agent/
cp env.example .env
echo "FLAG_CHALLENGE=ictf{test_flag}" > .env
docker compose up --build
```

Poi caricare il bundle ASL nella UI Agentish e lanciare l'esecuzione.

### Success rate atteso

- **Versione originale** (80 mani, 2500 target, hint espliciti): ~70-80%
- **Versione hardened** (50 mani, 3500 target, zero hint): ~20-35%

Il rate più basso è intenzionale — la challenge è difficile e richiede fortuna oltre che un buon prompt. L'agente ha bisogno sia di mani buone sia di sfruttarle correttamente.

---

## Flag

```
ictf{p0k3r_f4c3_pr0_d3g3n_ch4mp_88442211}
```
