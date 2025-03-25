import logging
from urllib import response
from Mapslog.azure_search import search_sample_hybrid, search_sample_index, search_sample_semantic, search_sample_vector
from Mapslog.openAI import chat_sample
from shared.azure_db import get_storage_name_List
import azure.functions as func
import os
import sys
import json



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


search_map = {
    "vector": search_sample_vector,
    "index": search_sample_index,
    "hybrid": search_sample_hybrid,
    "semantic": search_sample_semantic
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.',{req})

    name = req.params.get('name')
    temp = req.params.get('sample_number')
    req_body:any
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
            temp = req_body.get('sample_number')
    titles = [claim["title"] for claim in temp] 
    combined_claims = "\n\n".join([f"{claim['text']}" for claim in temp])
    # まとめたテキストを新しい請求項の生成用に加工
    prompt = (
        "以下に複数の請求項を示します。それらを基にして、新しい創造的な請求項を1つ作成してください。:\n\n"
        f"{combined_claims}\n\n"
        "これらを基にした新しい請求項を以下に記述してください。:"
    )
    text = chat_sample(prompt,req_body.get("model"))
    response["titles"]=titles
    response["search_text"]=temp
    response["create_text"]=text
    result_titles=[]
    # 検索の選択
    for result in search_map[req_body.get("search")](text,int(req_body.get("top"))):
        result_titles.append(result.get("title"))
    response["result_titles"]=result_titles
    #一致しているtitleをカウント
    match=sum(1 for title in result_titles if title in titles)
    response["match"]=match
    logging.info("search_result", extra={
        "custom_dimensions": {
            "sourceSize": int(req_body.get("top")),        # 元データ数
            "searchCount": int(req_body.get("search")),        # 検索数（横軸）
            "matchCount": match           # 一致数（縦軸）
        }
    })

    return func.HttpResponse(json.dumps(response), mimetype="application/json")

