■TOBE
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

# Blobクライアントの設定
blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER)
output_container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER)

PROGRESS_FILE_NAME = "progress.txt"

def extract_summary(text: str) -> str:
    match = re.search(r'【要約】(.*?)<TXF', text, re.DOTALL)
    if match:
        summary = match.group(1).strip()
        summary = summary.replace("<BR>", "").strip()
        heading_patterns = [
            r'[【［](目\s?的)[】］]',
            r'[【［](構\s?成)[】］]',
            r'[【［](効果)[】］]',
        ]
        for pattern in heading_patterns:
            summary = re.sub(pattern, "", summary)
        summary = summary.split("<")[0].strip()
        return summary.strip()
    return ""

def get_last_processed_filename():
    try:
        blob_client = output_container_client.get_blob_client(PROGRESS_FILE_NAME)
        content = blob_client.download_blob().readall().decode("utf-8").strip()
        return content
    except Exception as e:
        logging.info("前回処理ファイル情報が見つかりません。初回または新規実行として扱います。")
        return None

def save_last_processed_filename(filename: str):
    blob_client = output_container_client.get_blob_client(PROGRESS_FILE_NAME)
    blob_client.upload_blob(filename, overwrite=True)

def main(req: func.HttpRequest) -> func.HttpResponse:
    file_count = 0
    logging.info(f"テキスト切り取り処理開始。開始時間：{datetime.datetime.now()}")

    # 前回処理済みファイル名を取得
    last_processed = get_last_processed_filename()
    skip = True if last_processed else False

    # 一覧取得し、ファイル名順にソート
    blobs = sorted(input_container_client.list_blobs(), key=lambda b: b.name)

    for blob in blobs:
        logging.info(f"処理対象チェック: {blob.name}")
        if skip:
            if blob.name == last_processed:
                skip = False  # 次のファイルから処理開始
            continue

        logging.info(f"処理開始・切抜き対象ファイル: {blob.name}")

        try:
            blob_client = input_container_client.get_blob_client(blob.name)
            blob_bytes = blob_client.download_blob().readall()
            encoding = chardet.detect(blob_bytes)["encoding"]
            blob_data = blob_bytes.decode(encoding)

            extracted_text = extract_summary(blob_data)
            logging.info(f"extracted_textの結果(空じゃないか？): {extracted_text}")

            if extracted_text:
                file_name = os.path.basename(blob.name)
                output_blob_client = output_container_client.get_blob_client(file_name)
                output_blob_client.upload_blob(extracted_text, overwrite=True)
                file_count += 1
                logging.info(f"要約抽出成功・保存済み: {file_name}")
                logging.info(f"現在保存したファイル件数：{file_count}")
                save_last_processed_filename(blob.name)  # 成功したら記録を更新
            else:
                logging.warning(f"要約が見つかりませんでした: {blob.name}")

        except Exception as e:
            logging.error(f"エラー発生（{blob.name}）: {str(e)}")

    logging.info("すべての処理が完了しました。")
    return func.HttpResponse("Blob processing completed.", status_code=200)
