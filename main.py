from fastapi import FastAPI, File, Form, UploadFile, Depends
from fastapi.responses import HTMLResponse
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos import PartitionKey
from fastapi.responses import RedirectResponse
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Azure Blob Storage setup
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "uploads"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Azure CosmosDB setup
COSMOSDB_URL = "https://mycosodb123.documents.azure.com:443/"
COSMOSDB_KEY = os.getenv("COSMOSDB_KEY")
DATABASE_NAME = "fileDatabase"
CONTAINER_NAME = "files"
cosmos_client = CosmosClient(COSMOSDB_URL, credential=COSMOSDB_KEY)
database = cosmos_client.create_database_if_not_exists(id=DATABASE_NAME)
cosmos_container = database.create_container_if_not_exists(id=CONTAINER_NAME, partition_key=PartitionKey(path="/name") )

# HTML form for uploading files
@app.get("/", response_class=HTMLResponse)
def main():
    files = list(cosmos_container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
    files_html = "".join([f'<li><a href="{file["url"]}" target="_blank">{file["name"]}</a></li>' for file in files])
    return f"""
    <html>
        <body>
            <h2>Upload File</h2>
            <form action="/upload/" enctype="multipart/form-data" method="post">
                Name: <input type="text" name="name"> <br>
                File: <input type="file" name="file"> <br>
                <input type="submit" value="Upload">
            </form>
            <h2>Uploaded Files</h2>
            <ul>{files_html}</ul>
        </body>
    </html>
    """

# Upload file endpoint
@app.post("/upload/")
def upload_file(name: str = Form(...), file: UploadFile = File(...)):
    blob_client = blob_container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file.file.read(), overwrite=True)
    file_url = f"{blob_client.url}"

    cosmos_container.create_item({"id": name, "name": name, "url": file_url})
    return RedirectResponse(url="/", status_code=303)
