# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from openai import AzureOpenAI
# from azure.search.documents import SearchClient
# from azure.search.documents.models import VectorizedQuery
# from azure.core.credentials import AzureKeyCredential
# from azure.storage.blob import BlobServiceClient
# import fitz
# import random

# # Azure設定
# service_name = "maps"
# admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
# connection_string = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"
# endpoint = f"https://{service_name}.search.windows.net/"
# index_name = "vector-1725588957492"

# # クライアント初期化
# credential = AzureKeyCredential(admin_key)
# search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# app = FastAPI()

# # Azure OpenAI 初期化
# def get_azure_openai_client():
#     return AzureOpenAI(
#         api_version="2023-03-15-preview",
#         azure_endpoint="https://ateamopenai.openai.azure.com/",
#         api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
#     )

# # APIリクエストモデル
# class ChatRequest(BaseModel):
#     message: str

# class SearchRequest(BaseModel):
#     query: str
#     top: int = 5

# @app.post("/chat")
# def chat(request: ChatRequest):
#     client = get_azure_openai_client()
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-35-turbo",
#             messages=[{"role": "user", "content": request.message}]
#         )
#         return {"response": completion.choices[0].message.content}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/search/vector")
# def search_vector(request: SearchRequest):
#     try:
#         vector_query = VectorizedQuery(
#             vector=[0.1, 0.2, 0.3],  # 仮のベクトル、実際には get_embedding(request.query) などを使用
#             fields="text_vector"
#         )
#         results = search_client.search(
#             search_text="",
#             vector_queries=[vector_query],
#             top=request.top
#         )
#         return {"results": [doc for doc in results]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/storage/list")
# def list_containers():
#     try:
#         containers = blob_service_client.list_containers()
#         return {"containers": [container['name'] for container in containers]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/storage/random-pdf")
# def random_pdf_claims(count: int = 3):
#     try:
#         container_name = "azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd"
#         container_client = blob_service_client.get_container_client(container_name)
#         blobs = list(container_client.list_blobs())
#         random_blobs = random.sample(blobs, count)
#         result = []
#         for pdf_blob in random_blobs:
#             blob_client = container_client.get_blob_client(pdf_blob.name)
#             pdf_data = blob_client.download_blob().readall()
#             with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
#                 for page in pdf_document:
#                     text = page.get_text()
#                     if "【請求項" in text:
#                         result.append({"title": pdf_blob.name, "text": text})
#                         break
#         return {"claims": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
