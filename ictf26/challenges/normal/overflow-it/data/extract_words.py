#!/usr/bin/env python3
import argparse
import html
import re
from pathlib import Path

TARGET_COUNT = 10000


def extract_words_from_html(html_text: str) -> list[str]:
    # Work only inside the first ordered list to avoid unrelated sidebar content.
    ol_match = re.search(r"<ol\b[^>]*>(.*?)</ol>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not ol_match:
        raise ValueError("No <ol> word list found in input HTML")

    ol_content = ol_match.group(1)
    li_chunks = re.findall(r"<li\b[^>]*>(.*?)</li>", ol_content, flags=re.IGNORECASE | re.DOTALL)

    words: list[str] = []
    seen: set[str] = set()

    for chunk in li_chunks:
        # Remove any nested tags (for example, occasional <a> wrappers).
        text = re.sub(r"<[^>]+>", "", chunk)
        text = html.unescape(text).strip()
        if not text:
            continue

        # Preserve first occurrence order while removing duplicates.
        if text not in seen:
            seen.add(text)
            words.append(text)

    return words


def write_word_file(path: Path, words: list[str]) -> None:
    path.write_text("\n".join(words) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract top 10,000 English and Italian words from saved HTML pages."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing the saved HTML pages (default: data)",
    )
    parser.add_argument(
        "--english-output",
        type=Path,
        default=Path("english-words"),
        help="Output file for extracted English words (default: english-words)",
    )
    parser.add_argument(
        "--italian-output",
        type=Path,
        default=Path("italian-words"),
        help="Output file for extracted Italian words (default: italian-words)",
    )
    args = parser.parse_args()

    english_html = args.data_dir / "Top 10000 English Words.html"
    italian_html = args.data_dir / "Top 10000 Italian Words.html"

    if not english_html.exists() or not italian_html.exists():
        raise FileNotFoundError(
            "Expected files were not found in data dir: "
            f"{english_html.name}, {italian_html.name}"
        )

    english_words = extract_words_from_html(english_html.read_text(encoding="utf-8"))
    italian_words = extract_words_from_html(italian_html.read_text(encoding="utf-8"))

    if len(english_words) < TARGET_COUNT:
        raise ValueError(f"English list has only {len(english_words)} unique words, expected {TARGET_COUNT}")
    if len(italian_words) < TARGET_COUNT:
        raise ValueError(f"Italian list has only {len(italian_words)} unique words, expected {TARGET_COUNT}")

    english_words = english_words[:TARGET_COUNT]
    italian_words = italian_words[:TARGET_COUNT]

    write_word_file(args.english_output, english_words)
    write_word_file(args.italian_output, italian_words)

    print(f"Wrote {len(english_words)} English words to {args.english_output}")
    print(f"Wrote {len(italian_words)} Italian words to {args.italian_output}")


if __name__ == "__main__":
    main()
