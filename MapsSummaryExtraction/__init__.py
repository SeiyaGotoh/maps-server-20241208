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
    match = re.search(r'【要約】(.*?)<TXF', text, re.DOTALL)  # 【要約】とその後のTXFタグを抽出
    if match:
        summary = match.group(1).strip()

        # 不要なタイトル部分を削除するためのパターン
        patterns_to_remove = [
            r'【目的】.*?【構成】',  # 【目的】と【構成】の間のテキスト
            r'【構成】.*?【効果】',  # 【構成】と【効果】の間のテキスト
            r'【目\s?的】.*?【構\s?成】',  # 【目  的】と【構  成】の間のテキスト
            r'【効果】.*$',  # 【効果】以降のテキスト
            r'［目的］.*?［構成］',  # ［目的］と［構成］の間のテキスト
            r'［目\s?的］.*?［構\s?成］',  # ［目  的］と［構  成］の間のテキスト
        ]
        
        # 不要な部分をすべて削除
        for pattern in patterns_to_remove:
            summary = re.sub(pattern, "", summary, flags=re.DOTALL)

        # <BR>を削除
        summary = summary.replace("<BR>", "").strip()

        # <以降の文字列を削除
        summary = summary.split("<")[0].strip()

        return summary.strip()

    return ""

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Azure Function がトリガーされました。")

    # BLOB 一覧を取得
    blobs = input_container_client.list_blobs()

    for blob in blobs:
        logging.info(f"処理開始・捜査対象ファイル: {blob.name}")

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
            # ファイル名を取得（コンテナ直下に配置）
            file_name = os.path.basename(blob.name)  # フォルダ名を取り除く
            output_blob_client = output_container_client.get_blob_client(file_name)
            output_blob_client.upload_blob(extracted_text, overwrite=True)
            logging.info(f"処理完了・保存済み: {file_name}")
        else:
            logging.warning(f"【要約】が見つかりませんでした: {blob.name}")

    logging.info("すべての処理が完了しました。")
    return func.HttpResponse("Blob processing completed.", status_code=200)
