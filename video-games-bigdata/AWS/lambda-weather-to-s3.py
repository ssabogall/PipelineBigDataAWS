import json, os, boto3, requests, pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from datetime import datetime

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']
API_KEY = os.environ['WEATHER_API_KEY']

def lambda_handler(event, context):
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Medellin,CO&appid={API_KEY}&units=metric"
    resp = requests.get(url).json()

    df = pd.DataFrame([{
        'timestamp': datetime.utcnow().isoformat(),
        'temp': resp['main']['temp'],
        'feels_like': resp['main']['feels_like'],
        'humidity': resp['main']['humidity'],
        'pressure': resp['main']['pressure'],
        'wind_speed': resp['wind']['speed'],
        'clouds': resp['clouds']['all'],
        'description': resp['weather'][0]['description']
    }])

    buffer = BytesIO()
    pq.write_table(pa.Table.from_pandas(df), buffer)
    buffer.seek(0)

    key = f"raw/weather/weather_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.getvalue())

    return {'statusCode': 200, 'body': f'Guardado en {key}'}