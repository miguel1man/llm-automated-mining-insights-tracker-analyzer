-- Creación de tablas para el sistema de scraping

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de programación de scraping
CREATE TABLE IF NOT EXISTS scraping_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de configuración de scraping
CREATE TABLE IF NOT EXISTS scrape_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_name TEXT NOT NULL,
    selectors JSONB NOT NULL,
    auth_settings JSONB,
    retry_interval INTERVAL DEFAULT '1 hour',
    max_retries SMALLINT DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de trabajos de scraping
CREATE TABLE IF NOT EXISTS scraping_job (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES scraping_schedule(id) ON DELETE SET NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    total_urls SMALLINT DEFAULT 0,
    success_count SMALLINT DEFAULT 0,
    error_count SMALLINT DEFAULT 0,
    status VARCHAR CHECK (status IN ('pending', 'running', 'completed', 'failed')) DEFAULT 'pending'
);

-- Tabla de URLs a scrapear
CREATE TABLE IF NOT EXISTS scrape_url (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID REFERENCES scrape_config(id) ON DELETE CASCADE,
    job_id UUID REFERENCES scraping_job(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    status VARCHAR CHECK (status IN ('pending', 'in_progress', 'success', 'failed')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    priority SMALLINT DEFAULT 5 CHECK (priority BETWEEN 1 AND 10)
);

-- Tabla de datos scrapeados
CREATE TABLE IF NOT EXISTS scraped_data (
    url_id UUID PRIMARY KEY REFERENCES scrape_url(id) ON DELETE CASCADE,
    raw_payload JSONB NOT NULL,
    cleaned_text TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    job_id UUID REFERENCES scraping_job(id) ON DELETE CASCADE
);

-- Tabla de errores de scraping
CREATE TABLE IF NOT EXISTS scrape_error (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_id UUID REFERENCES scrape_url(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    job_id UUID REFERENCES scraping_job(id) ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_scraping_schedule_scheduled_at ON scraping_schedule(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scraping_job_schedule_id ON scraping_job(schedule_id);
CREATE INDEX IF NOT EXISTS idx_scrape_url_job_id ON scrape_url(job_id);
CREATE INDEX IF NOT EXISTS idx_scrape_url_config_id ON scrape_url(config_id);
CREATE INDEX IF NOT EXISTS idx_scraped_data_job_id ON scraped_data(job_id);
CREATE INDEX IF NOT EXISTS idx_scrape_error_url_id ON scrape_error(url_id);
CREATE INDEX IF NOT EXISTS idx_scrape_error_job_id ON scrape_error(job_id);

-- Funciones de actualización automática de timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar automáticamente el campo updated_at
CREATE TRIGGER update_user_updated_at
BEFORE UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_scraping_schedule_updated_at
BEFORE UPDATE ON scraping_schedule
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_scrape_config_updated_at
BEFORE UPDATE ON scrape_config
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Función para actualizar automáticamente el contador de URLs totales, exitosas y con errores
CREATE OR REPLACE FUNCTION update_job_counts()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE scraping_job
    SET 
        total_urls = (SELECT COUNT(*) FROM scrape_url WHERE job_id = NEW.job_id),
        success_count = (SELECT COUNT(*) FROM scrape_url WHERE job_id = NEW.job_id AND status = 'success'),
        error_count = (SELECT COUNT(*) FROM scrape_url WHERE job_id = NEW.job_id AND status = 'failed')
    WHERE id = NEW.job_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar contadores cuando cambia el estado de una URL
CREATE TRIGGER update_job_counts_trigger
AFTER INSERT OR UPDATE OF status ON scrape_url
FOR EACH ROW
EXECUTE FUNCTION update_job_counts();

-- Función para actualizar el estado del trabajo cuando todas las URLs están procesadas
CREATE OR REPLACE FUNCTION update_job_status()
RETURNS TRIGGER AS $$
DECLARE
    pending_count INTEGER;
    in_progress_count INTEGER;
BEGIN
    -- Contar URLs pendientes y en progreso
    SELECT 
        COUNT(*) FILTER (WHERE status = 'pending'),
        COUNT(*) FILTER (WHERE status = 'in_progress')
    INTO pending_count, in_progress_count
    FROM scrape_url
    WHERE job_id = NEW.job_id;
    
    -- Si no hay URLs pendientes ni en progreso, marcar el trabajo como completado
    IF pending_count = 0 AND in_progress_count = 0 AND NEW.status = 'running' THEN
        UPDATE scraping_job
        SET 
            status = 'completed',
            finished_at = NOW()
        WHERE id = NEW.job_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar el estado del trabajo
CREATE TRIGGER update_job_status_trigger
AFTER UPDATE OF status ON scrape_url
FOR EACH ROW
EXECUTE FUNCTION update_job_status();

-- Políticas de Row Level Security (RLS)
-- Habilitar RLS en todas las tablas
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_job ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_url ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraped_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_error ENABLE ROW LEVEL SECURITY;

-- Política para que los usuarios solo vean y modifiquen sus propios datos
CREATE POLICY user_policy ON "user"
    USING (id = auth.uid());

-- Política para programaciones - usuario solo ve sus propias programaciones
CREATE POLICY schedule_select_policy ON scraping_schedule
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY schedule_insert_policy ON scraping_schedule
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY schedule_update_policy ON scraping_schedule
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY schedule_delete_policy ON scraping_schedule
    FOR DELETE USING (user_id = auth.uid());

-- Las demás políticas seguirían la misma lógica, asociando los registros al usuario
-- a través de las relaciones establecidas en el modelo de datos

-- Vista para facilitar el análisis de scraping completado
CREATE VIEW completed_scrapes AS
SELECT 
    j.id AS job_id,
    j.started_at,
    j.finished_at,
    j.total_urls,
    j.success_count,
    j.error_count,
    s.id AS schedule_id,
    s.scheduled_at,
    u.username AS scheduled_by
FROM scraping_job j
JOIN scraping_schedule s ON j.schedule_id = s.id
JOIN "user" u ON s.user_id = u.id
WHERE j.status = 'completed';

-- Vista para URLs con errores frecuentes
CREATE VIEW problematic_urls AS
SELECT 
    u.url,
    COUNT(e.id) AS error_count,
    MAX(e.occurred_at) AS last_error_date,
    string_agg(DISTINCT e.type, ', ') AS error_types
FROM scrape_url u
JOIN scrape_error e ON u.id = e.url_id
GROUP BY u.url
HAVING COUNT(e.id) > 3
ORDER BY error_count DESC;