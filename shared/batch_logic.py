# shared/batch_logic.py


from shared.azure_db import get_storage_name_List 
import logging

def run_batch(run_id: str="test"):
    log_prefix = f"[{run_id}]"

    try:
        container_list = get_storage_name_List()
        
        logging.info(f"{log_prefix} バッチ結果:{container_list}")

    except Exception as e:
        logging.exception(f"{log_prefix} バッチ処理中にエラーが発生しました: {e}")
