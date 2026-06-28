-- Neon PostgreSQL schema for Nixie Gold Bot distributed services
-- Run this once against your Neon database before deploying.

CREATE TABLE IF NOT EXISTS ticks (
    id        BIGSERIAL PRIMARY KEY,
    ts        TIMESTAMPTZ NOT NULL,
    bid       DOUBLE PRECISION NOT NULL,
    ask       DOUBLE PRECISION NOT NULL,
    volume    DOUBLE PRECISION,
    source    TEXT DEFAULT 'alpha_vantage_sim',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ticks_ts ON ticks (ts DESC);

CREATE TABLE IF NOT EXISTS signals (
    id          BIGSERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL,
    direction   TEXT NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    entry       DOUBLE PRECISION NOT NULL,
    sl          DOUBLE PRECISION NOT NULL,
    tp1         DOUBLE PRECISION,
    tp2         DOUBLE PRECISION,
    tp3         DOUBLE PRECISION,
    confidence  DOUBLE PRECISION CHECK (confidence BETWEEN 0 AND 100),
    regime      TEXT,
    level_name  TEXT,
    session     TEXT,
    latency_ms  DOUBLE PRECISION,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_ts ON signals (ts DESC);

CREATE TABLE IF NOT EXISTS orders (
    id                BIGSERIAL PRIMARY KEY,
    signal_id         BIGINT REFERENCES signals(id),
    telegram_sent_at  TIMESTAMPTZ,
    telegram_ok       BOOLEAN DEFAULT FALSE,
    status            TEXT DEFAULT 'pending',
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orders_signal_id ON orders (signal_id);
