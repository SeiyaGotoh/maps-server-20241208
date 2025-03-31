import logging
from urllib import response
import azure.functions as func
import os
import sys
import json



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python MapsDemo function processed a request.',{req})

    req_body = req.get_json()
    # 検索ワード
    word = req_body.params.get('word')
    # 検索数
    top = req_body.get('top')

    result_titles=[]
    # 検索の選択
    response["result"]=search_sample_vector(word,int(top))

    return func.HttpResponse(json.dumps(response), mimetype="application/json")

from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)

def get_embedding(text: str, engine="text-embedding-ada-002"):
    # OpenAI埋め込みモデルを使用してテキストをベクトル化
    response = client.embeddings.create(
        input=text,
        model=engine  # 埋め込みモデルの名前
    )
    return response.data[0].embedding


# azureの検索機能

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
index_name="vector-1725588957492"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"

# ベクトル検索
def search_sample_vector(message: str,top:int=5) -> str:
        search_client = SearchClient(endpoint, index_name, credential)
        # ベクトル検索を実行
        vector_query = VectorizedQuery(
                vector=get_embedding(message),
                fields="text_vector"
                )
        return search_client.search(
                search_text="",# フルテキスト検索は空にします
                vector_queries=[vector_query],
                top=top 
        )
