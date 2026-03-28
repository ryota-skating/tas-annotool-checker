#!/bin/bash

# Tas-Annotool-Checker: HTMLレポート生成・公開スクリプト
# 既存のJSONレポートからHTMLレポートを生成してGitHubに公開します

set -e  # エラーが発生したら即座に終了

echo "=========================================="
echo "HTMLレポート生成・公開スクリプト"
echo "=========================================="
echo ""

# 1. HTMLレポート生成
echo "[1/2] HTMLレポートを生成中..."
uv run python make_report.py
if [ $? -eq 0 ]; then
    echo "✓ HTMLレポート生成完了"
else
    echo "✗ HTMLレポート生成失敗"
    exit 1
fi
echo ""

# 2. GitHubに公開
echo "[2/2] GitHubに公開中..."

# Gitの状態を確認
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✗ Gitリポジトリが初期化されていません"
    exit 1
fi

# 変更をステージング
git add output/report-html/*.html
git add README.md .gitignore make_report.py update_and_publish.sh publish_reports.sh

# 変更があるか確認
if git diff --cached --quiet; then
    echo "変更がありません。公開をスキップします。"
else
    # コミット
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Update HTML reports - $TIMESTAMP

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    # プッシュ
    if git push origin main; then
        echo "✓ GitHubへの公開完了"
        echo ""
        echo "=========================================="
        echo "レポートが公開されました！"
        echo "URL: https://ryota-skating.github.io/tas-annotool-checker/output/report-html/"
        echo "=========================================="
    else
        echo "✗ GitHubへのプッシュに失敗しました"
        echo "  認証情報を確認してください"
        exit 1
    fi
fi

echo ""
echo "すべての処理が完了しました！"
