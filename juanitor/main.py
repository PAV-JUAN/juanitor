from juanitor import ai, evidence, notify, state
from juanitor.checks import backup, system

def explain_text(db, f):
    proof = evidence.collect(db, f)
    answer = ai.explain(f, proof)
    if answer is None:
        return None
    return (f"{answer['summary']}\n"
            f"Cause: {answer['cause']}\n"
            f"Fix: {answer['fix']}\n"
            f"(AI confidence: {answer['confidence']})")


def handle_alert(db, f):
    if f["level"] == "urgent":
        notify.send(f["title"], f["details"], "urgent")
        text = explain_text(db, f)
        if text:
            notify.send(f"Why: {f['title']}", text, "warning")
    else:
        text = explain_text(db, f)
        message = f["details"] if text is None else f"{f['details']}\n\n{text}"
        notify.send(f["title"], message, "warning")


def main():
    findings = system.run_all() + backup.run_all()
    db = state.connect()
    with db:
        for f in findings:
            state.save_reading(db, f)
            action = state.decide(db, f)
            if action == "alert":
                print(f"ALERT    [{f['level']}] {f['title']}")
                handle_alert(db, f)
            elif action == "resolved":
                print(f"RESOLVED {f['title']}")
                notify.send(f"Resolved: {f['title']}", f["details"], "resolved")
    db.close()
    print(f"Checked {len(findings)} items.")


if __name__ == "__main__":
    main()
