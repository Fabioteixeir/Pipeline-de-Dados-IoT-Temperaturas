"""Importa leituras IoT do CSV para PostgreSQL e cria views analíticas."""
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
CSV_PATH = ROOT / "data" / "IOT-temp.csv"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://iot_user:iot_senha_local@localhost:5432/iot_database",
)
engine = create_engine(DATABASE_URL)


def load_csv(path: Path) -> pd.DataFrame:
    """Lê o CSV, padroniza os nomes e adapta as colunas conhecidas do Kaggle."""
    if not path.exists():
        raise FileNotFoundError(
            f"CSV não encontrado em {path}. Baixe o dataset do Kaggle e salve como IOT-temp.csv."
        )
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    # Nomes comuns no dataset Temperature Readings: IoT Devices.
    aliases = {
        "id": "reading_id",
        "room_id/id": "room_id",
        "noted_date": "timestamp",
        "temp": "temperature",
        "out/in": "location_type",
        "device_id": "device_id",
        "temperature": "temperature",
        "timestamp": "timestamp",
    }
    df = df.rename(columns={c: aliases[c] for c in df.columns if c in aliases})

    # O dataset pode não conter um identificador físico de dispositivo.
    if "device_id" not in df.columns:
        df["device_id"] = pd.NA
    if "room_id" not in df.columns:
        df["room_id"] = pd.NA
    if "location_type" not in df.columns:
        df["location_type"] = "unknown"

    required = {"timestamp", "temperature"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas essenciais ausentes: {sorted(missing)}. "
            f"Colunas encontradas: {list(df.columns)}"
        )

    if "reading_id" not in df.columns:
        df["reading_id"] = range(1, len(df) + 1)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["location_type"] = df["location_type"].astype("string").str.strip()
    df["device_id"] = df["device_id"].astype("string")
    df["room_id"] = df["room_id"].astype("string")
    df = df.dropna(subset=["timestamp", "temperature"])
    df = df.drop_duplicates(subset=["reading_id"])

    return df[
        ["reading_id", "device_id", "room_id", "timestamp", "temperature", "location_type"]
    ]


def create_views() -> None:
    """Cria três views para análise temporal e por tipo de localização."""
    statements = [
        """
        CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
        SELECT
            COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown') AS device_id,
            AVG(temperature) AS avg_temp,
            COUNT(*) AS total_leituras
        FROM temperature_readings
        GROUP BY COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown');
        """,
        """
        CREATE OR REPLACE VIEW leituras_por_hora AS
        SELECT EXTRACT(HOUR FROM timestamp)::INTEGER AS hora,
               COUNT(*) AS contagem
        FROM temperature_readings
        GROUP BY EXTRACT(HOUR FROM timestamp)
        ORDER BY hora;
        """,
        """
        CREATE OR REPLACE VIEW temp_max_min_por_dia AS
        SELECT CAST(timestamp AS DATE) AS data,
               MAX(temperature) AS temp_max,
               MIN(temperature) AS temp_min,
               AVG(temperature) AS temp_media
        FROM temperature_readings
        GROUP BY CAST(timestamp AS DATE)
        ORDER BY data;
        """,
    ]
    if engine.dialect.name == "sqlite":
        # SQLite nao tem CREATE OR REPLACE VIEW nem EXTRACT: usa sintaxe equivalente.
        statements = [
            "DROP VIEW IF EXISTS avg_temp_por_dispositivo",
            "DROP VIEW IF EXISTS leituras_por_hora",
            "DROP VIEW IF EXISTS temp_max_min_por_dia",
            """
            CREATE VIEW avg_temp_por_dispositivo AS
            SELECT
                COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown') AS device_id,
                AVG(temperature) AS avg_temp,
                COUNT(*) AS total_leituras
            FROM temperature_readings
            GROUP BY COALESCE(NULLIF(device_id, 'nan'), location_type, 'unknown');
            """,
            """
            CREATE VIEW leituras_por_hora AS
            SELECT CAST(strftime('%H', timestamp) AS INTEGER) AS hora,
                   COUNT(*) AS contagem
            FROM temperature_readings
            GROUP BY CAST(strftime('%H', timestamp) AS INTEGER)
            ORDER BY hora;
            """,
            """
            CREATE VIEW temp_max_min_por_dia AS
            SELECT DATE(timestamp) AS data,
                   MAX(temperature) AS temp_max,
                   MIN(temperature) AS temp_min,
                   AVG(temperature) AS temp_media
            FROM temperature_readings
            GROUP BY DATE(timestamp)
            ORDER BY data;
            """,
        ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def main() -> None:
    df = load_csv(CSV_PATH)
    if df.empty:
        raise ValueError("Nenhuma leitura válida foi encontrada no CSV.")
    # 'replace' torna a carga repetível para fins didáticos; em produção, prefira carga incremental.
    df.to_sql(
        "temperature_readings",
        engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi",
    )
    create_views()
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM temperature_readings")).scalar_one()
    print(f"Pipeline concluído: {total} leituras gravadas e 3 views criadas.")


if __name__ == "__main__":
    main()
