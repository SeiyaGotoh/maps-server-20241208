# from openai import AzureOpenAI

# client = AzureOpenAI(
#     api_version="2023-03-15-preview",
#     azure_endpoint="https://ateamopenai.openai.azure.com/",
#     api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
# )


# def chat_sample(message: str,model:str="gpt-35-turbo") -> str:
#     completion = client.chat.completions.create(
#         model = model, 
#         messages=[
#             {
#                 "role": "user",
#                 "content": message,
#             },
#         ],
#     ) 
#     return(completion.choices[0].message.content)

# def get_embedding(text: str, engine="text-embedding-ada-002"):
#     # OpenAI埋め込みモデルを使用してテキストをベクトル化
#     response = client.embeddings.create(
#         input=text,
#         model=engine  # 埋め込みモデルの名前
#     )
#     return response.data[0].embedding

