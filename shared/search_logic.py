# shared/search_logic.py


import logging
import json

from MapsDemo import search_sample_vector
from shared.azure_db import get_random_nameList, get_random_nameList_v2
from shared.azure_search import search_sample_hybrid, search_sample_index, search_sample_semantic
from shared.open_ai import chat_sample
from opencensus.ext.azure.log_exporter import AzureLogHandler

# 指定のテキストを使用して検索
# 実装途中
def search_logic(prop: dict[str, any]):

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
        # logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=90400575-c365-4f36-b271-dbd91fc5fc37;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/;ApplicationId=071ce0b4-9e9c-45c0-b6c2-13240885c6fd"))
        logging.info(f'mago log.loop={prop["loop"]}.top={prop["top"]}')

        with open(prop["json"], 'r', encoding='utf-8') as f:
            loaded_env = json.load(f)
        for i in range(min(prop["loop"], len(loaded_env))):
            titles =loaded_env[i]["title"]
            create_text=loaded_env[i]["text"]
            response_data["titles"].append(titles)
            response_data["create_text"].append(create_text)
            result_titles=[]
            match_count=[]
            matchlist=[]
            # 検索の選択
            for result in search_map[prop["search"]](create_text,prop["top"],prop["index_name"]):
                result_titles.append(result.get("title"))
                matchlist.append(len(set(titles) & set(result_titles)))
                match_count.append(sum(1 for title in result_titles if title in titles))
            response_data["result_titles"].append(result_titles)
            #一致しているtitleをカウント
            match=sum(1 for title in result_titles if title in titles)
            logging.info(f'mago log.match={match}')
            response_data["match"].append(match)

            print(i)
            print(match_count)

            # カスタムディメンション付きでログ送信
            logger.info("search_result_7", extra={
                "custom_dimensions": {
                    "top": str(prop["top"]),          # 検索数（横軸）
                    "matchList": str(matchlist),         # 一致数（縦軸)
                    "matchCount": str(match_count),      # 一致数（縦軸)重複あり
                    "model": prop["model"],          # モデル
                    "search": prop["search"],         # 検索モデル
                    "count": str(i),
                    "name": prop["name"], 
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