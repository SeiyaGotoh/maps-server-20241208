from openai import AzureOpenAI

### AzureOpenAI クライアントの初期化と利用 ############################
# ここでは、Azure OpenAI サービスに接続するためのクライアントを生成しています。
# APIバージョンやエンドポイント、APIキーを指定しているため、これ以降の呼び出しはこの設定に基づいて行われます。
    

client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)

# 純粋なOpenAIの通信
def chat_sample(message: str,model:str="gpt-35-turbo") -> str:
    """
    純粋なOpenAIの通信

    Args:
            message (str): 送信するメッセージ
            model (str="gpt-35-turbo"): 計算に使用するモデル

    Returns:
            str: 出力結果
    """
    completion = client.chat.completions.create(
        model = model, 
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    ) 
    return(completion.choices[0].message.content)


# ベクトル化の通信
def get_embedding(text: str, engine: str="text-embedding-ada-002"):
    """
    ベクトル化の通信

    Args:
            message (str): 送信するメッセージ
            engine (str="text-embedding-ada-002"): 計算に使用するモデル

    Returns:
            str: 出力結果
    """
    # OpenAI埋め込みモデルを使用してテキストをベクトル化
    response = client.embeddings.create(
        input=text,
        model=engine  # 埋め込みモデルの名前
    )
    return response.data[0].embedding

