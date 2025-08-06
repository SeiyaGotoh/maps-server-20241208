from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchFieldDataType, SearchField,
    VectorSearch, HnswAlgorithmConfiguration,
    SearchIndexerDataSourceConnection, SearchIndexerSkillset, SearchIndexer,
    AzureOpenAIEmbeddingSkill, SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset
)

service_name = "maps"
endpoint = f"https://{service_name}.search.windows.net/"
admin_key = "EKz0IbLfgliPcYLCYcQVLiukrwthFaIcNe4byooh1mAzSeAuV0Vp"
cred       = DefaultAzureCredential()

# 1. データソース（Blob）
ds = SearchIndexerDataSourceConnection(
    name="docs-src",
    type="azureblob",
    connection_string="DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net",
    container={"name": "json-3000"}
)

# 2. Skillset ─ チャンク + Embedding を宣言
skillset = SearchIndexerSkillset(
    name="chunk-embed",
    skills=[
        SplitSkill(
            name="text_split",
            description="文章を2000文字にチャンク分割",
            context="/document/content",
            default_language_code="ja",
            text_split_mode="pages",         # sentences や pages が指定可
            maximum_page_length=2000,
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")]
        ),
        AzureOpenAIEmbeddingSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
            outputs=[OutputFieldMappingEntry(name="embedding", target_name="vector")],
            resource_url="https://ateamopenai.openai.azure.com",
            deployment_name="text-embedding-ada-002",
            model_name="text-embedding-ada-002",
            dimensions=1536
        )
    ]
)

# 3. インデックス（vector フィールドだけ定義）
index = SearchIndex(
    name="docs-vector",
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(
            name="vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="vec-prof" 
        )
    ],
    vector_search=VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="vec-prof",
                kind="hnsw",
                parameters={"m":4, "efConstruction":400, "efSearch":500, "metric":"cosine"}
            )
    ]
    )
)

# 4. インデクサー（定期実行可）
indexer = SearchIndexer(
    name="docs-indexer",
    data_source_name=ds.name,
    target_index_name=index.name,
    skillset_name=skillset.name
)

# --- 作成 ---
idx_cli  = SearchIndexClient(endpoint, AzureKeyCredential(admin_key))
idx_cli.create_or_update_index(index)
ix_cli   = SearchIndexerClient(endpoint, AzureKeyCredential(admin_key))
ix_cli.create_or_update_data_source_connection(ds)
ix_cli.create_or_update_skillset(skillset)
ix_cli.create_or_update_indexer(indexer)
ix_cli.run_indexer(indexer.name)   # 初回フル取り込み
