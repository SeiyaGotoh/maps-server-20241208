import logging
from shared.azure_db import get_storage_name_List
import azure.functions as func
import os
import sys
import os
import sys

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
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        name = get_storage_name_List()[1]
        return func.HttpResponse(
             f"{name}This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
