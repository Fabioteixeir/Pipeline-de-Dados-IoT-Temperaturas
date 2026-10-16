# Pipeline de Dados IoT — Temperaturas

Pipeline didático de dados IoT: lê um CSV público, trata leituras com Python/Pandas, grava no PostgreSQL em Docker e apresenta indicadores em um dashboard Streamlit/Plotly.

## Tecnologias

- Python, Pandas e SQLAlchemy
- PostgreSQL 16 com Docker Compose
- Streamlit e Plotly
- Git e GitHub

## Estrutura

```text
pipeline-iot-temperatura/
├── data/                  # CSV baixado do Kaggle (IOT-temp.csv)
├── src/
│   ├── pipeline.py        # Leitura, limpeza e carga no banco
│   └── dashboard.py       # Dashboard interativo
├── sql/views.sql          # Três views analíticas
├── docs/                  # Relatório PDF da disciplina
├── screenshots/           # Capturas reais do dashboard
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Fonte de dados

https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

O arquivo deve estar em `data/IOT-temp.csv`. Verifique os termos de uso do conjunto de dados antes de publicar o CSV.

## Pré-requisitos

Python 3.10 ou superior e Docker Desktop. Portas locais: `5432` (PostgreSQL) e `8501` (Streamlit).

## Início rápido (Windows)

- `INICIAR.bat` (duplo clique): modo simples, sem Docker. Usa SQLite com as mesmas três views e abre o dashboard.
- `INICIAR_COM_POSTGRES.bat`: usa PostgreSQL no Docker (abra o Docker Desktop antes).

Observação: os `.bat` criam o ambiente Python em `%LOCALAPPDATA%\pipeline-iot-venv` (caminho curto), o que evita o erro `WinError 206` quando a pasta do projeto fica em um caminho longo, como dentro do OneDrive.

## Instalação e execução manual

### 1. Ambiente Python

Windows (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Credenciais

Copie `.env.example` para `.env` (já incluído nesta versão). Se alterar a senha, altere em `POSTGRES_PASSWORD` e em `DATABASE_URL`. O `.env` é ignorado pelo Git.

### 3. Iniciar o PostgreSQL

Abra o Docker Desktop e rode:

```bash
docker compose up -d
docker ps
```

### 4. Importar e processar os dados

```bash
python src/pipeline.py
```

Resultado esperado: `Pipeline concluído: 97605 leituras gravadas e 3 views criadas.`

### 5. Abrir o dashboard

```bash
streamlit run src/dashboard.py
```

Acesse http://localhost:8501.

### 6. Conferir os dados no banco

```bash
docker exec -it postgres-iot psql -U iot_user -d iot_database
```

```sql
SELECT COUNT(*) FROM temperature_readings;
SELECT * FROM avg_temp_por_dispositivo;
SELECT * FROM leituras_por_hora;
SELECT * FROM temp_max_min_por_dia;
\q
```

Para parar o banco: `docker compose down`. Os dados persistem no volume Docker. `docker compose down -v` também apaga o volume e os dados.

## Views SQL

1. **`avg_temp_por_dispositivo`**: média de temperatura e quantidade de leituras por dispositivo; como o CSV não tem `device_id`, usa o tipo de localização (In/Out).
2. **`leituras_por_hora`**: contagem de registros por hora do dia.
3. **`temp_max_min_por_dia`**: temperaturas máxima, mínima e média por dia.

As definições estão em `sql/views.sql`; o pipeline cria as views automaticamente.

## Capturas de tela

Depois de executar o dashboard, salve capturas reais em `screenshots/` e inclua-as aqui:

```markdown
![Dashboard IoT](screenshots/dashboard.png)
```

## Limitações conhecidas

- O CSV precisa corresponder aos nomes de coluna tratados pelo script.
- A carga substitui a tabela a cada execução (adequada para demonstração, não para produção).
- Use senha local de desenvolvimento apenas em máquina própria; não publique `.env`.
