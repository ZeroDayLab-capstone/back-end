# logger.py
from models import Log
from datetime import datetime

def save_log(db, action: str, user: str):
    log = Log(
        timestamp=datetime.utcnow().isoformat(),
        action=action,
        user=user
    )
    db.add(log)
    db.commit()
