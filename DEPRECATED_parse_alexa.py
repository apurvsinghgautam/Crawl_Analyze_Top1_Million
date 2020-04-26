import csv
import requests
from io import BytesIO
from zipfile import ZipFile

alexa_url = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
req = requests.get(alexa_url)
zf = ZipFile(BytesIO(req.content))
zf.extractall()

d = {}
with open('top-1m.csv') as f:
	reader = csv.reader(f)
	for row in reader:
		d[int(row[0])] = row[1]

print(len(d), "items parsed")
