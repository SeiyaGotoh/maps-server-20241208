from shared.batch_logic import run_batch 
import logging
import azure.functions as func
import uuid
import threading



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python batchjob function processed a request.{req}')
    
    run_id = str(uuid.uuid4())  # GUID発行
    logging.info('バッチ処理起動')
    
    # バックグラウンドでバッチ処理を実行
    thread = threading.Thread(target=run_batch, args=(run_id,))
    thread.start()

    return func.HttpResponse(f"バッチ実行: {run_id}", status_code=200)


