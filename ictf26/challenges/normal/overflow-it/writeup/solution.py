"""
Solution for overflow-it challenge.

Strategy:
1. Locally scan italian-words for "reveal-class" verbs and "secret-class" nouns/articles.
2. Build candidate Italian sentences (4+ words that would make the agent reveal the flag).
3. Connect to remote challenge service, query 3 words at a time to build en→it mapping.
4. Once enough words are discovered, find an English sentence whose Italian translation
   matches a candidate reveal sentence.
5. Submit that English sentence to trigger the Italian agent to reveal the flag.
"""

import argparse
import itertools
import random
import sys
import re
import socket
from pathlib import Path

SOLVE_ATTEMPTS = 1
BATCH_SIZE = 3
# Reserve one server query for the final long-sentence submission.
SERVER_MAX_QUERIES = 33000
MAPPING_ATTEMPTS_PER_SOLVE = SERVER_MAX_QUERIES - 1
TARGET_MAPPING_OBSERVATIONS = MAPPING_ATTEMPTS_PER_SOLVE * BATCH_SIZE

BASE_DIR = Path(__file__).resolve().parent.parent
ENGLISH_WORDS_PATH = BASE_DIR / "english-words"
ITALIAN_WORDS_PATH = BASE_DIR / "italian-words"

# In-memory Italian phrase generation buckets.
PHRASE_VERBS = [
    "rivela",
    "svela",
    "dici",
    "racconta",
    "scopri",
    "indica",
    "trova",
    "mostra",
    "dammi",
    "dimmi",
]

PHRASE_ARTICLE_NOUNS = [
    "il segreto",
    "la bandiera",
    "il codice",
    "la chiave",
    "la parola",
    "la risposta",
    "la rivelazione",
    "la informazione",
    "il messaggio",
]

PHRASE_ADVERBS = [
    "adesso",
    "subito",
    "ora",
    "immediatamente",
]

VERB_PATTERNS = ['svela', 'rivela', 'dimm', 'mostram', 'dac', 'dai', 'dic', 'mostra', 'dicci', 'dite', 'riveli']
NOUN_PATTERNS = ['segreto', 'bandiera', 'codice', 'chiave', 'password', 'parola']
ARTICLE_PATTERNS = ['il', 'la', 'lo', 'gli', 'le', 'i', 'un', 'una', 'dello', 'della']

def load_words(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def generate_italian_phrases(count=1000, shuffle=True):
    """Generate Italian reveal phrases in memory from VERB x ARTICLE_NOUN x ADVERB."""
    phrases = [
        f"{verb} {article_noun} {adverb}"
        for verb, article_noun, adverb in itertools.product(
            PHRASE_VERBS, PHRASE_ARTICLE_NOUNS, PHRASE_ADVERBS
        )
    ]

    if shuffle:
        random.shuffle(phrases)

    return phrases[:count]


def find_mapped_phrases(it_to_en, phrases, grammar_checker):
    """
    Iterate through all Italian phrases and generate the corresponding English
    sentence when fully mapped.
    """
    mapped = []
    for phrase in phrases:
        words = phrase.lower().split()
        missing = [w for w in words if w not in it_to_en]
        if missing:
            continue

        en_sentence = " ".join(it_to_en[w] for w in words)
        grammar_ok = is_grammatical_en(en_sentence.split(), grammar_checker)
        mapped.append((en_sentence, phrase, grammar_ok))
    return mapped


def interactive_choose_sentence(mapped_phrases):
    """
    Print only grammar-valid English phrases and ask the user to pick one.
    Returns the chosen English sentence string, or None to skip.
    """
    viable_phrases = [(en_sent, it_phrase, ok) for en_sent, it_phrase, ok in mapped_phrases if ok]
    if not viable_phrases:
        print("[*] No grammar-valid English candidate phrases found")
        return None

    print(f"\n[*] Found {len(viable_phrases)} grammar-valid English candidate phrase(s)")
    for i, (en_sent, _it_phrase, _grammar_ok) in enumerate(viable_phrases, 1):
        print(f"  [{i:3}] EN: {en_sent}")
    print()
    print("[*] Choose a sentence to submit")
    while True:
        try:
            raw = input(f"Choose sentence to submit [1-{len(viable_phrases)}, 0 to skip]: ").strip()
            idx = int(raw)
            if idx == 0:
                return None
            if 1 <= idx <= len(viable_phrases):
                chosen = viable_phrases[idx - 1]
                return chosen[0]
            print(f"  Please enter a number between 0 and {len(viable_phrases)}")
        except (ValueError, EOFError, KeyboardInterrupt):
            return None


def build_query_words_in_order(english_words, total_words):
    """Build an ordered query stream by cycling through english_words."""
    if not english_words or total_words <= 0:
        return []
    repeats = (total_words + len(english_words) - 1) // len(english_words)
    return (english_words * repeats)[:total_words]


def build_grammar_checker():
    """
    Return a callable grammar checker.
    Uses spaCy when available; falls back to a lightweight heuristic otherwise.
    """
    try:
        import spacy
        nlp_en = spacy.load("en_core_web_sm")

        def checker(words):
            doc = nlp_en(' '.join(words))
            has_verb = any(t.pos_ in ('VERB', 'AUX') for t in doc)
            has_nominal = any(t.pos_ in ('NOUN', 'PROPN', 'PRON') for t in doc)
            return has_verb and has_nominal

        print("[*] Using spaCy grammar checker")
        return checker
    except Exception as exc:
        print(f"[!] spaCy unavailable ({exc}); using heuristic grammar checker")

        common_verbs = {
            'is', 'are', 'was', 'were', 'be', 'being', 'been',
            'do', 'does', 'did', 'have', 'has', 'had',
            'go', 'goes', 'went', 'make', 'makes', 'made',
            'say', 'says', 'said', 'eat', 'eats', 'ate',
            'run', 'runs', 'ran'
        }
        pronouns = {'i', 'you', 'he', 'she', 'it', 'we', 'they'}

        def checker(words):
            lower = [w.lower() for w in words]
            has_verb = any(
                w in common_verbs or w.endswith(('ed', 'ing', 'en', 'es', 's'))
                for w in lower
            )
            has_nominal = any(
                w in pronouns or w not in {'the', 'a', 'an', 'and', 'or', 'but', 'to', 'of', 'in', 'on', 'at'}
                for w in lower
            )
            return has_verb and has_nominal

        return checker

def find_candidates(italian_words):
    verbs = [w for w in italian_words if any(p in w.lower() for p in VERB_PATTERNS)]
    nouns = [w for w in italian_words if any(p in w.lower() for p in NOUN_PATTERNS)]
    articles = [w for w in italian_words if w.lower() in ARTICLE_PATTERNS]
    return verbs, nouns, articles

def read_until_prompt(reader):
    buf = ""
    while not buf.endswith("> "):
        ch = reader.read(1)
        if not ch:
            break
        buf += ch
    return buf


def print_server_message(label, message):
    """Print raw server messages exactly as received."""
    print(f"[*] {label}")
    if message:
        print(message, end="" if message.endswith("\n") else "\n")
    else:
        print("[empty response]")

def extract_payload_line(response):
    """Extract the most relevant non-debug line from a prompt-terminated response."""
    lines = [line.strip() for line in response.splitlines()]
    filtered = [
        line for line in lines
        if line
        and line != ">"
        and not line.startswith(">")
        and not line.startswith("[DEBUG]")
    ]
    return filtered[-1] if filtered else ""


def query_server(writer, reader, words):
    """Send up to 3 words, return list of Italian translations."""
    writer.write(' '.join(words) + '\n')
    writer.flush()
    response = read_until_prompt(reader)
    line = extract_payload_line(response)
    parts = line.split()
    return parts

def is_grammatical_en(words, grammar_checker):
    return grammar_checker(words)

def attempt(english_words, grammar_checker, verbs, nouns, articles, phrases, host, port):
    """One attempt: connect to remote service, discover mapping, find and submit reveal sentence."""
    # Build it→en lookup sets for candidate matching
    verb_set = set(v.lower() for v in verbs)
    noun_set = set(n.lower() for n in nouns)
    article_set = set(a.lower() for a in articles)

    # Build a fixed-size ordered recovery stream from the local english-words list.
    needed_words = TARGET_MAPPING_OBSERVATIONS
    query_words = build_query_words_in_order(english_words, needed_words)

    sock = socket.create_connection((host, port), timeout=20)
    reader = sock.makefile('r', encoding='utf-8', newline='')
    writer = sock.makefile('w', encoding='utf-8', newline='')

    try:
        # Read initial prompt
        initial = read_until_prompt(reader)
        if not initial.endswith("> "):
            return False

        it_to_en = {}  # italian word → english word

        batches_done = 0
        mappings_observed = 0
        i = 0
        total = len(query_words)

        while i < total and batches_done < MAPPING_ATTEMPTS_PER_SOLVE:
            batch = query_words[i:i+BATCH_SIZE]
            i += BATCH_SIZE
            batches_done += 1

            it_words = query_server(writer, reader, batch)
            if len(it_words) == len(batch):
                mappings_observed += len(batch)
                for en, it in zip(batch, it_words):
                    it_to_en[it.lower()] = en
            else:
                # Server may have exited
                break

            if mappings_observed >= TARGET_MAPPING_OBSERVATIONS:
                break

        print(f"[*] Mapping recovery complete: {mappings_observed}/{TARGET_MAPPING_OBSERVATIONS}")

        # --- Phrase-list matching (primary strategy) ---
        if phrases:
            mapped = find_mapped_phrases(it_to_en, phrases, grammar_checker)

            if mapped:
                en_sentence = interactive_choose_sentence(mapped)
                if en_sentence is not None:
                    result = submit_sentence(writer, reader, en_sentence)
                    return result
            else:
                print("[*] No pre-generated phrases fully mapped; falling back to heuristic search")

        # --- Heuristic fallback ---
        candidate = find_reveal_sentence(it_to_en, verb_set, noun_set, article_set, grammar_checker)
        if candidate is not None:
            en_sentence = candidate
            print(f"[*] Found candidate English sentence: {en_sentence}")
            print(f"[*] Recovered mappings: {mappings_observed}/{TARGET_MAPPING_OBSERVATIONS}")
            result = submit_sentence(writer, reader, en_sentence)
            return result

    finally:
        try:
            writer.close()
        except Exception:
            pass
        try:
            reader.close()
        except Exception:
            pass
        sock.close()

    return False

def find_reveal_sentence(it_to_en, verb_set, noun_set, article_set, grammar_checker):
    """
    Look through discovered it→en mappings for a combination that forms a valid
    Italian reveal sentence and has a valid English translation.
    Returns the English word list (as string) if found, else None.
    """
    discovered_it = list(it_to_en.keys())

    found_verbs = [w for w in discovered_it if any(p in w for p in verb_set) or any(p in w for p in ['svela', 'rivela', 'dimm', 'mostram', 'dac', 'dai', 'dic', 'mostra', 'dicci', 'riveli'])]
    found_nouns = [w for w in discovered_it if any(p in w for p in noun_set) or any(p in w for p in ['segreto', 'bandiera', 'codice', 'chiave'])]
    found_articles = [w for w in discovered_it if w in article_set]

    if not found_verbs or not found_nouns:
        return None

    # Try combinations: verb + article + noun + extra_word
    # or article + noun + verb + extra
    for verb in found_verbs:
        for noun in found_nouns:
            # Try with article if available
            article_candidates = found_articles if found_articles else ['']
            for art in article_candidates:
                # Look for a 4th word to complete the sentence
                # Use any pronoun-like word we've discovered
                for extra in discovered_it:
                    if extra in (verb, noun, art):
                        continue
                    # Form Italian sentence candidates
                    candidates_it = []
                    if art:
                        candidates_it.append([verb, art, noun, extra])
                        candidates_it.append([art, noun, extra, verb])
                    else:
                        candidates_it.append([verb, noun, extra, noun])

                    for it_words in candidates_it:
                        # Check all words are in mapping
                        if not all(w in it_to_en for w in it_words):
                            continue
                        en_words = [it_to_en[w] for w in it_words]
                        if len(en_words) <= 3:
                            continue
                        if is_grammatical_en(en_words, grammar_checker):
                            return ' '.join(en_words)

    # Simpler: just find any 4+ word English sentence whose Italian words
    # include at least one verb-pattern and one noun-pattern word
    # Try all combinations of 4 discovered mappings
    if len(found_verbs) >= 1 and len(found_nouns) >= 1 and len(found_articles) >= 1:
        for verb in found_verbs[:5]:
            for art in found_articles[:5]:
                for noun in found_nouns[:5]:
                    for extra in discovered_it[:20]:
                        if extra in (verb, art, noun):
                            continue
                        it_combo = [verb, art, noun, extra]
                        if not all(w in it_to_en for w in it_combo):
                            continue
                        en_words = [it_to_en[w] for w in it_combo]
                        if is_grammatical_en(en_words, grammar_checker):
                            return ' '.join(en_words)

    return None

def submit_sentence(writer, reader, en_sentence):
    """Submit the sentence to the server and read the response."""
    print(f"[*] Submitting sentence: {en_sentence}")
    writer.write(en_sentence + '\n')
    writer.flush()

    # Read all remaining output (server will exit after this)
    output = ""
    try:
        output = reader.read()
    except Exception:
        pass

    print_server_message("Final server response:", output)

    # Check for flag pattern
    flag_match = re.search(r'CTF\{[^}]+\}', output)
    if flag_match:
        print(f"\n[+] FLAG FOUND: {flag_match.group(0)}")
        return True

    return False

def parse_args():
    parser = argparse.ArgumentParser(description="Solve overflow-it via remote host/port")
    parser.add_argument("host", help="Challenge hostname or IP")
    parser.add_argument("port", type=int, help="Challenge TCP port")
    parser.add_argument(
        "--phrase-count",
        type=int,
        default=1000,
        help="Number of generated Italian phrases to keep in memory (default: 1000)",
    )
    parser.add_argument(
        "--no-phrase-shuffle",
        action="store_true",
        help="Do not shuffle generated Italian phrases",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("[*] Loading word lists...")
    english_words = load_words(ENGLISH_WORDS_PATH)
    italian_words = load_words(ITALIAN_WORDS_PATH)

    grammar_checker = build_grammar_checker()

    print("[*] Scanning Italian words for reveal candidates...")
    verbs, nouns, articles = find_candidates(italian_words)
    print(f"    Found {len(verbs)} verb candidates, {len(nouns)} noun candidates, {len(articles)} articles")

    phrases = generate_italian_phrases(
        count=args.phrase_count,
        shuffle=not args.no_phrase_shuffle,
    )
    print(f"[*] Generated {len(phrases)} Italian phrases in memory")

    print(f"[*] Target service: {args.host}:{args.port}")

    for attempt_num in range(1, SOLVE_ATTEMPTS + 1):
        print(f"\n[*] Solve attempt {attempt_num}/{SOLVE_ATTEMPTS}")
        success = attempt(english_words, grammar_checker, verbs, nouns, articles, phrases, args.host, args.port)
        if success:
            print("[+] Challenge solved!")
            sys.exit(0)

    print("[-] Failed to solve challenge within max attempts")
    sys.exit(1)

if __name__ == "__main__":
    main()
