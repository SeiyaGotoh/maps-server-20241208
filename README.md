## ブランチ管理
- develop を正規ブランチとして運用
- 各自のブランチは、'woek_for_{名前}'で設定
- main を develop からmergeして、デプロイ

## ローカル起動方法
1. インストール
- 'npm init -y  # 既定の設定でpackage.jsonを作成'
- 'npm install -g azure-functions-core-tools@4 --unsafe-perm true'
- 'python -m venv venv'
- 'venv/scripts/activate'
- 'pyenv local 3.11.5'
1. 起動
- 'func: host start'