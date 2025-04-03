import logging
import json
from shared.batch_logic import run_batch

def main(msg: str):
    try:
        payload = json.loads(msg)
        run_id = payload.get("run_id", "unknown")
    except:
        run_id = "invalid"

    logging.info(f"[{run_id}] キュートリガーでバッチ処理を開始")
    run_batch(run_id)
