import logging
import azure.functions as func
import os
import sys
import json
from shared.old_search_logic import old_search_logic



# 親ディレクトリを取得
parent_dir = os.path.dirname(os.path.abspath(__file__))

# .funcignore ファイルのパス
ignore_file = os.path.join(parent_dir, ".funcignore")


# .funcignore に記載されているフォルダ名をリストとして取得
ignore_folders = set()
if os.path.exists(ignore_file):
    with open(ignore_file, "r") as f:
        ignore_folders = set(line.strip() for line in f.readlines())

# 親ディレクトリ内のすべてのフォルダを追加（.funcignore に記載されたフォルダは除外）
for folder in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder)
    if os.path.isdir(folder_path) and folder not in ignore_folders:
        sys.path.append(folder_path)


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info(f'Python HTTP trigger function processed a request.{req}')
    try:
        req_body = req.get_json()
        prop = {
            "sample_number" : int(req_body.get('sample_number')or 1),#生成に使用するサンプル数、0の時そのまま使用
            "try_times" : int(req_body.get('try_times')or 1),#
            "name" : req_body.get('name'),#
            "loop" : int(req_body.get('loop') or 1),#ループ回数
            "top" : int(req_body.get('top') or 1),#検索結果数
            "model":req_body.get("model"),#gptモデル
            "search":req_body.get("search"),#searchモデル
            "store" : req_body.get("store") or "summary-text-only-test",#store
            "index_name" : req_body.get("index_name") or "vector-summary-text-only-test"#store
        }
        # 検索ロジック
        response_data = old_search_logic(prop)

        return func.HttpResponse(json.dumps(response_data), mimetype="application/json")
    except Exception as e:
        logging.error(f'mago log.error={e}') 
        return func.HttpResponse(e, mimetype="application/json")
    