import logging
import json
from shared.batch_logic import run_batch
import azure.functions as func

def main(msg: func.QueueMessage):
    logging.info("QueueTrigger 起動しました。msg内容:")
    logging.info(msg)
    try:
        if msg.dequeue_count > 1:
            logging.warning("このメッセージは2回目以降の処理です。スキップして削除します。")
            return 
        body = msg.get_body().decode("utf-8")
        payload = json.loads(body)
        run_id = payload.get("run_id", "unknown")
        logging.info(f"[{run_id}] バッチ処理開始")
        run_batch(run_id)
    except Exception as e:
        logging.error(f"メッセージ解析失敗: {e}")
        run_id = "invalid"

    logging.info(f"[{run_id}] キュートリガーでバッチ処理を開始")
    run_batch(run_id)
