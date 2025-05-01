import logging
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-03-15-preview",
    azure_endpoint="https://ateamopenai.openai.azure.com/",
    api_key="b7e21555bf544a038f1b26c9d9b0fb9e",
)
# シンプルなgpt利用
def chat_sample(message: str,model:str="gpt-35-turbo") -> str:
    """
    シンプルなgpt利用
    """
    logging.info(f'mago log.message={message}.model={model}')
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
