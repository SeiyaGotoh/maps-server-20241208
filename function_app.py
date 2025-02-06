import azure.functions as func
import datetime
import json
import logging

from functions.azure_db import get_random_nameList
from functions.azure_search import search_sample_hybrid, search_sample_index, search_sample_semantic, search_sample_vector
from functions.openAI import chat_sample

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
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
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
search_map = {
    "vector": search_sample_vector,
    "index": search_sample_index,
    "hybrid": search_sample_hybrid,
    "semantic": search_sample_semantic
}
@app.route(route="maps_test", auth_level=func.AuthLevel.FUNCTION)
def search_test_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            response={}
            temp = get_random_nameList(int(data["sample_number"]))
            # タイトルを保存するリスト
            titles = [claim["title"] for claim in temp] 
            combined_claims = "\n\n".join([f"{claim['text']}" for claim in temp])
            text=""
            if data["try_times"] == "0":
                text=combined_claims
            else:
                # まとめたテキストを新しい請求項の生成用に加工
                prompt = (
                    "以下に複数の請求項を示します。それらを基にして、新しい創造的な請求項を1つ作成してください。:\n\n"
                    f"{combined_claims}\n\n"
                    "これらを基にした新しい請求項を以下に記述してください。:"
                )
                text = chat_sample(prompt,data["model"])
            response["titles"]=titles
            response["search_text"]=temp
            response["create_text"]=text
            result_titles=[]
            # 検索の選択
            for result in search_map[data["search"]](text,int(data["top"])):
                result_titles.append(result.get("title"))
            response["result_titles"]=result_titles
            #一致しているtitleをカウント
            response["match"]=sum(1 for title in result_titles if title in titles)
            return func.HttpResponse(response)
        except json.JSONDecodeError:
            return func.HttpResponse({'error': 'Invalid JSON'}, status=400)

    return func.HttpResponse({'error': 'Invalid method'}, status=405)