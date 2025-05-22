from azure.data.tables import TableClient
import csv
import os

# 接続文字列（検証用）
connection_string = "DefaultEndpointsProtocol=https;AccountName=maps5370605259;AccountKey=jA9t0HLlnYSLmPbSf6RkEg8emdkjhHO9JfkL5XT8HNX8H4kfq+WCHO/v0fwXgN4b083JhPDP77Fk+AStBofZPg==;EndpointSuffix=core.windows.net"

# Table Storageからエラー一覧を取得
table_client = TableClient.from_connection_string(connection_string, table_name="ErrorLogs")
errors = table_client.query_entities("PartitionKey eq 'Errors'")

# CSVに出力
with open("error_list.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["FilePath", "Error", "Timestamp"])
    for error in errors:
        writer.writerow([error['FilePath'], error['Error'], error['Timestamp']])
print("Error list saved to error_list.csv")
