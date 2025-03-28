import shutil

import requests
import zipfile
import io

REPO_NAME = 'Fantasy-Premier-League-master'
URL = f"https://github.com/vaastav/Fantasy-Premier-League/archive/refs/heads/master.zip"

print("Downloading repo...")
response = requests.get(URL)
if response.status_code == 200:
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
        zip.extractall(f"../{REPO_NAME}")
    print(f"Repository downloaded.")
else:
    print("Failed to download repository")

print('Extracting data...')
shutil.move(f"../{REPO_NAME}/{REPO_NAME}/data", '../data')  # Rename as needed
shutil.rmtree(f"../{REPO_NAME}")  # Delete the rest
print("Data extracted.")