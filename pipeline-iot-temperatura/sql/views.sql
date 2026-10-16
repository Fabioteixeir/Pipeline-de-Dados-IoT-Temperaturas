-- View 1: média por dispositivo quando disponível; caso contrário, por tipo de localização.
CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT
    COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown') AS device_id,
    AVG(temperature) AS avg_temp,
    COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown');

-- View 2: volume de leituras por hora do dia.
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT EXTRACT(HOUR FROM timestamp)::INTEGER AS hora,
       COUNT(*) AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY hora;

-- View 3: temperatura mínima, máxima e média por dia.
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT CAST(timestamp AS DATE) AS data,
       MAX(temperature) AS temp_max,
       MIN(temperature) AS temp_min,
       AVG(temperature) AS temp_media
FROM temperature_readings
GROUP BY CAST(timestamp AS DATE)
ORDER BY data;
