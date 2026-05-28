import os, boto3, pymysql, pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from datetime import datetime

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    conn = pymysql.connect(
        host=os.environ['RDS_HOST'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        database='historical_events_db'
    )

    df = pd.read_sql("SELECT * FROM historical_events", conn)
    conn.close()

    buffer = BytesIO()
    pq.write_table(pa.Table.from_pandas(df), buffer)
    buffer.seek(0)

    key = f"raw/rds/historical_events_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.getvalue())

    return {'statusCode': 200, 'body': f'Guardado en {key}'}