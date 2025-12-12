-- ECOA News Monitoring Portal - MySQL Schema
-- Esse script é gerado automaticamente pelo SQLAlchemy, mas está aqui para referência

-- Users table
CREATE TABLE IF NOT EXISTS ecoa_users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    political_name VARCHAR(255),
    party VARCHAR(100),
    state VARCHAR(2),
    avatar_url VARCHAR(500),
    plan_type ENUM('free', 'pro') DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- News Sources table
CREATE TABLE IF NOT EXISTS ecoa_news_sources (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    base_url VARCHAR(255) NOT NULL,
    scraper_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- News table
CREATE TABLE IF NOT EXISTS ecoa_news (
    id VARCHAR(36) PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    image_url VARCHAR(1000),
    author VARCHAR(255),
    published_at DATETIME,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment ENUM('positive', 'negative', 'neutral'),
    sentiment_score FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_news_source (source),
    INDEX idx_news_published (published_at),
    INDEX idx_news_sentiment (sentiment),
    INDEX idx_news_source_published (source, published_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Monitored Terms table
CREATE TABLE IF NOT EXISTS ecoa_monitored_terms (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    term VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_term (user_id, term),
    INDEX idx_term (term),
    INDEX idx_term_user_active (user_id, is_active),
    FOREIGN KEY (user_id) REFERENCES ecoa_users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- News Term Matches table
CREATE TABLE IF NOT EXISTS ecoa_news_term_matches (
    id VARCHAR(36) PRIMARY KEY,
    news_id VARCHAR(36) NOT NULL,
    term_id VARCHAR(36) NOT NULL,
    match_count INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_news_term (news_id, term_id),
    INDEX idx_match_news (news_id),
    INDEX idx_match_term (term_id),
    FOREIGN KEY (news_id) REFERENCES ecoa_news(id) ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES ecoa_monitored_terms(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alerts table
CREATE TABLE IF NOT EXISTS ecoa_alerts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    term_id VARCHAR(36),
    news_id VARCHAR(36),
    alert_type ENUM('news_match', 'sentiment_alert', 'trending') NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alert_user (user_id),
    INDEX idx_alert_user_read (user_id, is_read),
    INDEX idx_alert_created (created_at),
    INDEX idx_alert_type (alert_type),
    FOREIGN KEY (user_id) REFERENCES ecoa_users(id) ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES ecoa_monitored_terms(id) ON DELETE SET NULL,
    FOREIGN KEY (news_id) REFERENCES ecoa_news(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default news sources
INSERT INTO ecoa_news_sources (id, name, slug, base_url, scraper_type, is_active) VALUES
    (UUID(), 'G1', 'g1', 'https://g1.globo.com', 'g1', TRUE),
    (UUID(), 'CNN Brasil', 'cnn', 'https://www.cnnbrasil.com.br', 'cnn', TRUE),
    (UUID(), 'Twitter/X', 'twitter', 'https://twitter.com', 'twitter', TRUE),
    (UUID(), 'Threads', 'threads', 'https://threads.net', 'threads', TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);
