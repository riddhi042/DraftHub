CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    username        VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    owner_id      UUID REFERENCES users(id) ON DELETE CASCADE,
    is_archived   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE member_role AS ENUM ('owner', 'editor', 'viewer');

CREATE TABLE IF NOT EXISTS project_members (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role       member_role NOT NULL DEFAULT 'viewer',
    joined_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (project_id, user_id)
);

CREATE TABLE IF NOT EXISTS blueprints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    current_version INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS blueprint_revisions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id      UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    uploader_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    version_number    INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename   VARCHAR(255) NOT NULL,
    file_path         VARCHAR(500) NOT NULL,
    file_size_bytes   INT,
    mime_type         VARCHAR(100),
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (blueprint_id, version_number)
);

CREATE TABLE IF NOT EXISTS