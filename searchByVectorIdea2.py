import random
import numpy as np
import fitz
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchFieldDataType, SearchableField,
    VectorSearchAlgorithmConfiguration, VectorSearch
)
from openai import AzureOpenAI

# 変数
SERVICE_NAME = "maps"
ADMIN_KEY = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"
AZURE_ENDPOINT = f"https://{SERVICE_NAME}.search.windows.net/"
INDEX_NAME = "vector-1725588957492"

# クライアントの初期化
credential = AzureKeyCredential(ADMIN_KEY)
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
index_client = SearchIndexClient(endpoint=AZURE_ENDPOINT, credential=credential)
search_client = SearchClient(endpoint=AZURE_ENDPOINT, index_name=INDEX_NAME, credential=credential)
openai_client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e"
)

# Azure Blob Storage 関数

def get_storage_name_list():
    containers = blob_service_client.list_containers()
    return [container['name'] for container in containers]


def get_random_claims(count=3):
    container_client = blob_service_client.get_container_client("azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd")
    blobs = list(container_client.list_blobs())
    random_blobs = random.sample(blobs, count)
    result = []
    for pdf_blob in random_blobs:
        blob_client = container_client.get_blob_client(pdf_blob.name)
        pdf_data = blob_client.download_blob().readall()

        with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                text = page.get_text()
                start_index = text.find("【請求項")
                end_index = text.find("【発明の詳細な説明】")
                if start_index != -1:
                    next_claim_index = text.find("【請求項", start_index + 5)
                    end_index = next_claim_index if next_claim_index != -1 and next_claim_index < end_index else end_index
                    result.append({
                        "title": pdf_blob.name,
                        "page": page_number + 1,
                        "text": text[start_index:end_index] if end_index > start_index else text[start_index:]
                    })
                    break
    return result

# Azure Search 関数

def create_index():
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True)
    ]
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=VectorSearch(
            algorithm_configurations=[
                VectorSearchAlgorithmConfiguration(
                    name="default", kind="hnsw", parameters={"efConstruction": 128, "m": 16}
                )
            ]
        )
    )
    index_client.create_index(index)


def upload_documents(documents):
    return search_client.upload_documents(documents)


# OpenAI 関数

def get_embedding(text, engine="text-embedding-ada-002"):
    response = openai_client.embeddings.create(input=text, model=engine)
    return response.data[0].embedding


def chat_with_openai(message):
    completion = openai_client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[{"role": "user", "content": message}],
    )
    return completion.choices[0].message.content


# サンプル使用
if __name__ == "__main__":
    print("Available storage containers:", get_storage_name_list())
    print("Random claims:", get_random_claims())
    print("ChatGPT response:", chat_with_openai("特許の見方について教えて"))
