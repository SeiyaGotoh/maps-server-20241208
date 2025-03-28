import logging
from urllib import response
import azure.functions as func
import os
import sys
import json



# 親ディレクトリを取得
parent_dir = os.path.dirname(os.path.abspath(__file__))

# .funcignore ファイルのパス
ignore_file = os.path.join(parent_dir, ".funcignore")


# .funcignore に記載されているフォルダ名をリストとして取得
ignore_folders = set()
if os.path.exists(ignore_file):
    with open(ignore_file, "r") as f:
        ignore_folders = set(line.strip() for line in f.readlines())

# 親ディレクトリ内のすべてのフォルダを追加（.funcignore に記載されたフォルダは除外）
for folder in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder)
    if os.path.isdir(folder_path) and folder not in ignore_folders:
        sys.path.append(folder_path)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.',{req})

    name = req.params.get('name')
    req_body = req.get_json()
    sample_number = req.params.get('sample_number')
    loop = int(req.params.get('loop') or 1)
    req_body:any
    
    for i in range(loop):
        sample_number = req_body.get('sample_number')
        temp = get_random_nameList(int(sample_number))
        titles = [claim["title"] for claim in temp] 
        combined_claims = "\n\n".join([f"{claim['text']}" for claim in temp])
        # まとめたテキストを新しい請求項の生成用に加工
        prompt = (
            "以下に複数の請求項を示します。それらを基にして、新しい創造的な請求項を1つ作成してください。:\n\n"
            f"{combined_claims}\n\n"
            "これらを基にした新しい請求項を以下に記述してください。:"
        )
        text = chat_sample(prompt,req_body.get("model"))
        response["titles"][i]=titles
        response["search_text"][i]=temp
        response["create_text"][i]=text
        result_titles=[]
        # 検索の選択
        for result in search_map[req_body.get("search")](text,int(req_body.get("top"))):
            result_titles.append(result.get("title"))
        response["result_titles"]=result_titles
        #一致しているtitleをカウント
        match=sum(1 for title in result_titles if title in titles)
        response["match"][i]=match
        logging.info("search_result", extra={
            "custom_dimensions": {
                "sourceSize": int(req_body.get("top")),        # 元データ数
                "searchCount": int(req_body.get("search")),        # 検索数（横軸）
                "matchCount": match           # 一致数（縦軸）
            }
        })

    return func.HttpResponse(json.dumps(response), mimetype="application/json")

from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)


def chat_sample(message: str,model:str="gpt-35-turbo") -> str:
    completion = client.chat.completions.create(
        model = model, 
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    ) 
    return(completion.choices[0].message.content)

def get_embedding(text: str, engine="text-embedding-ada-002"):
    # OpenAI埋め込みモデルを使用してテキストをベクトル化
    response = client.embeddings.create(
        input=text,
        model=engine  # 埋め込みモデルの名前
    )
    return response.data[0].embedding

from azure.storage.blob import BlobServiceClient
import random
import fitz
# import os
# from dotenv import load_dotenv
# # .env ファイルの読み込み (ローカル環境用)
# load_dotenv()

connection_string = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"

# コンテナの指定
container_name = "azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd"
# connection_string = os.getenv('connection_string', 'DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# コンテナの指定
# container_name = os.getenv('container_name', 'azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd')
container_client = blob_service_client.get_container_client(container_name)


# コンテナ一覧の取得
def get_storage_nameList():
    containers = blob_service_client.list_containers()
    for container in containers:
        print("Container Name:", container['name'])


# 選択した数PDFの請求項を取得
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
                        "text": relevant_text.replace("\n", "")
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

# azureの検索機能

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# import os
# from dotenv import load_dotenv
# # .env ファイルの読み込み (ローカル環境用)
# load_dotenv()

service_name = "maps"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
index_name="vector-1725588957492"
# service_name = os.getenv('service_name', 'default-secret-key')
# admin_key = os.getenv('admin_key', 'default-secret-key')
credential = AzureKeyCredential(admin_key)
endpoint = f"https://{service_name}.search.windows.net/"
# index_name = os.getenv('INDEX_NAME', 'default-secret-key')

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


# index検索
def search_sample_index(message: str,top:int=5) -> str:
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    # クエリを実行して検索
    query = message
    return client.search(search_text=query,top=top )


# ハイブリッド検索
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


# セマンティック検索
def search_sample_semantic(message: str,top:int=5) -> str:
        search_client = SearchClient(endpoint, index_name, credential)

        return search_client.search(
                search_text=message,
                query_type="semantic", 
                query_caption="extractive",  # 説明を含む結果を提供する設定
                query_answer="extractive",  # クエリに基づく要約回答を取得する
                top=top 
        )


search_map = {
    "vector": search_sample_vector,
    "index": search_sample_index,
    "hybrid": search_sample_hybrid,
    "semantic": search_sample_semantic
}