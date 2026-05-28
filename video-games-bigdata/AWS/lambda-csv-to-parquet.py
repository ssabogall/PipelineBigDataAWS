import os, boto3, pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO, StringIO
from datetime import datetime

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    obj = s3.get_object(Bucket=BUCKET, Key='raw/csv/car_brands.csv')
    df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))

    buffer = BytesIO()
    pq.write_table(pa.Table.from_pandas(df), buffer)
    buffer.seek(0)

    key = f"raw/csv/car_brands_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.getvalue())

    return {'statusCode': 200, 'body': f'Guardado en {key}'}