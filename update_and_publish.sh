#!/bin/bash

# Tas-Annotool-Checker: 自動更新・公開スクリプト
# 最新のアノテーションデータをクロールし、HTMLレポートを生成してGitHubに公開します

set -e  # エラーが発生したら即座に終了

echo "=========================================="
echo "Tas-Annotool-Checker 自動更新スクリプト"
echo "=========================================="
echo ""

# 1. クロール
echo "[1/5] データをクロール中..."
uv run python crawl.py
if [ $? -eq 0 ]; then
    echo "✓ クロール完了"
else
    echo "✗ クロール失敗"
    exit 1
fi
echo ""

# 2. JSONに変換
echo "[2/5] HTMLをJSONに変換中..."
uv run python html_to_json.py
if [ $? -eq 0 ]; then
    echo "✓ JSON変換完了"
else
    echo "✗ JSON変換失敗"
    exit 1
fi
echo ""

# 3. ミス検出
echo "[3/5] ミスを検出中..."
uv run python detect.py
if [ $? -eq 0 ]; then
    echo "✓ ミス検出完了"
else
    echo "✗ ミス検出失敗"
    exit 1
fi
echo ""

# 4. HTMLレポート生成
echo "[4/5] HTMLレポートを生成中..."
uv run python make_report.py
if [ $? -eq 0 ]; then
    echo "✓ HTMLレポート生成完了"
else
    echo "✗ HTMLレポート生成失敗"
    exit 1
fi
echo ""

# 5. GitHubに公開
echo "[5/5] GitHubに公開中..."

# Gitの状態を確認
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✗ Gitリポジトリが初期化されていません"
    echo "  以下のコマンドを実行してください："
    echo "  git remote add origin https://github.com/ryota-skating/tas-annotool-checker.git"
    exit 1
fi

# 変更があるか確認
if git diff --quiet && git diff --cached --quiet; then
    echo "変更がありません。公開をスキップします。"
else
    # 変更をステージング
    git add output/report-html/*.html

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
        echo "  リモートリポジトリが設定されているか確認してください："
        echo "  git remote -v"
        exit 1
    fi
fi

echo ""
echo "すべての処理が完了しました！"
