import sqlite3

DATABASE = "events.db"

# ======================================================
# INITIALIZE DATABASE
# ======================================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            device TEXT NOT NULL,

            event TEXT NOT NULL,

            severity TEXT NOT NULL,

            message TEXT

        )

    """)

    conn.commit()

    conn.close()

# ======================================================
# INSERT EVENT
# ======================================================

def insert_event(
    timestamp,
    device,
    event,
    severity,
    message
):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO events(

            timestamp,
            device,
            event,
            severity,
            message

        )

        VALUES(?,?,?,?,?)

    """,(

        timestamp,
        device,
        event,
        severity,
        message

    ))

    conn.commit()

    conn.close()

# ======================================================
# GET EVENTS
# ======================================================

def get_events(limit=100):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM events

        ORDER BY id DESC

        LIMIT ?

    """,(limit,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

# ======================================================
# EVENT COUNT
# ======================================================

def get_event_count():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

# ======================================================
# CLEAR EVENTS
# ======================================================

def clear_events():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM events

    """)

    conn.commit()

    conn.close()

def get_recent_events(limit=20):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM events

        ORDER BY id DESC

        LIMIT ?

    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def get_last_event(device):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT event

        FROM events

        WHERE device=?

        ORDER BY id DESC

        LIMIT 1

    """, (device,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row["event"]

    return None

def get_statistics():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    stats = {}

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

    """)

    stats["total_events"] = cursor.fetchone()[0]

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

        WHERE event='POWER_LOST'

        AND DATE(timestamp)=DATE('now','localtime')

    """)

    stats["power_lost_today"] = cursor.fetchone()[0]

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

        WHERE event='POWER_RESTORED'

        AND DATE(timestamp)=DATE('now','localtime')

    """)

    stats["power_restored_today"] = cursor.fetchone()[0]

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

        WHERE event='SHUTDOWN_EXECUTED'

        AND DATE(timestamp)=DATE('now','localtime')

    """)

    stats["shutdown_today"] = cursor.fetchone()[0]

    cursor.execute("""

        SELECT COUNT(*)

        FROM events

        WHERE event='COUNTDOWN_STARTED'

        AND DATE(timestamp)=DATE('now','localtime')

    """)

    stats["countdown_today"] = cursor.fetchone()[0]

    conn.close()

    return stats

def get_recent_events_text(limit=10):

    events = get_recent_events(limit)

    if not events:

        return "No events"

    lines = []

    for e in events:

        lines.append(

            f"{e['timestamp']} | {e['event']}"

        )

    return "\n".join(lines)