-- Welcome Link PostgreSQL Migration
-- Führe dieses Skript auf deiner PostgreSQL-Datenbank aus

-- 1. Drop alte Tabellen falls sie existieren
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS status_checks CASCADE;

-- 2. Erstelle User-Tabelle mit korrektem Schema
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  is_admin BOOLEAN DEFAULT false
);

-- 3. Erstelle Properties-Tabelle (für Unterkünfte)
CREATE TABLE properties (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE,
  address VARCHAR(500),
  city VARCHAR(255),
  zip_code VARCHAR(20),
  country VARCHAR(100) DEFAULT 'Deutschland',
  phone VARCHAR(50),
  email VARCHAR(255),
  website VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);

-- 4. Erstelle Status Checks Tabelle
CREATE TABLE status_checks (
  id SERIAL PRIMARY KEY,
  property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
  check_type VARCHAR(50) NOT NULL,
  status VARCHAR(20) DEFAULT 'ok',
  message TEXT,
  checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Füge Demo-User hinzu (Passwort: Demo123!)
-- Hash generieren mit: bcrypt.hashpw(b'Demo123!', bcrypt.gensalt())
INSERT INTO users (email, password_hash, name, is_admin)
VALUES (
  'demo@welcome-link.de',
  '$2b$12$ExampleHashThatNeedsToBeReplacedWithRealBcryptHash',
  'Demo User',
  true
);

-- 6. Füge Demo-Property hinzu
INSERT INTO properties (user_id, name, slug, city)
VALUES (1, 'Demo Hotel', 'demo-hotel', 'Berlin');
