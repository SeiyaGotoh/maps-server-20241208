import logging
import traceback
from urllib import response
import azure.functions as func
from shared.batch_logic import run_batch 
import json
import uuid



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python batchjob function processed a request.{req}')
    
    try:
        run_id = str(uuid.uuid4())  # GUID発行
        logging.info('バッチ処理起動')
        
        run_batch(run_id)

        return func.HttpResponse(f"バッチ実行: {run_id}", status_code=200)
    except Exception as e:
        logging.error(f"500 Internal Server Error: {str(e)}")
        logging.error(traceback.format_exc())  # スタックトレースをログ出力
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


