# shared/old_search_logic.py


import logging

from MapsDemo import search_sample_vector
from shared.azure_db import get_random_nameList, get_random_nameList_v2
from shared.azure_search import search_sample_hybrid, search_sample_index, search_sample_semantic
from shared.open_ai import chat_sample
from opencensus.ext.azure.log_exporter import AzureLogHandler

def old_search_logic(prop: dict[str, any]):

    response_data={
        "titles": [],
        "search_text": [],
        "create_text": [],
        "match": [],
        "result_titles":[],
        "result_page":[]
    }
    try:
        logger = logging.getLogger("my_logger")
        logger.setLevel(logging.INFO)
        logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=90400575-c365-4f36-b271-dbd91fc5fc37;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/;ApplicationId=071ce0b4-9e9c-45c0-b6c2-13240885c6fd"))
        logging.info(f'mago log.loop={prop["loop"]}.top={prop["top"]}')
        for i in range(prop["loop"]):
            temp=[]
            if(prop["store"]!="azureml-blobstore-7e664d9f-7a26-47bc-81b8-b1545cc9cedd"):
                temp = get_random_nameList_v2(prop["sample_number"],prop["store"])
            else:
                temp = get_random_nameList(prop["sample_number"])
            if not temp:
                logging.info(f'[Skip] temp')
                continue
            titles = [claim["title"] for claim in temp] 
            combined_claims = "\n\n".join([f"{claim['text']}" for claim in temp])[:8000]
            
            logging.info(f'mago log.temp={temp}.titles={titles}.combined_claims={combined_claims}')
            # まとめたテキストを新しい請求項の生成用に加工
            prompt = (
                "以下に複数の仕組みを示します。それらを基にして、似ている仕組みを1つ作成してください。compositionがある場合はcomposition内のデータを使用して下さい:\n\n"
                f"{combined_claims}\n\n"
                "これらを基に、類似している単語を使用して似ている仕組みを以下に記述してください。:"
            )
            if(prop["sample_number"]!=0):
                text = chat_sample(prompt,prop["model"])
            else:
                text = [claim["text"] for claim in temp] 
            text = text[:8000]  # 長すぎる入力をカット
            logging.info(f'mago log.text={text}.combined_claims={combined_claims}.sample_number!=0={prop["sample_number"]!=0}')
            response_data["titles"].append(titles)
            response_data["search_text"].append(temp)
            response_data["create_text"].append(text)
            result_titles=[]
            match_count=[]
            matchlist=[]
            # 検索の選択
            for result in search_map[prop["search"]](text,prop["top"],prop["index_name"]):
                result_titles.append(result.get("title"))
                matchlist.append(len(set(titles) & set(result_titles)))
                match_count.append(sum(1 for title in result_titles if title in titles))
            response_data["result_titles"].append(result_titles)
            #一致しているtitleをカウント
            match=sum(1 for title in result_titles if title in titles)
            logging.info(f'mago log.match={match}')
            response_data["match"].append(match)

            # カスタムディメンション付きでログ送信
            logger.info("search_result_7", extra={
                "custom_dimensions": {
                    "sampleNumber": str(prop["sample_number"]), # 元データ数
                    "top": str(prop["top"]),          # 検索数（横軸）
                    "matchList": str(matchlist),         # 一致数（縦軸)
                    "matchCount": str(match_count),      # 一致数（縦軸)重複あり
                    "model": prop["model"],          # モデル
                    "search": prop["search"],         # 検索モデル
                    "count": str(i),
                    "name": prop["name"], 
                    "store":prop["store"], 
                }
            })
            return response_data
    except Exception as e:
        logging.exception(f"サーチ処理中にエラーが発生しました: {e}")

        

search_map = {
    "vector": search_sample_vector,
    "index": search_sample_index,
    "hybrid": search_sample_hybrid,
    "semantic": search_sample_semantic
}