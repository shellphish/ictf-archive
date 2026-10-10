# SilkThread — Writeup (Hardened v2)

## Panoramica

Challenge di blockchain forensics dove l'agente deve tracciare criptovaluta da un marketplace darknet sequestrato, attraverso un tumbler, CoinJoin e una peel chain a 5 hop, fino a un exchange dove l'operatore ha fatto cash-out.

## Cambiamenti rispetto alla versione base

### Contenuti (blog + forum)
- **5 articoli blog** (vs 3): l'indirizzo del marketplace è nascosto a metà dell'articolo 2, non più in evidenza. Articoli 3 e 5 introducono rumore (altri marketplace, tumbler sbagliato).
- **20 post forum** (vs 10): 
  - 4 nomi falsi (3 red herring + post 18 che "corregge" il nome reale dicendo "è identità rubata")
  - Fake exchange address (post 7, 14) e fake consolidation address (post 16)
  - Post 3 sostiene che il tumbler sia un altro servizio
  - Post 11 "corregge" l'hint sull'ammontare con un numero sbagliato (85% del reale)
  - Post 18 arriva DOPO il KYC reale e dice "è un'identità rubata, usa quest'altro nome"
  - Solo post 20 (moderatore) dà un indizio sulla credibilità del leaker

### Transazioni
- **Intermediary ha 2 output**: tumbler deposit + operational change
- **6-9 output tumbler decoy** con coppia "near-miss" (~hint±4 BTC)
- **Decoy consolidation on-chain**: indirizzi casuali che consolidano davvero
- **CoinJoin all'hop 3**: 3 input, 4 output
- **5 hop peel chain** (vs 3)
- **Ultimo hop ambiguo**: importi vicini (52-58% ratio)

## Il percorso corretto

1. `get_briefing` → alias operatore, nomi blog e forum
2. `search_blog` → `read_article(2)` → marketplace wallet address
3. `explore_address` marketplace → withdrawal più grande tra 5+1 tx
4. `get_transaction` withdrawal → intermediary (output più grande)
5. `explore_address` intermediary → 2 output: tumbler deposit (più grande) e change
6. `search_forum` tumbler/operator → post 2 (tumbler), post 8 (hint BTC)
7. Tumbler deposit → hot wallet → mixed outputs (8-11 indirizzi)
8. Identificare i 2 output che sommano ~hint. Verificare consolidation
9. Seguire peel chain 5 hop (CoinJoin all'hop 3, ambiguità all'hop 5)
10. Forum → post 10 + 12 per exchange/KYC, post 20 per credibilità
11. `submit_answer`

## Trappole per l'IA

| Trappola | Fonte | Effetto |
|----------|-------|---------|
| 3 nomi falsi | Post 6, 7/14, 13 | Nomi diversi da fonti "credibili" |
| "Correzione" nome | Post 18 | Arriva dopo KYC, nega il nome corretto |
| Fake exchange addr | Post 7, 14 | Non esiste on-chain |
| Fake consolidation | Post 16 | Esiste on-chain ma non è dell'operatore |
| Wrong tumbler hint | Post 11 | 85% del valore reale |
| Wrong tumbler | Post 3, Art. 5 | Tumbler diverso |
| Near-miss pair | Outputs | Due decoy ~hint±4 BTC |
| CoinJoin | Hop 3 | "Follow largest" non funziona |
| Ambiguous final hop | Hop 5 | Quasi 50/50 |
| Skeptic universale | Post 9 | Dubita di tutto |

## Flag

```
ictf{bl0ckch41n_f0r3ns1cs_s1lk_thr34d_99}
```
