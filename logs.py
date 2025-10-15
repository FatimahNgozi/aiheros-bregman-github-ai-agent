"""logs.py — handles saving conversation logs"""

import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_interaction_to_file(agent, messages, source="user"):
    """Save interaction logs for evaluation or debugging."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"{agent.name}_{timestamp}.json"

    record = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent.name,
        "messages": messages,
        "source": source
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"🪵 Logged interaction to {log_file}")
