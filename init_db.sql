DROP TABLE IF EXISTS url;

CREATE TABLE url (
    original_url TEXT NOT NULL,
    short_url TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP NOT NULL,
    click_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_url_short_url ON url (short_url);
