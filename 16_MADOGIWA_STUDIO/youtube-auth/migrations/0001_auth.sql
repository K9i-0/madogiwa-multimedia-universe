CREATE TABLE invitations (hash TEXT PRIMARY KEY, expires INTEGER NOT NULL);
CREATE TABLE sessions (state_hash TEXT PRIMARY KEY, browser_hash TEXT NOT NULL, verifier TEXT NOT NULL, expires INTEGER NOT NULL);
CREATE TABLE connections (channel_id TEXT PRIMARY KEY, title TEXT NOT NULL, encrypted_refresh TEXT NOT NULL, scopes TEXT NOT NULL, updated INTEGER NOT NULL);
