import subprocess

from juanitor import state


def disk_evidence(db, finding):
    mount = finding["key"].split(":", 1)[1]
    lines = []

    change = state.change_over(db, finding["key"], days=7)
    if change is None:
        lines.append("History: unknown, there is no past data. Do not say whether it grew, shrank or stayed the same.")
    else:
        old, hours = change
        lines.append(f"History: {old:.0f}% full {hours:.0f} hours ago, "
                     f"{finding['value']:.0f}% now.")

    try:
        result = subprocess.run(
            ["du", "-x", "-k", "--max-depth=1", mount],
            capture_output=True, text=True, timeout=60,
        )
        rows = []
        for line in result.stdout.splitlines():
            size_kb, path = line.split("\t", 1)
            rows.append((int(size_kb), path))
        rows.sort(reverse=True)
        lines.append("Largest folders:")
        for size_kb, path in rows[1:7]:
            lines.append(f"  {path}: {size_kb / 1e6:.1f} GB")
    except subprocess.TimeoutExpired:
        lines.append("Folder sizes: scan took too long, skipped.")

    return "\n".join(lines)


BACKUP_LOG = "/var/log/homelab-backup.log"
BACKUP_KEYWORDS = ("FAILED", "ERROR", "Fatal", "error:", "STATUS",
                   "Backup started")


def backup_evidence(db, finding):
    try:
        with open(BACKUP_LOG, errors="replace") as log:
            lines = log.read().splitlines()
    except OSError as error:
        return f"Backup log could not be read: {error}"
    important = [line for line in lines[-200:]
                 if any(word in line for word in BACKUP_KEYWORDS)]
    if not important:
        return "No error lines in the recent backup log."
    return "Recent backup log lines:\n" + "\n".join(important[-12:])



EVIDENCE = {"disk": disk_evidence, "backup": backup_evidence}

def collect(db, finding):
    collector = EVIDENCE.get(finding["check"])
    if collector is None:
        return "No extra evidence collected."
    return collector(db, finding)
