# # azureの検索機能

# from Mapslog.openAI import get_embedding
# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.models import VectorizedQuery

# # import os
# # from dotenv import load_dotenv
# # # .env ファイルの読み込み (ローカル環境用)
# # load_dotenv()

# service_name = "maps"
# admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
# index_name="vector-1725588957492"
# # service_name = os.getenv('service_name', 'default-secret-key')
# # admin_key = os.getenv('admin_key', 'default-secret-key')
# credential = AzureKeyCredential(admin_key)
# endpoint = f"https://{service_name}.search.windows.net/"
# # index_name = os.getenv('INDEX_NAME', 'default-secret-key')

# # ベクトル検索
# def search_sample_vector(message: str,top:int=5) -> str:
#         search_client = SearchClient(endpoint, index_name, credential)
#         # ベクトル検索を実行
#         vector_query = VectorizedQuery(
#                 vector=get_embedding(message),
#                 fields="text_vector"
#                 )
#         return search_client.search(
#                 search_text="",# フルテキスト検索は空にします
#                 vector_queries=[vector_query],
#                 top=top 
#         )


# # index検索
# def search_sample_index(message: str,top:int=5) -> str:
#     client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

#     # クエリを実行して検索
#     query = message
#     return client.search(search_text=query,top=top )


# # ハイブリッド検索
# def search_sample_hybrid(message: str,top:int=5) -> str:
#         search_client = SearchClient(endpoint, index_name, credential)
#         # ベクトル検索を実行
#         vector_query = VectorizedQuery(
#                 vector=get_embedding(message),
#                 fields="text_vector",
#                 top_k=5,  # 類似度の高い上位5件を取得
#                 boost=1.0  # ベクトル検索の重要度（boost値）
#                 )
#         return search_client.search(
#                 search_text=message,
#                 vector_queries=[vector_query],
#                 top=top 
#         )


# # セマンティック検索
# def search_sample_semantic(message: str,top:int=5) -> str:
#         search_client = SearchClient(endpoint, index_name, credential)

#         return search_client.search(
#                 search_text=message,
#                 query_type="semantic", 
#                 query_caption="extractive",  # 説明を含む結果を提供する設定
#                 query_answer="extractive",  # クエリに基づく要約回答を取得する
#                 top=top 
#         )
