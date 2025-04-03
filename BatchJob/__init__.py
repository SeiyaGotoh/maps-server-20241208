from shared.batch_logic import run_batch 
import logging
import azure.functions as func
import uuid
import json
from azure.storage.queue import QueueClient
import os



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python batchjob function processed a request.{req}')
    
    run_id = str(uuid.uuid4())  # GUID発行
    logging.info('バッチ処理起動')
    
    # ストレージ接続文字列とキュー名（環境変数から取得）
    conn_str = os.environ["AzureWebQueueJobsStorage"]
    queue_name = "mago-batch-test-queue"

    # キュークライアントを作成してメッセージを送信
    queue_client = QueueClient.from_connection_string(conn_str, queue_name)
    queue_client.send_message(json.dumps({ "run_id": run_id }))

    return func.HttpResponse(f"バッチ実行ID: {run_id}", status_code=202)


