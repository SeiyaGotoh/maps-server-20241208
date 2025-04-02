# shared/batch_logic.py


from shared.azure_db import get_storage_name_List 
import time
import logging

def run_batch(run_id: str):
    log_prefix = f"[{run_id}]"
    logging.info(f"{log_prefix} バッチ処理を開始します")

    try:
        
        logging.info(f"{log_prefix} バッチ処理 - 20分待機開始")
        time.sleep(20 * 60)  # 20分待機（= 1200秒）
        logging.info(f"{log_prefix} 20分待機終了 - 処理完了")
        container_list = get_storage_name_List()
        
        logging.info(f"{log_prefix} 結果:{container_list}")
        logging.info(f"{log_prefix} バッチ処理が正常に完了しました")

    except Exception as e:
        logging.exception(f"{log_prefix} バッチ処理中にエラーが発生しました: {e}")
