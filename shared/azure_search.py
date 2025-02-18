# # azureの検索機能

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.models import VectorizedQuery
# from function.openAiUtil import AzureContainer
# from function.openAiUtil import AzureOpenAIClient


# # import os
# # from dotenv import load_dotenv
# # # .env ファイルの読み込み (ローカル環境用)
# # load_dotenv()

# ### 検索機能 クライアントの初期化と利用 ############################
# # ここでは、各種検索に接続するためのクライアントを生成しています。
# # APIバージョンやエンドポイント、APIキーを指定しているため、これ以降の呼び出しはこの設定に基づいて行われます。
 

# # service_name = os.getenv('service_name', 'default-secret-key')
# # admin_key = os.getenv('admin_key', 'default-secret-key')
# # credential = AzureKeyCredential(admin_key)
# # endpoint = f"https://{service_name}.search.windows.net/"
# # index_name = os.getenv('INDEX_NAME', 'default-secret-key')

# class AzureSearchClient:
#     SERVICE_NAME = "maps"
#     ADMIN_KEY = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
#     INDEX_NAME = "vector-1725588957492"
    
#     @property
#     def credential(self):
#         return AzureKeyCredential(self.ADMIN_KEY)
    
#     @property
#     def endpoint(self):
#         return f"https://{self.SERVICE_NAME}.search.windows.net/"
    
    
# # ベクトル検索
#     def search_sample_vector(self, message: str, top: int = 5) -> str:
#         search_client = SearchClient(self.endpoint, self.INDEX_NAME, self.credential)
#         vector_query = VectorizedQuery(
#             vector=AzureOpenAIClient.get_embedding(message),
#             fields="text_vector"
#         )
#         return search_client.search(
#             search_text="",
#             vector_queries=[vector_query],
#             top=top
#         )
#  # index検索
#     def search_sample_index(self, message: str, top: int = 5) -> str:
#         client = SearchClient(endpoint=self.endpoint, index_name=self.INDEX_NAME, credential=self.credential)
#         return client.search(search_text=message, top=top)
# # ハイブリッド検索
#     def search_sample_hybrid(self, message: str, top: int = 5) -> str:
#         search_client = SearchClient(self.endpoint, self.INDEX_NAME, self.credential)
#         vector_query = VectorizedQuery(
#             vector=AzureOpenAIClient.get_embedding(message),
#             fields="text_vector",
#             top_k=5,
#             boost=1.0
#         )
#         return search_client.search(
#             search_text=message,
#             vector_queries=[vector_query],
#             top=top
#         )
# # セマンティック検索
#     def search_sample_semantic(self, message: str, top: int = 5) -> str:
#         search_client = SearchClient(self.endpoint, self.INDEX_NAME, self.credential)
#         return search_client.search(
#             search_text=message,
#             query_type="semantic",
#             query_caption="extractive",
#             query_answer="extractive",
#             top=top
#         )

# # # 使用例
# # search_client = AzureSearchClient()
# # vector_results = search_client.search_sample_vector("example query")
# # index_results = search_client.search_sample_index("example query")
# # hybrid_results = search_client.search_sample_hybrid("example query")
# # semantic_results = search_client.search_sample_semantic("example query")
