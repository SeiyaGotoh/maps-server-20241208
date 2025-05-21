import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import re
import chardet
from datetime import datetime

# ログ設定の追加（ファイル出力用）
log_file_path = os.path.join(os.getcwd(), 'function.log')
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, mode='w', encoding='utf-8'),
        logging.StreamHandler()  # これがあるとターミナルにも出る
    ]
)

# 環境変数からストレージ接続文字列を取得
# CONNECT_STR = os.getenv("PatentBlobConnectionString")
# INPUT_CONTAINER = os.getenv("INPUT_BLOB_CONTAINER")  # 入力コンテナ名
# OUTPUT_CONTAINER = os.getenv("OUTPUT_BLOB_CONTAINER")  # 出力コンテナ名
CONNECT_STR = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"
INPUT_CONTAINER = "all-data-txt"  # 入力コンテナ名
OUTPUT_CONTAINER = "summary-text-only"  # 出力コンテナ名

# Blobクライアントの作成
blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER)
output_container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER)

def extract_summary(text: str) -> str:
    """
    【要約】の中から、【目的】や【構成】等の見出し付きブロックを抽出・整形する。
    """
    match = re.search(r'【要約】(.*?)<TXF', text, re.DOTALL)
    if not match:
        return ""

    summary = match.group(1).strip()

    # <BR> を改行に置換しておく（見やすさ・区切り処理のため）
    summary = summary.replace("<BR>", "\n")

    # パターン定義（タイトル＋本文の抽出）
    patterns = [
        r'(【目的】.*?)(?=【構成】)',        # パターン③
        r'(【構成】.*?)(?=【効果】|$)',      # パターン③または終了
        r'(【目\s?的】.*?)(?=【構\s?成】)',   # パターン②（空白含む）
        r'(【構\s?成】.*?)(?=【効果】|$)',   # パターン②（空白含む）
        r'(［目的］.*?)(?=［構成］)',        # パターン①
        r'(［構成］.*?)(?=$)',              # パターン①（末尾まで）
    ]

    extracted_parts = []
    for pattern in patterns:
        matches = re.findall(pattern, summary, flags=re.DOTALL)
        extracted_parts.extend(matches)

    # 改行と空白を整形し、<以降の不要部分も削除
    cleaned_parts = []
    for part in extracted_parts:
        part = re.sub(r'<.*$', '', part.strip(), flags=re.DOTALL)  # <以降を削除
        part = re.sub(r'\s+', ' ', part)  # 改行・空白を1つの空白にまとめる
        cleaned_parts.append(part)

    return " ".join(cleaned_parts).strip()

from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Azure Function がトリガーされました。")

    # BLOB 一覧を取得
    blobs = list(input_container_client.list_blobs())  # 回数カウントのためにリスト化
    total_files = len(blobs)
    logging.info(f"処理対象ファイル数: {total_files}")

    for index, blob in enumerate(blobs, start=1):
        logging.info(f"[{index}/{total_files}] 処理開始: {blob.name}")

        # テキストデータの文字コードを取得
        blob_client = input_container_client.get_blob_client(blob.name)
        blob_bytes = blob_client.download_blob().readall()
        encoding = chardet.detect(blob_bytes)["encoding"]
        logging.info(f"検出された文字コード: {encoding}")

        # テキストデータ読み取り
        blob_data = blob_bytes.decode(encoding)

        # 【要約】部分を抽出
        extracted_text = extract_summary(blob_data)

        if extracted_text:
            # 書き出し前の時間ログ
            start_time = datetime.now()
            logging.info(f"[{index}] 書き出し開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # ファイル名を取得（コンテナ直下に配置）
            file_name = os.path.basename(blob.name)
            output_blob_client = output_container_client.get_blob_client(file_name)
            output_blob_client.upload_blob(extracted_text, overwrite=True)

            # 書き出し後の時間ログ
            end_time = datetime.now()
            logging.info(f"[{index}] 書き出し完了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info(f"[{index}] 処理完了・保存済み: {file_name}")
        else:
            logging.warning(f"[{index}] 【要約】が見つかりませんでした: {blob.name}")

    logging.info("すべての処理が完了しました。")
    return func.HttpResponse("Blob processing completed.", status_code=200)
