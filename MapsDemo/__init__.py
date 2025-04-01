import logging
import traceback
from urllib import response
import azure.functions as func
import os
import sys
import json



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python MapsDemo function processed a request.{req}')
    
    try:
        req_body = req.get_json()
        # 検索ワード
        word = req_body.get('word')
        # 検索数
        top = req_body.get('top')
        # ベクトル検索
        items = []
        for item in search_sample_vector(word,int(top)):
            items.append({
                "score": item["@search.score"],  # スコア追加
                "chunk": item["chunk"],          # ドキュメント全体
                "title": item["title"],          # タイトル
            }) 

        return func.HttpResponse(json.dumps({"result": items}, ensure_ascii=False), mimetype="application/json")
    except Exception as e:
        logging.error(f"500 Internal Server Error: {str(e)}")
        logging.error(traceback.format_exc())  # スタックトレースをログ出力
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


# azureの検索機能

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery


service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
index_name="vector-1725588957492"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"

# ベクトル検索
def search_sample_vector(message: str,top:int=5) -> str:
        logging.info(f'search_sample_vector function processed a message.{message}')
        search_client = SearchClient(endpoint, index_name, credential)
        # ベクトル検索を実行
        vector_query = VectorizableTextQuery(
                vector=message, k_nearest_neighbors=50, fields="text_vector", exhaustive=True
                )
        return search_client.search(
                search_text=message,# フルテキスト検索は空にします
                vector_queries=[vector_query],
                select=["title", "chunk_id", "chunk"],
                top=top 
        )
