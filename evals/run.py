import json
import sys
import time
from pathlib import Path

from juanitor import ai

SCENARIOS = Path(__file__).parent / "scenarios.json"


def grade(scenario, answer):
    if answer is None:
        return ["no usable answer from the AI"]
    problems = []
    text = " ".join([answer["summary"], answer["cause"], answer["fix"]]).lower()
    for group in scenario.get("must_mention", []):
        if not any(word.lower() in text for word in group):
            problems.append(f"should mention one of {group}")
    for word in scenario.get("must_not_mention", []):
        if word.lower() in text:
            problems.append(f"should not mention '{word}'")
    allowed = scenario.get("confidence_in")
    if allowed and answer["confidence"] not in allowed:
        problems.append(f"confidence '{answer['confidence']}' not in {allowed}")
    return problems


def main():
    scenarios = json.loads(SCENARIOS.read_text())
    only = sys.argv[1] if len(sys.argv) > 1 else None
    passed = 0
    total = 0
    for s in scenarios:
        if only and s["id"] != only:
            continue
        total += 1
        start = time.time()
        answer = ai.explain(s["finding"], s["evidence"])
        seconds = time.time() - start
        problems = grade(s, answer)
        if not problems:
            passed += 1
        print(f"[{'PASS' if not problems else 'FAIL'}] {s['id']} ({seconds:.0f}s)")
        if answer:
            print(f"    summary: {answer['summary']}")
            print(f"    cause:   {answer['cause']}")
            print(f"    fix:     {answer['fix']}  [{answer['confidence']}]")
        for problem in problems:
            print(f"    -> {problem}")
    print(f"\nScore: {passed}/{total} with model {ai.OLLAMA_MODEL}")


if __name__ == "__main__":
    main()
