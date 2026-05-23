import boto3

s3 = boto3.client('s3')

s3.upload_file(
    '../data/processed/games.csv',
    'tu-bucket',
    'games/games.csv'
)