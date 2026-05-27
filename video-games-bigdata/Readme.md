# Pipeline Big Data — Local + AWS

Pipeline de ingestión y procesamiento de datos construido en dos etapas: primero de forma local con PySpark y luego desplegado en AWS como arquitectura cloud nativa.

---

## Arquitectura general

```
Etapa 1 — Local (Procesamiento)          Etapa 2 — Cloud (Ingestión + Consulta)
─────────────────────────────            ──────────────────────────────────────
OpenWeatherMap API                        OpenWeatherMap API
        │                                         │
        ▼                                         ▼ (cada hora)
MariaDB (XAMPP local)              EventBridge ──→ Lambda ──→ S3/raw/weather/
        │                                         
        ▼                                RDS MariaDB
CSV local (car_brands.csv)                        │
        │                                         ▼ (cada día)
        ▼                          EventBridge ──→ Lambda ──→ S3/raw/rds/
PySpark (local)
        │                                EC2 (car_brands.csv)
        ▼                                         │
Parquet / Visualización                           ▼ (cron 1pm Colombia)
                                      S3 trigger ──→ Lambda ──→ S3/raw/csv/
                                                  
                                                  │
                                                  ▼
                                           Glue Crawler
                                                  │
                                                  ▼
                                          Glue Data Catalog
                                                  │
                                                  ▼
                                               Athena
                                          (consultas SQL)
```

---

## Etapa 1 — Pipeline local con PySpark

### Descripción
Pipeline de datos construido localmente que consume tres fuentes heterogéneas, las transforma con PySpark y genera visualizaciones con Matplotlib.

### Tecnologías utilizadas

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.11 | Lenguaje base |
| PySpark | 4.1.1 | Procesamiento distribuido |
| pandas | 3.0.3 | Manipulación de DataFrames |
| SQLAlchemy | 2.0.49 | Conexión a base de datos |
| PyMySQL | 1.2.0 | Driver MySQL/MariaDB |
| Matplotlib | 3.10.9 | Visualizaciones |
| pyarrow | 24.0.0 | Serialización Parquet |
| MariaDB (XAMPP) | - | Base de datos local (puerto 3307) |
| OpenWeatherMap API | - | Datos del clima en tiempo real |

### Fuentes de datos

**Fuente 1 — API del clima (OpenWeatherMap)**
- Endpoint: `api.openweathermap.org/data/2.5/weather?q=Medellin,CO`
- Campos extraídos: temperatura, sensación térmica, humedad, presión, velocidad del viento, nubosidad, descripción
- Salida: `data/raw/weather_raw.json` → SparkDataFrame

**Fuente 2 — MariaDB local (XAMPP)**
- Conexión: `mysql+pymysql://root:@127.0.0.1:3307/historical_events_db`
- Tabla: `historical_events`
- Salida: pandas DataFrame → SparkDataFrame

**Fuente 3 — CSV local**
- Archivo: `data/processed/car_brands.csv`
- Columnas: `brand`, `country`, `rating`, `sales_2025`, `electric_model`
- 15 registros de marcas de carros con métricas de ventas y ratings
- Salida: SparkDataFrame + visualizaciones Matplotlib

### Proceso
1. Consumo de las tres fuentes en paralelo
2. Conversión a SparkDataFrames
3. Transformaciones y análisis con PySpark
4. Generación de visualizaciones (barras de ratings, línea de ventas)
5. Exportación a formato Parquet

### Estructura del proyecto local
```
video-games-bigdata/
├── notebooks/
│   ├── Distributed Multi-source ETL Notebook.ipynb
│   └── VideoGames_ETL.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── car_brands.csv
│   │   ├── games.csv
│   │   ├── historical_events.csv
│   │   └── weather_clean.csv
│   └── db_exports/
├── scripts/
├── requirements.txt
└── .env
```

---

## Etapa 2 — Ingestión de datos en AWS

### Descripción
Pipeline de ingestión automatizado en AWS que consume las mismas tres fuentes de datos y las deposita en un Data Lake en S3 como archivos Parquet, disponibles para consulta con Athena.

### Tecnologías utilizadas

| Servicio AWS | Rol |
|---|---|
| S3 | Data Lake — almacenamiento de archivos Parquet |
| Lambda (Python 3.11) | Funciones de ingestión por fuente |
| EventBridge Scheduler | Triggers automáticos por tiempo |
| RDS MariaDB | Base de datos relacional en cloud |
| EC2 (Amazon Linux) | Servidor para envío automático del CSV |
| Glue Crawler | Catalogación automática del esquema |
| Glue Data Catalog | Registro de tablas y metadatos |
| Athena | Consultas SQL sobre S3 |
| IAM (LabRole) | Gestión de permisos |
| CloudShell | Construcción del Lambda Layer en Linux |

### Dependencias del Lambda Layer

```
pandas, pyarrow, pymysql, requests
```

> El Layer fue compilado en Linux (CloudShell) para compatibilidad con el runtime de Lambda.

### Fuentes de datos y triggers

**Fuente 1 — API del clima → S3**
- Lambda: `lambda-weather-to-s3`
- Trigger: EventBridge `trigger-weather` → `rate(1 hour)`
- Salida: `s3://.../raw/weather/weather.parquet`

**Fuente 2 — RDS MariaDB → S3**
- Lambda: `lambda-rds-to-s3`
- Trigger: EventBridge `trigger-rds` → `rate(1 day)`
- Salida: `s3://.../raw/rds/historical_events.parquet`

**Fuente 3 — EC2 CSV → S3**
- EC2 ejecuta `send_to_s3.sh` vía cron todos los días a la 1pm (Colombia)
- Lambda: `lambda-csv-to-parquet`
- Trigger: S3 Event Notification (PUT en `raw/csv/*.csv`)
- Salida: `s3://.../raw/csv/parquet/car_brands.parquet`

### Estructura del bucket S3

```
data-pipeline-[nombre]/
├── raw/
│   ├── weather/
│   │   └── weather.parquet
│   ├── rds/
│   │   └── historical_events.parquet
│   └── csv/
│       ├── car_brands.csv           ← enviado por EC2
│       └── parquet/
│           └── car_brands.parquet   ← generado por Lambda
├── layers/
│   └── layer_linux.zip
└── athena-results/
```

### Consultas disponibles en Athena

```sql
-- Clima actual
SELECT * FROM weather LIMIT 10;

-- Eventos históricos
SELECT * FROM rds LIMIT 10;

-- Marcas por rating
SELECT * FROM car_brands_direct
ORDER BY rating DESC;

-- Marcas con modelo eléctrico
SELECT brand, country, rating
FROM car_brands_direct
WHERE electric_model = 'Yes'
ORDER BY rating DESC;

-- Cruce de fuentes: clima vs marcas eléctricas top
SELECT 
    w.timestamp,
    w.temp,
    w.description,
    c.brand,
    c.rating
FROM weather w
CROSS JOIN car_brands_direct c
WHERE c.electric_model = 'Yes'
AND c.rating > 9.0
ORDER BY c.rating DESC;
```

---

## Requisitos previos

### Local
- Python 3.11
- Java 8 o superior (requerido por PySpark)
- XAMPP con MariaDB corriendo en puerto 3307
- API Key de OpenWeatherMap

### AWS
- Cuenta AWS (se usó AWS Academy con LabRole)
- AWS CLI instalado y configurado
- Servicios habilitados: Lambda, S3, RDS, EC2, Glue, Athena, EventBridge

### Instalación local

```bash
pip install -r requirements.txt
```

Crear archivo `.env` con:
```
WEATHER_API_KEY=tu_api_key
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=
DB_NAME=historical_events_db
```

---

## Autor

Santiago Sabogal  
Sistemas Distribuidos — 2026-1