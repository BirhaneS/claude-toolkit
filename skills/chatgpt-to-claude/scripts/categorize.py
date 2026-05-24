#!/usr/bin/env python3
"""
Keyword-based categorizer for ChatGPT conversations.

Reads parsed conversations from stdin (one JSON per line), emits the same
records with an added "category" field.

Usage:
    python3 parse_export.py <dir> | python3 categorize.py

The CATEGORIES dict below is the default. To customize, edit it before running
or maintain a fork of this script tailored to your domains.
"""

import json
import sys


CATEGORIES = {
    "Software Development": [
        "c#", ".net", "dotnet", "python", "javascript", "typescript",
        "react", "node", "linq", "asp.net", "swagger", "json", "regex",
        "sql", "database", "api", "function", "class", "exception",
        "git", "github", "rebase", "merge", "commit",
    ],
    "Cloud & DevOps": [
        "aws", "ec2", "s3", "lambda", "dynamodb", "kubernetes", "k8s",
        "docker", "container", "nomad", "consul", "terraform", "helm",
        "ingress", "cluster", "pod", "deployment", "ci/cd", "pipeline",
    ],
    "Monitoring & Observability": [
        "splunk", "new relic", "datadog", "grafana", "prometheus",
        "opentelemetry", "metric", "trace", "dashboard", "alert",
    ],
    "AI & Machine Learning": [
        "machine learning", "neural network", "llm", "gpt", "claude",
        "openai", "anthropic", "mcp", "ai agent", "prompt", "embedding",
        "rag", "fine-tun", "transformer", "obsidian", "knowledge base",
    ],
    "Personal Finance": [
        "mortgage", "401k", "savings", "tax", "refinance", "invest",
        "stock", "bond", "loan", "debt", "budget", "vanguard",
        "interest rate", "escrow", "insurance", "credit card",
        "retirement", "ira", "roth", "etf", "real estate",
    ],
    "Health & Medical": [
        "doctor", "hospital", "medication", "symptom", "diagnosis",
        "exercise", "diet", "nutrition", "vitamin", "supplement",
        "health", "medical", "pain", "injury", "allergy",
    ],
    "Home & DIY": [
        "home", "house", "repair", "renovation", "plumb", "electric",
        "appliance", "furniture", "garden", "roof", "tile", "paint",
        "kitchen", "bathroom", "install", "fix",
    ],
    "Family & Parenting": [
        "kid", "child", "son", "daughter", "school", "homework",
        "parent", "family", "baby", "toddler", "teen", "tutor",
        "daycare", "birthday",
    ],
    "Vehicles & Cars": [
        "car", "vehicle", "honda", "toyota", "ford", "bmw", "tesla",
        "engine", "brake", "tire", "oil change", "mechanic",
        "dealership", "lease", "auto loan",
    ],
    "Career & Business": [
        "job", "resume", "interview", "salary", "promotion", "manager",
        "team", "meeting", "client", "presentation", "career",
        "offer letter", "performance review", "linkedin", "startup",
    ],
    "Education": [
        "course", "exam", "grade", "professor", "homework", "assignment",
        "lecture", "study", "degree", "university", "college", "math",
        "algorithm", "gpa", "thesis", "research",
    ],
    "Travel": [
        "flight", "hotel", "airport", "trip", "vacation", "travel",
        "passport", "visa", "tourism",
    ],
    "Food & Cooking": [
        "recipe", "cook", "bake", "ingredient", "meal", "dinner",
        "lunch", "breakfast", "restaurant",
    ],
}


def categorize(title: str, messages: list) -> str:
    text = title.lower() + " " + " ".join(
        m[1].lower() for m in messages[:6]
    )
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            scores[cat] += text.count(kw)
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "Uncategorized"


def main() -> None:
    counts: dict[str, int] = {}
    for line in sys.stdin:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        cat = categorize(record["title"], record["messages"])
        record["category"] = cat
        counts[cat] = counts.get(cat, 0) + 1
        print(json.dumps(record, ensure_ascii=False))

    print("\nCategory counts:", file=sys.stderr)
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  [{n:4d}] {cat}", file=sys.stderr)


if __name__ == "__main__":
    main()
