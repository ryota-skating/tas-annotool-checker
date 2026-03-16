# Tas-Annotool-Checker

Tas-Annotoolのミスを検出するツール（ほぼChatGPT作）。

## 検出の方針

* あるアノテータ(検出対象)の結果を、同じ動画にアノテーションした他のアノテータたち(比較対象)の結果と比較して、矛盾を検出する
* 目的はアノテータ間の比較ではなくあくまでミスの検出であるため、誤っている可能性の高い箇所を最低限列挙する


## 検出できるもの

アノテータの見間違えや操作ミスとして、次の項目を検出する。

* **ラベルミス(confusable_label)**: 間違えやすいラベルの付け間違え。例えば、RFO Rocker TurnとRBO Rocker Turn、Cross ForwardとCrossover Forward。
* **範囲過剰(long_segment_overflow)**: 極端に長い範囲のラベル。アノテーション操作ミスなどで、意図せず長い範囲になっているもの。
* **複数に跨ったラベル(long_segment_multi_label)**: 長い範囲のラベルで、本来複数のラベルに分かれるかもしれないもの。アノテーション操作ミスの検出。

なお、`config.json`で細かい内容を設定できる。
* `groups`: 同じ動画をアノテーションしているアノテータのグループ。
* `confusable_groups`: 「ラベルミス(confusable_label)」検出用。間違えやすいラベルの定義。同じ配列の中に入れたラベル同士が間違えやすいラベルとする。
* `long_segment_threshold`: 「範囲過剰(long_segment_overflow)」検出用。何フレーム以上を過剰と判定するかの閾値。


## 実行方法
`accounts.csv`と`config.json`を用意して、次の順でスクリプトを実行
1. crawl.py でクロール
2. html_to_json.py でJSONに変換
3. detect.py でJSONレポート作成
4. make_report.py でHTMLレポート作成

## 出力結果

### ディレクトリ構成

* `output/html/`: Tas-Annotoolから取得した生HTML
* `output/json/`: HMLTから必要事項だけ抽出したJSON
* `output/report/`: 検出したミスのJSONレポート
* `output/report-html/`: 人間が読みやすいようJSONレポートをHTMLにしたもの

### HTMLレポートの見方

**オンラインレポート:** https://ryota-skating.github.io/tas-annotool-checker/

検出対象のアノテータごとに1ファイルのレポートがある。
各ファイルの中で、動画ごとのミス検出結果が記載されている。

記載の例は次のとおり。

**ラベルミス:**
```
frame 2641-2690 :
  - Cross Forward は Crossover Forward の可能性
```
上記例は、フレーム2641-2690でCross Forwardとラベル付けしているが、実際はCrossover Forwardではないかという疑いを示している。

**範囲過剰:**
```
frame 3223-3331 :
  - Hop の範囲が長すぎる可能性
```
上記例は、フレーム3223-3331のHopが長く、範囲が過剰ではないかという疑いを示している。

**複数に跨ったラベル:**
```
frame 4418-4476 :
  - Hop は複数のラベルに分かれる可能性：
    - Toe Step (4408-4445)
    - Hop (4462-4469)
```
上記例は、フレーム4418-4476のHopの中に、Toe StepとHopの2つのラベルが付けられるのではないかという疑いを示している。


