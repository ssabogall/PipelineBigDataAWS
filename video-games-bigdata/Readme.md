                    ┌──────────────────┐
                    │ RAWG API         │
                    │ Internet Data    │
                    └────────┬─────────┘
                             │

                    ┌──────────────────┐
                    │ MariaDB RDS      │
                    │ Structured Data  │
                    └────────┬─────────┘
                             │

                    ┌──────────────────┐
                    │ EC2 Files        │
                    │ CSV / JSON       │
                    └────────┬─────────┘
                             │

              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼

        ETL Ingestion                PySpark Processing
        (Python/Colab)                 (EMR Cluster)

              │                             │
              └──────────────┬──────────────┘
                             ▼

                    AWS S3 Data Lake

                             ▼

                    Hive External Tables

                             ▼

                   Athena / Spark SQL

                             ▼

                    Analytics / Graphs