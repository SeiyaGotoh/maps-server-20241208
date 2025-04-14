■ASIS
import datetime
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import re
import chardet

# 環境変数からストレージ接続文字列を取得
CONNECT_STR = os.getenv("PatentBlobConnectionString")
INPUT_CONTAINER = os.getenv("INPUT_BLOB_CONTAINER")  # 入力コンテナ名
OUTPUT_CONTAINER = os.getenv("OUTPUT_BLOB_CONTAINER")  # 出力コンテナ名

# Blobクライアントの作成
blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER)
output_container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER)

def extract_summary(text: str) -> str:
    """
    【要約】の部分のみを抽出し、【目的】や【構成】、【効果】、<BR>を削除
    """
    # 【要約】とその後のTXFタグを抽出
    match = re.search(r'【要約】(.*?)<TXF', text, re.DOTALL)

    if match:
        summary = match.group(1).strip()
        # <BR>を削除
        summary = summary.replace("<BR>", "").strip()

        # 見出し削除
        heading_patterns = [
            r'[【［](目\s?的)[】］]',   # 【目的】, ［目的］, 【目 的】など
            r'[【［](構\s?成)[】］]',   # 【構成】, ［構成］, 【構 成】など
            r'[【［](効果)[】］]',     # 【効果】, ［効果］
        ]
        for pattern in heading_patterns:
            summary = re.sub(pattern, "", summary)
        
        # <以降にゴミタグが残ってるケースに備えて除去
        summary = summary.split("<")[0].strip()

        return summary.strip()

    return ""

def main(req: func.HttpRequest) -> func.HttpResponse:

    file_count = 0
    logging.info(f"テキスト切り取り処理開始。開始時間：{datetime.datetime.now()}")
    
    # BLOB 一覧を取得
    blobs = input_container_client.list_blobs()

    for blob in blobs:
        logging.info(f"処理開始・切抜き対象ファイル: {blob.name}")

        # テキストデータの文字コードを取得
        blob_client = input_container_client.get_blob_client(blob.name)
        blob_bytes = blob_client.download_blob().readall()
        encoding = chardet.detect(blob_bytes)["encoding"]

        # テキストデータ読み取り
        blob_data = blob_bytes.decode(encoding)

        # 【要約】部分を抽出
        extracted_text = extract_summary(blob_data)

        if extracted_text:
            # ファイル名を取得（コンテナ直下に配置）
            file_name = os.path.basename(blob.name)  # フォルダ名を取り除く
            output_blob_client = output_container_client.get_blob_client(file_name)
            output_blob_client.upload_blob(extracted_text, overwrite=True)
            file_count += 1
            logging.info(f"要約抽出成功・保存済み: {file_name}")
            logging.info(f"現在保存したファイル件数：{file_count}")
        else:
            logging.warning(f"要約が見つかりませんでした: {blob.name}")

    logging.info("すべての処理が完了しました。")
    return func.HttpResponse("Blob processing completed.", status_code=200)
