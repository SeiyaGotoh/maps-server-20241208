# azureの検索機能
import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import VectorizableTextQuery
from openai import AzureOpenAI

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
index_name_0="vector-1725588957492"
# index_name="vector-summary-text-only-test"
# service_name = os.getenv('service_name', 'default-secret-key')
# admin_key = os.getenv('admin_key', 'default-secret-key')
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
# index_name = os.getenv('INDEX_NAME', 'default-secret-key')

client = AzureOpenAI(
    api_version="2025-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)

def get_embedding(text: str, engine="ateam-text-embedding-3-small"):
    # OpenAI埋め込みモデルを使用してテキストをベクトル化
    response = client.embeddings.create(
        input=text,
        model=engine  # 埋め込みモデルの名前
    )
    return response.data[0].embedding


# ベクトル検索
def search_sample_vector(message: str,top:int=5,index_name:str="vector-summary-text-only-test") -> str:
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


# index検索
def search_sample_index(message: str,top:int=5,index_name:str="vector-summary-text-only-test") -> str:
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    # クエリを実行して検索
    query = message
    return client.search(search_text=query,top=top )


# ハイブリッド検索
def search_sample_hybrid(message: str,top:int=5,index_name:str="vector-summary-text-only-test") -> str:
        logging.info(f'mago log.message={message}.top={top}')
        search_client = SearchClient(endpoint, index_name, credential)
        # ベクトル検索を実行
        vector_query = VectorizableTextQuery(
                text=message, 
                k_nearest_neighbors=50, 
                fields="text_vector", 
                exhaustive=True
                # top_k=5,  # 類似度の高い上位5件を取得
                # boost=1.0  # ベクトル検索の重要度（boost値）
        )
        return search_client.search(
                search_text=message,
                vector_queries=[vector_query],
                top=top 
        )


# セマンティック検索
def search_sample_semantic(message: str,top:int=5,index_name:str="vector-json-3000-summary-reference") -> str:
        search_client = SearchClient(endpoint, index_name, credential)

        return search_client.search(
                search_text=message,
                query_type="semantic", 
                query_caption="extractive",  # 説明を含む結果を提供する設定
                query_answer="extractive",   # クエリに基づく要約回答を取得する
                headers={"Accept-Language": "ja-JP"},
                semantic_configuration_name=f"{index_name}-semantic-configuration", 
                top=top 
        )
