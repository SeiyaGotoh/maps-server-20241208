from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient # type: ignore
import numpy as np
from azure.search.documents.indexes import SearchIndexClient

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    VectorSearchAlgorithmConfiguration,
    VectorSearch
)

def main():
    ### AzureOpenAI クライアントの初期化と利用 ############################
    # 純粋なOpenAIの通信
    # ここでは、Azure OpenAI サービスに接続するためのクライアントを生成しています。
    # APIバージョンやエンドポイント、APIキーを指定しているため、これ以降の呼び出しはこの設定に基づいて行われます。
    client = AzureOpenAI(
        api_version="2023-03-15-preview",
        azure_endpoint="https://ateamopenai.openai.azure.com/",
        api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
    )

    # チャットのサンプル
    # 渡されたメッセージをもとにAzure OpenAI のチャット API を呼び出す。
    # チャットAPIは、メッセージをもとに応答を生成するため、メッセージを渡すと応答を返します。
    def chat_sample(message: str) -> str:
        completion = client.chat.completions.create(
            model="ateam-gpt-4o-mini", 
            messages=[
                {
                    "role": "user",
                    "content": message,
                },
            ],
        )
        return(completion.choices[0].message.content)

    service_name = "maps"
    admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
    index_name = "vector-1725588957492"

    ### Azure Search 関連の処理 ########################################
    # インデックスの作成
    # Azure Cognitive Search サービスに接続するためのクライアントを生成しています。
    credential = AzureKeyCredential(admin_key)
    endpoint = f"https://{service_name}.search.windows.net/"
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    # ベクターフィールドを含むインデックス定義
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True)
    ]

    # ベクターサーチの設定を含むインデックス定義
    index = SearchIndex(
        name=index_name,
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

    # ドキュメントのアップロード
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    # ベクター化されたサンプルデータ（例：文章の埋め込み）
    documents = [
        {"id": "1", "content": "This is a sample document.", "embedding": [0.1, 0.2, 0.3]},
        {"id": "2", "content": "Another example document.", "embedding": [0.2, 0.1, 0.4]}
    ]

    result = search_client.upload_documents(documents)
    print(f"Indexing status: {result}")


    # サンプルのクエリ用ベクトル（埋め込み）
    query_vector = np.array([0.1, 0.2, 0.3])

    # ベクター検索を実行
    vector_search_options = {
        "vector": query_vector.tolist(),
        "k": 3,  # 取得する結果の数
        "fields": "embedding"  # 検索するフィールド
    }

    search_results = search_client.search(
        search_text="",
        vector=vector_search_options,
        include_total_count=True
    )


