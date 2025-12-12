-- ECOA - Portal de Monitoramento de Notícias
-- Schema SQL para Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable text search extension for trigram search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ==========================================
-- ECOA_PROFILES TABLE
-- Extends Supabase Auth users with profile data
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    political_name TEXT,
    party TEXT,
    state TEXT,
    avatar_url TEXT,
    plan_type TEXT DEFAULT 'free' CHECK (plan_type IN ('free', 'pro')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE ecoa_profiles ENABLE ROW LEVEL SECURITY;

-- Policies for profiles
CREATE POLICY "Users can view their own profile"
    ON ecoa_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON ecoa_profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON ecoa_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ==========================================
-- ECOA_NEWS_SOURCES TABLE
-- Available news sources for scraping
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_news_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL,
    scraper_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default sources
INSERT INTO ecoa_news_sources (name, slug, base_url, scraper_type) VALUES
    ('G1', 'g1', 'https://g1.globo.com', 'g1'),
    ('CNN Brasil', 'cnn', 'https://www.cnnbrasil.com.br', 'cnn'),
    ('Twitter/X', 'twitter', 'https://twitter.com', 'twitter'),
    ('Threads', 'threads', 'https://www.threads.net', 'threads')
ON CONFLICT (slug) DO NOTHING;

-- ==========================================
-- ECOA_NEWS TABLE
-- Scraped news articles
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    image_url TEXT,
    author TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sentiment TEXT CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    sentiment_score DECIMAL(5,3),
    categories TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster searches
CREATE INDEX IF NOT EXISTS idx_ecoa_news_source ON ecoa_news(source);
CREATE INDEX IF NOT EXISTS idx_ecoa_news_published_at ON ecoa_news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_ecoa_news_sentiment ON ecoa_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_ecoa_news_title_trgm ON ecoa_news USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_ecoa_news_content_trgm ON ecoa_news USING gin(content gin_trgm_ops);

-- ==========================================
-- ECOA_MONITORED_TERMS TABLE
-- Terms/keywords that users want to monitor
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_monitored_terms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES ecoa_profiles(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, term)
);

-- Enable RLS
ALTER TABLE ecoa_monitored_terms ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view their own terms"
    ON ecoa_monitored_terms FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own terms"
    ON ecoa_monitored_terms FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own terms"
    ON ecoa_monitored_terms FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own terms"
    ON ecoa_monitored_terms FOR DELETE
    USING (auth.uid() = user_id);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_ecoa_monitored_terms_user ON ecoa_monitored_terms(user_id);
CREATE INDEX IF NOT EXISTS idx_ecoa_monitored_terms_term ON ecoa_monitored_terms(term);

-- ==========================================
-- ECOA_NEWS_TERM_MATCHES TABLE
-- Tracks which news articles match which terms
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_news_term_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    news_id UUID NOT NULL REFERENCES ecoa_news(id) ON DELETE CASCADE,
    term_id UUID NOT NULL REFERENCES ecoa_monitored_terms(id) ON DELETE CASCADE,
    match_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(news_id, term_id)
);

-- Index for faster joins
CREATE INDEX IF NOT EXISTS idx_ecoa_news_term_matches_news ON ecoa_news_term_matches(news_id);
CREATE INDEX IF NOT EXISTS idx_ecoa_news_term_matches_term ON ecoa_news_term_matches(term_id);

-- ==========================================
-- ECOA_ALERTS TABLE
-- User alert configurations
-- ==========================================
CREATE TABLE IF NOT EXISTS ecoa_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES ecoa_profiles(id) ON DELETE CASCADE,
    term_id UUID REFERENCES ecoa_monitored_terms(id) ON DELETE CASCADE,
    alert_type TEXT DEFAULT 'email' CHECK (alert_type IN ('email', 'push', 'sms')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE ecoa_alerts ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can manage their own alerts"
    ON ecoa_alerts FOR ALL
    USING (auth.uid() = user_id);

-- ==========================================
-- FUNCTIONS
-- ==========================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION ecoa_update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for profiles
CREATE TRIGGER update_ecoa_profiles_updated_at
    BEFORE UPDATE ON ecoa_profiles
    FOR EACH ROW
    EXECUTE FUNCTION ecoa_update_updated_at_column();

-- Trigger for monitored_terms
CREATE TRIGGER update_ecoa_monitored_terms_updated_at
    BEFORE UPDATE ON ecoa_monitored_terms
    FOR EACH ROW
    EXECUTE FUNCTION ecoa_update_updated_at_column();

-- Function to handle new user signup (auto-create profile)
CREATE OR REPLACE FUNCTION ecoa_handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO ecoa_profiles (id, full_name, plan_type)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'full_name',
        'free'
    );
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Trigger for auto-creating profile on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION ecoa_handle_new_user();

-- ==========================================
-- VIEWS
-- ==========================================

-- View for dashboard stats (per user)
CREATE OR REPLACE VIEW ecoa_user_dashboard_stats AS
SELECT
    mt.user_id,
    COUNT(DISTINCT n.id) as total_news,
    COUNT(DISTINCT CASE WHEN n.published_at >= CURRENT_DATE THEN n.id END) as news_today,
    COUNT(DISTINCT CASE WHEN n.sentiment = 'positive' THEN n.id END) as positive_mentions,
    COUNT(DISTINCT CASE WHEN n.sentiment = 'negative' THEN n.id END) as negative_mentions,
    COUNT(DISTINCT CASE WHEN n.sentiment = 'neutral' THEN n.id END) as neutral_mentions,
    COUNT(DISTINCT CASE WHEN mt.is_active THEN mt.id END) as active_terms
FROM ecoa_monitored_terms mt
LEFT JOIN ecoa_news_term_matches ntm ON mt.id = ntm.term_id
LEFT JOIN ecoa_news n ON ntm.news_id = n.id
GROUP BY mt.user_id;

-- ==========================================
-- SAMPLE DATA (Optional - for testing)
-- ==========================================

-- Uncomment below to insert sample news for testing
/*
INSERT INTO ecoa_news (source, title, summary, url, sentiment, sentiment_score, published_at) VALUES
('g1', 'Governo anuncia novo pacote de medidas econômicas', 'Ministro da Fazenda apresentou detalhes do plano', 'https://g1.globo.com/economia/noticia/1', 'neutral', 0.05, NOW() - INTERVAL '2 hours'),
('cnn', 'Deputado propõe reforma tributária simplificada', 'Projeto de lei visa reduzir burocracia para empresas', 'https://cnnbrasil.com.br/politica/noticia/1', 'positive', 0.35, NOW() - INTERVAL '5 hours'),
('g1', 'Senado aprova medida provisória sobre energia', 'Votação ocorreu na madrugada desta quarta-feira', 'https://g1.globo.com/politica/noticia/2', 'neutral', 0.0, NOW() - INTERVAL '1 day');
*/
