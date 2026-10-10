-- Unchanged videos share a successful scan heartbeat; this table has no public cache trigger.
CREATE TABLE youtube_sync_status (
 id INTEGER PRIMARY KEY CHECK(id=1),
 checked_at TEXT NOT NULL
);
