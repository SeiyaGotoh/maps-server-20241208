# from azure.storage.blob import BlobServiceClient
# import random
# import fitz
# from openai import AzureOpenAI

# class AzureContainer:
#     # Azure Blob Storage の定数
#     CONNECTION_STRING = "AAAA"
#     CONTAINER_NAME = "BBBB"
    
#     @property
#     def blob_service_client(self):
#         return BlobServiceClient.from_connection_string(self.CONNECTION_STRING)
    
#     @property
#     def container_client(self):
#         return self.blob_service_client.get_container_client(self.CONTAINER_NAME)
    
#     def get_storage_name_list(self) -> list:
#         """
#         ストレージ内のコンテナ一覧を取得
#         """
#         containers = self.blob_service_client.list_containers()
#         return [container.name for container in containers]

#     def get_random_name_list(self, count: int = 3) -> list[dict]:
#         """
#         指定した数のPDFから請求項を取得
#         """
#         blobs = list(self.container_client.list_blobs())
#         random_blobs = random.sample(blobs, count)
#         result = []
        
#         for pdf_blob in random_blobs:
#             blob_client = self.container_client.get_blob_client(pdf_blob.name)
#             pdf_data = blob_client.download_blob().readall()
            
#             with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
#                 start_keyword = "【請求項"
#                 end_keyword = "【発明の詳細な説明】"
                
#                 for page_number in range(pdf_document.page_count):
#                     page = pdf_document.load_page(page_number)
#                     text = page.get_text()
                    
#                     start_index = text.find(start_keyword)
#                     end_index = text.find(end_keyword)
                    
#                     if start_index != -1:
#                         next_claim_index = text.find(start_keyword, start_index + len(start_keyword))
#                         end_desc_index = text.find(end_keyword, start_index + len(start_keyword))
                        
#                         if next_claim_index != -1 and (end_desc_index == -1 or next_claim_index < end_desc_index):
#                             end_index = next_claim_index
#                         else:
#                             end_index = end_desc_index
                    
#                     if start_index != -1 and end_index != -1 and end_index > start_index:
#                         relevant_text = text[start_index:end_index]
#                         result.append({
#                             "title": pdf_blob.name,
#                             "page": page_number + 1,
#                             "text": relevant_text.replace("\n", "")
#                         })
#                         break
#                     elif start_index != -1:
#                         result.append({
#                             "title": pdf_blob.name,
#                             "page": page_number + 1,
#                             "text": text[start_index:]
#                         })
#                         break
        
#         return result

# class AzureOpenAIClient:
#     """
#     Azure OpenAI クライアントのラッパークラス
#     """
#     # Azure OpenAI の定数
#     API_VERSION = "2023"
#     AZURE_ENDPOINT = "AAAA"
#     API_KEY = "BBBB"
    
#     @property
#     def client(self):
#         return AzureOpenAI(
#             api_version=self.API_VERSION,
#             azure_endpoint=self.AZURE_ENDPOINT,
#             api_key=self.API_KEY,
#         )
    
#     # 純粋なOpenAIの通信
#     def chat_sample(self, message: str, model: str = "gpt-35-turbo") -> str:
#         """
#         純粋なOpenAIの通信
#         """
#         completion = self.client.chat.completions.create(
#             model=model, 
#             messages=[
#                 {"role": "user", "content": message},
#             ],
#         ) 
#         return completion.choices[0].message.content
    
#     # ベクトル化の通信
#     def get_embedding(self, text: str, engine: str = "text-embedding-ada-002"):
#         """
#         ベクトル化の通信
#         """
#         response = self.client.embeddings.create(
#             input=text,
#             model=engine  # 埋め込みモデルの名前
#         )
#         return response.data[0].embedding

# # # 使用例
# # processor = AzureContainer()
# # container_list = processor.get_storage_name_list()
# # pdf_data_list = processor.get_random_name_list(3)

# # openai_client = AzureOpenAIClient()
# # response_text = openai_client.chat_sample("Hello, how are you?")
# # embedding_vector = openai_client.get_embedding("Sample text")
