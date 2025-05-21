import azure.functions as func
import logging
import os
import re
import json
import chardet
import time
import asyncio
from azure.storage.blob.aio import BlobServiceClient
from azure.data.tables import TableClient
from datetime import datetime

# 3000JSONsummary.pyのロジック
def clean_text(text):
    return text.replace('<BR>', '').replace('\r', '').replace('\n', '').strip()

def extract_purpose_and_composition(text: str):
    match = re.search(r'【要約】(.*?)【\s*(?:請求項\s*１|特許請求の範囲|発明の詳細な説明)\s*】', text, re.DOTALL)
    if not match:
        return "", ""
    summary = match.group(1).strip()
    summary = re.sub(r'<[^>]+>', '', summary)
    heading_patterns = [
        r'[【［](目\s*的)[】］]',
        r'[【［](構\s*成)[】］]',
        r'[【［](効果)[】］]'
    ]
    for pattern in heading_patterns:
        summary = re.sub(pattern, "", summary)
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    purpose = lines[0] if len(lines) > 0 else ""
    composition = lines[1] if len(lines) > 1 else ""
    return purpose, composition

def extract_named_field(pattern: str, content: str):
    match = re.search(pattern, content)
    return clean_text(match.group(1)) if match else ""

async def process_raw_file(blob_service_client, raw_container, processed_container, file_path, log):
    try:
        # 生データファイルの読み込み
        raw_blob_client = blob_service_client.get_blob_client(container=raw_container, blob=file_path)
        raw_data = await raw_blob_client.download_blob()
        content = raw_data.readall()
        detected = chardet.detect(content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        content = content.decode(encoding, errors='ignore')

        # データ抽出
        name = extract_named_field(r'【発明の名称】(.+)', content)
        classification = extract_named_field(r'【国際特許分類.*?】([\s\S]+?)\n【', content)
        purpose, composition = extract_purpose_and_composition(content)
        summary = (purpose + composition).strip()

        # JSONデータ作成
        data = {
            'name': name,
            'classification': classification,
            'summary': summary
        }

        # 処理後コンテナに保存（コンテナ直下、.json）
        output_filename = file_path.split('/')[-1].replace('.TXT', '.json')
        processed_blob_client = blob_service_client.get_blob_client(container=processed_container, blob=output_filename)
        await processed_blob_client.upload_blob(json.dumps(data, ensure_ascii=False, indent=4), overwrite=True)
        log.info(f"Processed: {file_path} -> {output_filename}")
        return file_path, "Success", ""
    except Exception as e:
        log.error(f"Error processing {file_path}: {str(e)}")
        return file_path, "Error", str(e)

async def main(timer: func.TimerRequest) -> None:
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)

    # 環境変数
    # 接続文字列
    connection_string = os.environ["PatentBlobConnectionString"]
    # ファイル名一覧が格納されているコンテナ名
    file_name_container = "test-text-conversion-data"
    # 生データが入っているコンテナ名
    raw_container = "all-data-txt"
    # 処理済みデータを入れるコンテナ名
    processed_container = "json-summary"
    # 処理済みファイルのテーブル名
    processed_table = "ProcessedFiles"
    # エラーログを入れるテーブル名
    error_table = "ErrorLogs"

    # BlobおよびTableクライアント
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    table_client_processed = TableClient.from_connection_string(connection_string, processed_table)
    table_client_error = TableClient.from_connection_string(connection_string, error_table)

    async with blob_service_client:
        # 未処理のX.txtを取得
        container_client = blob_service_client.get_container_client(file_name_container)
        blobs = container_client.list_blobs()
        for blob in blobs:
            file_name = blob.name  # 例: 1.txt
            # 処理済みチェック
            try:
                entity = table_client_processed.get_entity(partition_key="Files", row_key=file_name)
                if entity.get("Status") == "Completed":
                    log.info(f"{file_name} already processed.")
                    continue
            except:
                pass

            # X.txtの内容を読み込む
            blob_client = container_client.get_blob_client(file_name)
            blob_data = await blob_client.download_blob()
            file_paths = blob_data.readall().decode('utf-8').splitlines()

            # タイムアウト対策（9分で中断）
            start_time = time.time()
            timeout_limit = 540  # 9分（秒）
            processed_paths = []
            error_logs = []

            # 逐次処理
            for file_path in file_paths:
                if time.time() - start_time > timeout_limit:
                    log.warning(f"Approaching timeout, stopping at {file_path}")
                    break
                result = await process_raw_file(blob_service_client, raw_container, processed_container, file_path, log)
                processed_paths.append(file_path)
                if result[1] == "Error":
                    error_logs.append({
                        "PartitionKey": "Errors",
                        "RowKey": file_path,
                        "FilePath": file_path,
                        "Error": result[2],
                        "Timestamp": datetime.utcnow().isoformat()
                    })

            # エラーログをTable Storageに保存
            for error_log in error_logs:
                table_client_error.upsert_entity(error_log)

            # 未処理のファイルパスを再処理用に保存
            remaining_paths = [p for p in file_paths if p not in processed_paths]
            if remaining_paths:
                retry_blob_client = container_client.get_blob_client(f"retry_{file_name}")
                await retry_blob_client.upload_blob("\n".join(remaining_paths), overwrite=True)
                log.info(f"Saved {len(remaining_paths)} unprocessed paths to retry_{file_name}")
            else:
                # 処理済みとして記録
                table_client_processed.upsert_entity({
                    "PartitionKey": "Files",
                    "RowKey": file_name,
                    "Status": "Completed",
                    "ProcessedAt": datetime.utcnow().isoformat()
                })
                log.info(f"Completed processing: {file_name}")
            break  # 1ファイル処理後終了（検証用）

# Timerトリガー関数
app.function_name(name="ProcessFileList")
app.schedule(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=True)(main)
