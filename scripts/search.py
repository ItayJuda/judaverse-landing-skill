#!/usr/bin/env python3
"""
BM25 search over landing-builder design data.

Usage:
  python3 scripts/search.py "dark AI agency" --domain layout
  python3 scripts/search.py "particles" --domain animation
  python3 scripts/search.py "glassmorphism hero" --domain component
  python3 scripts/search.py "nextjs" --domain stack
  python3 scripts/search.py "SaaS dark" -n 5
"""

import argparse
import csv
import math
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# BM25 implementation (no external deps)
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    text = text.lower()
    # replace separators with spaces
    text = re.sub(r'[|;,.\-_/]', ' ', text)
    return [t for t in text.split() if len(t) > 1]


class BM25:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.N = len(corpus)
        self.avgdl = sum(len(d) for d in corpus) / max(self.N, 1)
        self.df: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self._build_df()
        self._build_idf()

    def _build_df(self):
        for doc in self.corpus:
            seen = set(doc)
            for term in seen:
                self.df[term] = self.df.get(term, 0) + 1

    def _build_idf(self):
        for term, df in self.df.items():
            # Robertson-Sparck Jones IDF with smoothing
            self.idf[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def score(self, query_tokens: list[str], doc_index: int) -> float:
        doc = self.corpus[doc_index]
        dl = len(doc)
        tf_map: dict[str, int] = {}
        for t in doc:
            tf_map[t] = tf_map.get(t, 0) + 1

        score = 0.0
        for term in query_tokens:
            if term not in self.idf:
                continue
            tf = tf_map.get(term, 0)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += self.idf[term] * numerator / max(denominator, 1e-9)
        return score

    def rank(self, query: str, n: int = 3) -> list[tuple[int, float]]:
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = [(i, self.score(tokens, i)) for i in range(self.N)]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(idx, s) for idx, s in scores if s > 0][:n]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

DOMAIN_FILES = {
    "animation": "animations.csv",
    "component":  "components.csv",
    "layout":    "layouts.csv",
    "stack":     "stacks.csv",
    # aliases
    "style":     "layouts.csv",
    "animations": "animations.csv",
    "components": "components.csv",
    "layouts":   "layouts.csv",
    "stacks":    "stacks.csv",
}

DOMAIN_KEYWORDS = {
    "animation":  ["particle", "aurora", "beam", "orb", "grid", "animation", "animate", "motion", "effect", "wave"],
    "component":  ["hero", "navbar", "footer", "marquee", "cta", "stats", "badge", "card", "section", "button", "nav"],
    "layout":     ["agency", "saas", "portfolio", "ecommerce", "business", "layout", "page", "structure", "conversion"],
    "stack":      ["nextjs", "next", "react", "vite", "html", "tailwind", "stack", "framework", "setup"],
}


def detect_domain(query: str) -> str:
    q = query.lower()
    scores: dict[str, int] = {d: 0 for d in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                scores[domain] += 1
    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "layout"


def find_data_dir() -> Path:
    # Walk up from script location to find data/
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir.parent / "data", script_dir / "data", Path("data")]:
        if candidate.is_dir():
            return candidate
    # Fallback: cwd/data
    return Path("data")


def load_csv(filepath: Path) -> tuple[list[str], list[dict]]:
    rows = []
    headers = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        headers = reader.fieldnames or []
        for row in reader:
            rows.append(dict(row))
    return headers, rows


def row_to_document(row: dict) -> list[str]:
    """Flatten all field values into a token list for BM25."""
    tokens = []
    for value in row.values():
        tokens.extend(tokenize(value or ""))
    return tokens


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_result(rank: int, row: dict, score: float, headers: list[str]):
    print(f"\n{'-' * 60}")
    print(f"  #{rank}  score={score:.3f}")
    print(f"{'-' * 60}")
    for h in headers:
        val = row.get(h, "")
        if val:
            label = f"  {h:<18}"
            print(f"{label}{val}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BM25 search over landing-builder design data."
    )
    parser.add_argument("query", help="Search query (e.g. 'dark AI agency')")
    parser.add_argument(
        "--domain", "-d",
        choices=list(DOMAIN_FILES.keys()),
        default=None,
        help="Data domain to search (auto-detected if omitted)",
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="Direct path to a CSV file (overrides --domain)",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=3,
        help="Max results to return (default: 3)",
    )
    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        domain_label = filepath.stem.upper()
    else:
        domain = args.domain or detect_domain(args.query)
        filename = DOMAIN_FILES[domain]
        data_dir = find_data_dir()
        filepath = data_dir / filename
        domain_label = domain.upper().rstrip("S")

    if not filepath.exists():
        print(f"ERROR: data file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    headers, rows = load_csv(filepath)
    if not rows:
        print("No data found.", file=sys.stderr)
        sys.exit(1)

    corpus = [row_to_document(r) for r in rows]
    bm25 = BM25(corpus)
    ranked = bm25.rank(args.query, n=args.n)

    print(f"\n{'=' * 60}")
    print(f"  SEARCH: \"{args.query}\"  |  DOMAIN: {domain_label}  |  TOP {args.n}")
    print("=" * 60)

    if not ranked:
        print("\n  No matching results. Try a different query or domain.")
        # Show all rows as fallback
        ranked = [(i, 0.0) for i in range(min(args.n, len(rows)))]

    for position, (idx, score) in enumerate(ranked, start=1):
        print_result(position, rows[idx], score, headers)

    print(f"\n{'-' * 60}\n")


if __name__ == "__main__":
    main()
