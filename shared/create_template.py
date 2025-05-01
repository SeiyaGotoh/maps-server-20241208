# shared/create_template.py

# テンプレート作成
import json
from shared.azure_db import get_random_nameList_v2
from shared.azure_search import search_sample_semantic
from shared.open_ai import chat_sample


def create_template_1_1_mix():
    """
    別々の２つ
    """
    with open('temp_data.json', 'r', encoding='utf-8') as f:
        loaded_env = json.load(f)
    start = 0
    end = 10
    template_1_1_mix=[]
    for i in range(start, end*2,2):
        prompt = (f"""
次の2つのテキストを使って、1つの似た仕組みの文章を作成してください。

【要件】
- 2つのテキストに登場する**単語**または、**類似語**を必ず使ってください。
- 最初のテキストは**前半部分**のみで、2番目のテキストは**後半部分**のみで参照してください。
- 長さは、合わせて１つ分のテキストの長さ程度にしてください。
- 前半と後半でつながりのない文章で問題ありません。

【テキスト1】
{loaded_env[i]["text"]}

【テキスト2】
{loaded_env[i+1]["text"]}
"""
            )
        template_1_1_mix.append({"title":[loaded_env[i]["title"],loaded_env[i+1]["title"]],"text":chat_sample(prompt)})
    
    with open('template_1_1_mix.json', 'w', encoding='utf-8') as f:
        json.dump(template_1_1_mix, f, ensure_ascii=False, indent=2)



def create_template_3_1_mix():
    """
    似た3つ別の1つ
    """
    with open('temp_data.json', 'r', encoding='utf-8') as f:
        loaded_env_similar = json.load(f)
        
    with open('temp_data_similar.json', 'r', encoding='utf-8') as f:
        loaded_env = json.load(f)
    start = 0
    end = 10
    index=0
    template_3_1_mix=[]
    for i in range(start, end*4,4):
        prompt = (f"""
次の4つのテキストを使って、1つの似た仕組みの文章を作成してください。

【要件】
- 4つのテキストに登場する**単語**または、**類似語**を必ず使ってください。
- 各テキストを全体の4分の1ごとで、一つずつのみで参照してください。
- 長さは、合わせて１つ分のテキストの長さ程度にしてください。
- 4分の1ごとでつながりのない文章で問題ありません。

【テキスト1】
{loaded_env_similar[i]["text"]}

【テキスト2】
{loaded_env_similar[i+1]["text"]}

【テキスト3】
{loaded_env_similar[i+2]["text"]}

【テキスト4】
{loaded_env[index+30]["text"]}
"""
            )
        template_3_1_mix.append({"title":[loaded_env_similar[i]["title"],loaded_env_similar[i+1]["title"],loaded_env_similar[i+2]["title"],loaded_env[index+30]["title"]],"text":chat_sample(prompt)})
        index += 1
    with open('template_3_1_mix.json', 'w', encoding='utf-8') as f:
        json.dump(template_3_1_mix, f, ensure_ascii=False, indent=2)


def create_template_4_0_mix():
    """
    似た4つ
    """
    with open('temp_data_similar.json', 'r', encoding='utf-8') as f:
        loaded_env = json.load(f)
    start = 0
    end = 10
    template_4_0_mix=[]
    for i in range(start, end*4,4):
        prompt = (f"""
次の4つのテキストを使って、1つの似た仕組みの文章を作成してください。

【要件】
- 4つのテキストに登場する**単語**または、**類似語**を必ず使ってください。
- 各テキストを全体の4分の1ごとで、一つずつのみで参照してください。
- 長さは、合わせて１つ分のテキストの長さ程度にしてください。
- 4分の1ごとでつながりのない文章で問題ありません。

【テキスト1】
{loaded_env[i]["text"]}

【テキスト2】
{loaded_env[i+1]["text"]}

【テキスト3】
{loaded_env[i+2]["text"]}

【テキスト4】
{loaded_env[i+3]["text"]}
"""
            )
        template_4_0_mix.append({"title":[loaded_env[i]["title"],loaded_env[i+1]["title"],loaded_env[i+2]["title"],loaded_env[i+3]["title"]],"text":chat_sample(prompt)})
    
    with open('template_4_0_mix.json', 'w', encoding='utf-8') as f:
        json.dump(template_4_0_mix, f, ensure_ascii=False, indent=2)


def create_template_similar():
    """
    似た値の取得
    """
    with open('temp_data.json', 'r', encoding='utf-8') as f:
        loaded_env = json.load(f)
    start = 30
    end = 40
    temp_data_similar=[]
    for i in range(start, end):
        for result in search_sample_semantic(loaded_env[i]["text"],4,"vector-json-3000-summary-referen"):
            temp_data_similar.append({"title":result.get("title"),"text":result.get("chunk")})
    # 保存（書き込み）
    with open('temp_data_similar.json', 'w', encoding='utf-8') as f:
        json.dump(temp_data_similar, f, ensure_ascii=False, indent=2)