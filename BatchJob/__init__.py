import logging
import traceback
from urllib import response
import azure.functions as func
from shared.batch_logic import run_batch 
import json
import uuid



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Python batchjob function processed a request.{req}')
    
    run_id = str(uuid.uuid4())  # GUID発行
    logging.info('バッチ処理起動')
    
    run_batch(run_id)

    return func.HttpResponse(f"バッチ実行: {run_id}", status_code=200)


