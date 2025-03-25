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

