# Importing dataset

import requests

url = 'https://zenodo.org/record/1342401/files/Jakobovski/free-spoken-digit-dataset-v1.0.8.zip'
r = requests.get(url, allow_redirects=True)

open('archive.zip', 'wb').write(r.content)
