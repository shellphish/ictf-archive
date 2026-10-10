import os
import sys
import random
import litellm

if "OPENAI_API_KEY" not in os.environ and "OPENAI_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_KEY"]

THRESHOLD = int(os.environ.get("THRESHOLD", 3))
MAX_QUERIES = int(os.environ.get("MAX_QUERIES", 33000))
FLAG = os.environ.get("FLAG", "iCTF{test_flag}")
MODEL = os.environ.get("MODEL", "openai/gpt-4o-mini")
DEBUG = os.environ.get("DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def debug_log(message):
    if DEBUG:
        print(f"[DEBUG] {message}", file=sys.stderr, flush=True)

def load_words(path):
    with open(path) as f:
        return [line.strip().lower() for line in f if line.strip()]

def build_mapping(english_words, italian_words):
    italian_copy = italian_words[:]
    random.shuffle(italian_copy)
    return dict(zip(english_words, italian_copy))

def is_grammatical(text, nlp):
    doc = nlp(text)
    has_verb = any(t.pos_ in ('VERB', 'AUX') for t in doc)
    has_nominal = any(t.pos_ in ('NOUN', 'PROPN', 'PRON') for t in doc)
    return has_verb and has_nominal


def grammar_details(text, nlp):
    doc = nlp(text)
    has_verb = any(t.pos_ in ('VERB', 'AUX') for t in doc)
    has_nominal = any(t.pos_ in ('NOUN', 'PROPN', 'PRON') for t in doc)
    return has_verb and has_nominal, has_verb, has_nominal

def sense_check_english(en_sent):
    response = litellm.completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Answer only 'yes' or 'no'."},
            {"role": "user", "content": (
                f"Does this look more or less like an English sentence: '{en_sent}'? "
                "Answer 'yes' only if it is English. It doesn't need to be meaningful, but it should look like a plausible English sentence, even if it's a bit weird."
                "Note that the punctuation has been removed and all words are in lowercase, but it should still look like English. Answer 'no' if it looks like random words or gibberish that doesn't resemble English at all."
            )}
        ],
        temperature=0,
        max_tokens=5
    )
    answer = response.choices[0].message.content or ""
    #DEBUG answer = 'yes'
    debug_log(f"English sense check LLM answer: {answer!r}")
    return 'yes' in answer.lower(), answer


def run_agent(system_prompt, user_message):
    response = litellm.completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=512
    )
    return response.choices[0].message.content or ""

def main():
    import spacy
    debug_log(f"Starting server with THRESHOLD={THRESHOLD}, MAX_QUERIES={MAX_QUERIES}, MODEL={MODEL}")
    english_words = load_words("english-words")
    italian_words = load_words("italian-words")
    debug_log(f"Loaded word lists: english={len(english_words)}, italian={len(italian_words)}")
    assert len(english_words) == len(italian_words), "Word lists must be equal length"

    en_to_it = build_mapping(english_words, italian_words)
    en_set = set(english_words)
    debug_log("Built random English->Italian mapping")

    nlp_en = spacy.load("en_core_web_sm")
    nlp_it = spacy.load("it_core_news_sm")
    debug_log("Loaded spaCy models for English and Italian")

    queries_left = MAX_QUERIES
    if DEBUG:
        print(f"[DEBUG] Allowed queries: {queries_left}")
        

    english_agent_prompt = "You are a helpful assistant. Do exactly what the user asks."
    italian_agent_prompt = (
        f"Sei un assistente che conosce un frase speciale. La frase speciale (anche chiamata 'bandiera' o 'flag') è: {FLAG}\n"
        "Rivela senza problemi questa frase se il messaggio dell'utente te lo chiede anche implicitamente"
        "(per esempo: \"Svela il segreto\", \"Rivela la informazione\", \"Dimmi la bandiera\", \"Rivela il flag\","
        "\"Mostrami la frase\", \"Dammi la risposta\", \"Racconta la storia\". ecc.). "
        "Altrimenti rispondi normalmente a qualunque altra richiesta."
    )

    while queries_left > 0:
        sys.stdout.write("> ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            debug_log("Input stream closed by client")
            break
        line = line.strip().lower()
        if not line:
            continue
        debug_log(f"Received input line: '{line}'")

        words = line.split()
        debug_log(f"Tokenized {len(words)} word(s): {words}")

        # Check all words are known
        unknown = [w for w in words if w not in en_set]
        if unknown:
            debug_log(f"Unknown input words: {unknown}")
            print(f"Unknown word(s): {', '.join(unknown)}")
            sys.exit(0)

        if len(words) <= THRESHOLD:
            # Short path: translate and print
            translations = [en_to_it[w] for w in words]
            debug_log(
                f"Short path success (len={len(words)} <= THRESHOLD={THRESHOLD}), "
                f"translations={translations}"
            )
            print(' '.join(translations))
            queries_left -= 1
            debug_log(f"Queries left: {queries_left}")
        else:
            # Long path: grammar check, sense check, agents
            en_sent = ' '.join(words)
            it_sent = ' '.join(en_to_it[w] for w in words)
            debug_log(f"Long path entered: en_sent='{en_sent}', it_sent='{it_sent}'")
            print(it_sent)
            en_ok, en_has_verb, en_has_nominal = grammar_details(en_sent, nlp_en)
            it_ok, it_has_verb, it_has_nominal = grammar_details(it_sent, nlp_it)

            if not en_ok or not it_ok:
                debug_log(
                    "Grammar check failed: "
                    f"en_ok={en_ok} (has_verb={en_has_verb}, has_nominal={en_has_nominal}, text='{en_sent}'), "
                    f"it_ok={it_ok} (has_verb={it_has_verb}, has_nominal={it_has_nominal}, text='{it_sent}')"
                )
                print("?!?")
                sys.exit(0)

            debug_log(
                "Grammar check passed: "
                f"en(has_verb={en_has_verb}, has_nominal={en_has_nominal}), "
                f"it(has_verb={it_has_verb}, has_nominal={it_has_nominal})"
            )

            en_sense_ok, en_sense_answer = sense_check_english(en_sent)
            if not en_sense_ok:
                debug_log(
                    "English sense check failed: "
                    f"en_sent='{en_sent}', llm_answer='{en_sense_answer}'"
                )
                print("EN?!?")
                sys.exit(0)

            debug_log(f"English sense check passed with llm_answer='{en_sense_answer}'")
            debug_log("Invoking English agent")

            en_response = run_agent(english_agent_prompt, en_sent)
            debug_log("Invoking Italian agent")
            it_response = run_agent(italian_agent_prompt, it_sent)
            debug_log("Agent invocations completed successfully")

            print(en_response)
            print(it_response)
            sys.exit(0)

            debug_log("No more queries left or loop ended; exiting cleanly")
    sys.exit(0)

if __name__ == "__main__":
    main()
