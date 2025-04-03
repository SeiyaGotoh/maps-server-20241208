import logging
import json
from shared.batch_logic import run_batch

def main(msg: str):
    logging.info("QueueTrigger 起動しました。msg内容:")
    logging.info(msg)
    try:
        payload = json.loads(msg)
        run_id = payload.get("run_id", "unknown")
        logging.info(f"[{run_id}] バッチ処理開始")
    except Exception as e:
        logging.error(f"メッセージ解析失敗: {e}")
        run_id = "invalid"

    logging.info(f"[{run_id}] キュートリガーでバッチ処理を開始")
    run_batch(run_id)
