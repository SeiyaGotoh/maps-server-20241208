###################################################################
# このファイルについての説明
# このファイルは、mago.ipynbをjupyter nbconvertコマンドを使用して
# Pythonファイルに変換したファイルの原本データです。
###################################################################


#!/usr/bin/env python
# coding: utf-8

# # azureの使用方法関数一覧
# - pipインストールは起動後に毎回必要
# - ※後日キーの置き換え

# ## DB周り

# #### azureのai searchのインデックス一覧取得

# In[17]:


get_ipython().run_line_magic('pip', 'install azure-core azure-search-documents')


# In[9]:


from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"

# SearchIndexClientを作成
index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

# インデックスの一覧を取得
indexes = index_client.list_indexes()

# インデックス名を表示
for index in indexes:
    print(f"Index Name: {index.name}")


# #### azureのストレージ一覧取得

# In[13]:


get_ipython().run_line_magic('pip', 'install azure-storage-blob azure-identity pymupdf')


# In[17]:


from azure.storage.blob import BlobServiceClient

# 接続文字列を設定
connection_string = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# # コンテナ一覧の取得
def get_storage_nameList():
    containers = blob_service_client.list_containers()
    for container in containers:
        print("Container Name:", container['name'])

get_storage_nameList()


# #### azureのストレージからランダムに請求項の取得

# In[ ]:


get_ipython().run_line_magic('pip', 'install azure-storage-blob azure-identity pymupdf')


# In[ ]:


from azure.storage.blob import BlobServiceClient
import random
import fitz

# 接続文字列を設定
connection_string = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# コンテナの指定
container_name = "azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd"
container_client = blob_service_client.get_container_client(container_name)


# 選択したPDFの内容を表示
def get_random_nameList(count:int=3) -> list[dict] :
    # BLOB一覧の取得
    blobs = list(container_client.list_blobs())
    random_blobs = random.sample(blobs, count)
    result = []
    for pdf_blob in random_blobs:
        # BLOBデータのダウンロード
        blob_client = container_client.get_blob_client(pdf_blob.name)
        pdf_data = blob_client.download_blob().readall()

        # PDFデータの読み取り
        with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
            # 開始と終了のキーワード
            start_keyword = "【請求項"
            end_keyword = "【発明の詳細な説明】"
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                text = page.get_text()

                # キーワードによる範囲抽出
                start_index = text.find(start_keyword)
                end_index = text.find(end_keyword)
                if start_index != -1:
                    # 最初のキーワードが見つかった場合、次のキーワードを探す
                    next_claim_index = text.find(start_keyword, start_index + len(start_keyword))
                    end_desc_index = text.find(end_keyword, start_index + len(start_keyword))

                    # 2つのインデックスのうち、存在する方か、より早く出現する方を終了位置とする
                    if next_claim_index != -1 and (end_desc_index == -1 or next_claim_index < end_desc_index):
                        end_index = next_claim_index
                    else:
                        end_index = end_desc_index

                if start_index != -1 and end_index != -1 and end_index > start_index:
                    # 該当部分の抽出と表示
                    relevant_text = text[start_index:end_index]
                    result.append({
                        "title": pdf_blob.name,
                        "page":page_number + 1,
                        "text": relevant_text
                    })
                    break
                elif start_index != -1:
                    # 終了キーワードが同ページにない場合、開始以降をすべて表示
                    result.append({
                        "title": pdf_blob.name,
                        "page":page_number + 1,
                        "text": text[start_index:]
                    })
                    break
    return result

get_random_nameList()


# ## azureのai活用

# #### 検索以外のサンプル

# ##### 純粋なベクトル化

# In[ ]:


get_ipython().run_line_magic('pip', 'install openai')


# In[ ]:


from openai import AzureOpenAI

# Azure OpenAI APIの設定
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

# クエリをベクトル化
query = "高速計算の簡略化"
query_vector = get_embedding(query)

print(f"Query Vector: {query_vector}")



# In[ ]:


get_ipython().run_line_magic('pip', 'install openai azure-search-documents')


# ##### 純粋なOpenAIの通信

# In[44]:


from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)
def chat_sample(message: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-35-turbo", 
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    )
    return(completion.choices[0].message.content)

chat_sample("特許の見方について教えて")


# #### azureのai searchの検索
# [公式](https://learn.microsoft.com/en-us/python/api/azure-search-documents/azure.search.documents.searchclient?view=azure-python)

# ##### vector

# In[42]:


from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
index_name="vector-1725588957492"

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


for result in search_sample_vector("電卓の高速化"):
    print("chunk:",result.get("chunk"))


# ##### index

# In[ ]:


from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# 必要な情報を設定
service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
index_name="vector-1725588957492"


def search_sample_index(message: str,top:int=5) -> str:
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    # クエリを実行して検索
    query = message
    return client.search(search_text=query,top=top )


for result in search_sample_index("電卓の高速化"):
    print("chunk:",result.get("chunk"))


# ##### hybrid

# In[20]:


from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
index_name="vector-1725588957492"

def search_sample_hybrid(message: str,top:int=5) -> str:
        search_client = SearchClient(endpoint, index_name, credential)
        # ベクトル検索を実行
        vector_query = VectorizedQuery(
                vector=get_embedding(message),
                fields="text_vector",
                top_k=5,  # 類似度の高い上位5件を取得
                boost=1.0  # ベクトル検索の重要度（boost値）
                )
        return search_client.search(
                search_text=message,
                vector_queries=[vector_query],
                top=top 
        )


for result in search_sample_hybrid("電卓の高速化"):
    print("chunk:",result.get("chunk"))


# ##### semantic
# - 検索エンジンが単純なキーワードの一致検索だけではなく、ユーザの意図やクエリの意味を理解して、関連性の高い情報を提供

# In[ ]:


from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
index_name="vector-1725588957492"

def search_sample_semantic(message: str,top:int=5) -> str:
        search_client = SearchClient(endpoint, index_name, credential)

        return search_client.search(
                search_text=message,
                query_type="semantic", 
                query_caption="extractive",  # 説明を含む結果を提供する設定
                query_answer="extractive",  # クエリに基づく要約回答を取得する
                top=top 
        )


for result in search_sample_semantic("電卓の高速化"):
    print("chunk:",result.get("chunk"))


# ## RAG実装

# #### RAG(ai searchの検索使用)

# In[1]:


get_ipython().run_line_magic('pip', 'install openai azure-search-documents azure-core')


# In[ ]:


from openai import AzureOpenAI


client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)

def chat_RAG_sample(query: str) -> str:
    # 検索結果を取得
    search_results = search_sample_vector(query,1)
    # 各種選択可能
    #search_sample_vector(query,1)
    #search_sample_index(query,1)
    #search_sample_hybrid(query,1)
    #search_sample_semantic(query,1)
    context = "\n".join([result["chunk"] for result in search_results])
    
    completion = client.completions.create(
        model="gpt-35-turbo", #ateam-gpt-4o-miniは未対応
        prompt=f"質問{query}あなたは特許の侵害に詳し弁護士です。以下のドキュメントを用いてuserの質問に答えてください。\n{context}",
        max_tokens=150
    )
    return(completion.choices[0].text)

chat_RAG_sample("電卓の高速化をする方法")


# ## 検証テストの実装

# ### ランダムに生成した請求項を取得可能であるか

# In[ ]:


def test()->int:
    temp=get_random_nameList()
    # タイトルを保存するリスト
    titles = [claim["title"] for claim in temp] 
    combined_claims = "\n\n".join([f"{claim['text']}" for claim in temp])
    # まとめたテキストを新しい請求項の生成用に加工
    prompt = (
        "以下に複数の請求項を示します。それらを基にして、新しい創造的な請求項を1つ作成してください。:\n\n"
        f"{combined_claims}\n\n"
        "これらを基にした新しい請求項を以下に記述してください。:"
    )
    text = chat_sample(prompt)
    print("titles",titles)
    print(text)
    result_titles=[]
    # 検索の選択
    for result in search_sample_vector(text):
        result_titles.append(result.get("title"))
    print("result_titles",result_titles)
    #一致しているtitleをカウント
    return sum(1 for title in result_titles if title in titles)
test()

