"""
storage.py — SQLite database layer for SolutionA4U Leah AI Concierge Platform
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from config import DB_PATH, TRIAL_DAYS

log = logging.getLogger(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize all database tables."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS hosts (
            host_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id     INTEGER UNIQUE NOT NULL,
            name            TEXT,
            business_name   TEXT,
            email           TEXT,
            phone           TEXT,
            language        TEXT DEFAULT 'en',
            status          TEXT DEFAULT 'demo',
            trial_start     TEXT,
            trial_end       TEXT,
            sub_start       TEXT,
            sub_end         TEXT,
            stripe_id       TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS properties (
            property_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id         INTEGER NOT NULL,
            property_name   TEXT NOT NULL,
            city            TEXT,
            state_region    TEXT,
            country         TEXT,
            address         TEXT,
            concierge_name  TEXT DEFAULT 'Leah',
            wifi_ssid       TEXT,
            wifi_pass       TEXT,
            checkin_time    TEXT,
            checkout_time   TEXT,
            keypad_code     TEXT,
            max_guests      INTEGER,
            amenities       TEXT,
            house_rules     TEXT,
            emergency       TEXT,
            telegram_group  TEXT,
            bot_token       TEXT,
            is_active       INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (host_id) REFERENCES hosts(host_id)
        );

        CREATE TABLE IF NOT EXISTS knowledge_base (
            kb_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id     INTEGER NOT NULL,
            file_type       TEXT,
            original_name   TEXT,
            content         TEXT,
            file_path       TEXT,
            keywords        TEXT,
            usage_count     INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (property_id) REFERENCES properties(property_id)
        );

        CREATE TABLE IF NOT EXISTS guest_sessions (
            session_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id     INTEGER,
            bot_type        TEXT DEFAULT 'demo',
            telegram_id     INTEGER NOT NULL,
            guest_name      TEXT,
            language        TEXT DEFAULT 'en',
            state           TEXT DEFAULT 'awaiting_name',
            pending_service TEXT,
            pending_place   TEXT,
            review_score    REAL DEFAULT 5.0,
            messages_count  INTEGER DEFAULT 0,
            is_active       INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            msg_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER NOT NULL,
            sender          TEXT NOT NULL,
            content         TEXT NOT NULL,
            sentiment       TEXT,
            intent          TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES guest_sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS escalations (
            esc_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER,
            property_id     INTEGER,
            esc_type        TEXT,
            guest_msg       TEXT,
            bot_response    TEXT,
            host_notified   INTEGER DEFAULT 0,
            resolved        INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS onboarding_sessions (
            ob_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id     INTEGER UNIQUE NOT NULL,
            state           TEXT DEFAULT 'start',
            language        TEXT DEFAULT 'en',
            data            TEXT DEFAULT '{}',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS payments (
            pay_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id         INTEGER,
            pay_type        TEXT,
            amount          REAL,
            currency        TEXT DEFAULT 'USD',
            status          TEXT DEFAULT 'pending',
            reference       TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        """)
    log.info("Database initialized at %s", DB_PATH)


# ─── Host Operations ──────────────────────────────────────────────────────────

def get_or_create_host(telegram_id: int) -> Dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM hosts WHERE telegram_id=?", (telegram_id,)).fetchone()
        if row:
            return dict(row)
        conn.execute("INSERT INTO hosts (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()
        return dict(conn.execute("SELECT * FROM hosts WHERE telegram_id=?", (telegram_id,)).fetchone())


def update_host(telegram_id: int, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [telegram_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE hosts SET {sets} WHERE telegram_id=?", vals)
        conn.commit()


def get_host(telegram_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM hosts WHERE telegram_id=?", (telegram_id,)).fetchone()
        return dict(row) if row else None


# ─── Property Operations ──────────────────────────────────────────────────────

def create_property(host_id: int, **kwargs) -> int:
    kwargs["host_id"] = host_id
    cols = ", ".join(kwargs.keys())
    placeholders = ", ".join("?" for _ in kwargs)
    with get_conn() as conn:
        cur = conn.execute(f"INSERT INTO properties ({cols}) VALUES ({placeholders})", list(kwargs.values()))
        conn.commit()
        return cur.lastrowid


def get_property(property_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM properties WHERE property_id=?", (property_id,)).fetchone()
        return dict(row) if row else None


def get_host_properties(host_id: int) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM properties WHERE host_id=? AND is_active=1", (host_id,)).fetchall()
        return [dict(r) for r in rows]


def update_property(property_id: int, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [property_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE properties SET {sets} WHERE property_id=?", vals)
        conn.commit()


# ─── Knowledge Base Operations ────────────────────────────────────────────────

def save_kb_file(property_id: int, file_type: str, original_name: str,
                 content: str, file_path: str = "", keywords: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO knowledge_base (property_id, file_type, original_name, content, file_path, keywords) VALUES (?,?,?,?,?,?)",
            (property_id, file_type, original_name, content, file_path, keywords)
        )
        conn.commit()
        return cur.lastrowid


def get_kb_files(property_id: int) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM knowledge_base WHERE property_id=?", (property_id,)).fetchall()
        return [dict(r) for r in rows]


def get_kb_content(property_id: int) -> str:
    """Assemble all knowledge base content for a property into one context string."""
    files = get_kb_files(property_id)
    if not files:
        return ""
    parts = []
    for f in files:
        label = f["file_type"].replace("_", " ").upper()
        parts.append(f"=== {label} ===\n{f['content']}")
    return "\n\n".join(parts)


def increment_kb_usage(kb_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE knowledge_base SET usage_count=usage_count+1 WHERE kb_id=?", (kb_id,))
        conn.commit()


# ─── Guest Session Operations ─────────────────────────────────────────────────

def get_or_create_guest_session(telegram_id: int, bot_type: str = "demo",
                                 property_id: Optional[int] = None) -> Dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM guest_sessions WHERE telegram_id=? AND bot_type=? AND is_active=1",
            (telegram_id, bot_type)
        ).fetchone()
        if row:
            return dict(row)
        conn.execute(
            "INSERT INTO guest_sessions (telegram_id, bot_type, property_id) VALUES (?,?,?)",
            (telegram_id, bot_type, property_id)
        )
        conn.commit()
        return dict(conn.execute(
            "SELECT * FROM guest_sessions WHERE telegram_id=? AND bot_type=? AND is_active=1",
            (telegram_id, bot_type)
        ).fetchone())


def update_guest_session(telegram_id: int, bot_type: str, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [telegram_id, bot_type]
    with get_conn() as conn:
        conn.execute(
            f"UPDATE guest_sessions SET {sets} WHERE telegram_id=? AND bot_type=? AND is_active=1", vals
        )
        conn.commit()


def get_guest_session(telegram_id: int, bot_type: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM guest_sessions WHERE telegram_id=? AND bot_type=? AND is_active=1",
            (telegram_id, bot_type)
        ).fetchone()
        return dict(row) if row else None


def log_message(session_id: int, sender: str, content: str,
                sentiment: str = "", intent: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, sender, content, sentiment, intent) VALUES (?,?,?,?,?)",
            (session_id, sender, content, sentiment, intent)
        )
        conn.execute(
            "UPDATE guest_sessions SET messages_count=messages_count+1, updated_at=? WHERE session_id=?",
            (datetime.utcnow().isoformat(), session_id)
        )
        conn.commit()


def update_review_score(session_id: int, delta: float):
    with get_conn() as conn:
        conn.execute(
            "UPDATE guest_sessions SET review_score=MAX(1.0, MIN(5.0, review_score+?)) WHERE session_id=?",
            (delta, session_id)
        )
        conn.commit()


# ─── Onboarding Session Operations ───────────────────────────────────────────

def get_or_create_onboarding(telegram_id: int) -> Dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM onboarding_sessions WHERE telegram_id=?", (telegram_id,)).fetchone()
        if row:
            return dict(row)
        conn.execute("INSERT INTO onboarding_sessions (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()
        return dict(conn.execute("SELECT * FROM onboarding_sessions WHERE telegram_id=?", (telegram_id,)).fetchone())


def update_onboarding(telegram_id: int, state: str = None, data_update: Dict = None, language: str = None):
    ob = get_or_create_onboarding(telegram_id)
    current_data = json.loads(ob.get("data", "{}"))
    if data_update:
        current_data.update(data_update)
    updates = {"data": json.dumps(current_data, ensure_ascii=False), "updated_at": datetime.utcnow().isoformat()}
    if state:
        updates["state"] = state
    if language:
        updates["language"] = language
    sets = ", ".join(f"{k}=?" for k in updates)
    vals = list(updates.values()) + [telegram_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE onboarding_sessions SET {sets} WHERE telegram_id=?", vals)
        conn.commit()


def get_onboarding(telegram_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM onboarding_sessions WHERE telegram_id=?", (telegram_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["data"] = json.loads(d.get("data", "{}"))
        return d


def reset_onboarding(telegram_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM onboarding_sessions WHERE telegram_id=?", (telegram_id,))
        conn.commit()


# ─── Escalation Operations ────────────────────────────────────────────────────

def log_escalation(session_id: int, property_id: Optional[int], esc_type: str,
                   guest_msg: str, bot_response: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO escalations (session_id, property_id, esc_type, guest_msg, bot_response) VALUES (?,?,?,?,?)",
            (session_id, property_id, esc_type, guest_msg, bot_response)
        )
        conn.commit()
        return cur.lastrowid


def mark_escalation_notified(esc_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE escalations SET host_notified=1 WHERE esc_id=?", (esc_id,))
        conn.commit()


# ─── Payment Operations ───────────────────────────────────────────────────────

def log_payment(host_id: int, pay_type: str, amount: float, reference: str = "", status: str = "pending") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO payments (host_id, pay_type, amount, reference, status) VALUES (?,?,?,?,?)",
            (host_id, pay_type, amount, reference, status)
        )
        conn.commit()
        return cur.lastrowid


def activate_trial(host_id: int):
    now = datetime.utcnow()
    end = now + timedelta(days=TRIAL_DAYS)
    update_host_by_id(host_id, status="trial", trial_start=now.isoformat(), trial_end=end.isoformat())


def update_host_by_id(host_id: int, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [host_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE hosts SET {sets} WHERE host_id=?", vals)
        conn.commit()
