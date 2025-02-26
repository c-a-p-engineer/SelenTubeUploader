# SelenTubeUploader

[![Build Status](https://img.shields.io/github/actions/workflow/status/your_username/SelenTubeUploader/build.yml?branch=master&label=Build%20Status)](https://github.com/your_username/SelenTubeUploader/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/your_username/SelenTubeUploader?style=social)](https://github.com/your_username/SelenTubeUploader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/your_username/SelenTubeUploader?style=social)](https://github.com/your_username/SelenTubeUploader/network)

SelenTubeUploader は、Python と Selenium、webdriver-manager を利用して YouTube Studio 上での動画アップロードを自動化するツールです。  
このツールは、JSON 形式の設定ファイルから動画のパラメータ（動画ファイルパス、サムネイル、タイトル、説明、投稿日時）を読み込み、複数の動画を順次アップロードします。

また、Chrome のユーザープロファイルを利用することで、既存のログイン状態を保持したまま自動化処理を実行できます。  
※ **--user-data-dir** と **--profile-directory** の値は [chrome://version](chrome://version) で確認できます。

---

## 特徴

- **自動化アップロード**  
  Selenium により YouTube Studio の操作を自動化し、動画ファイルのアップロード、タイトル・説明の入力、サムネイル設定、投稿日時の設定、スケジュール設定まで一括で処理します。

- **複数動画対応**  
  JSON 設定ファイルに複数の動画情報を記述でき、設定順にアップロードを実施します。

- **ユーザープロファイル指定**  
  コマンドライン引数 `--user-data-dir` および `--profile-directory` により、Chrome の既存ユーザープロファイルを利用できます。

- **デバッグログの切り替え**  
  `--debug` オプションを指定すると詳細なデバッグログが出力され、指定しない場合は INFO レベルのログに切り替えられます。

- **UI 固有の対策**  
  - タイトル入力は ActionChains を使用して全選択・削除後に入力。
  - 説明入力は TrustedTypes ポリシーを利用して innerHTML を更新し、BMP 外文字エラーを回避。
  - 「いいえ、子ども向けではありません」のラジオボタンをクリックして設定。
  - 日付・時刻入力は、直接テキスト入力フィールドに値を入力し、Enter キーで確定（Chrom レコーダーの記録を参考）。
  - 公開/スケジュール設定完了ボタンは、特定の ID 要素（例: `second-container-expand-button`）や XPath を利用してクリックします。

---

## 要求環境

- **Python 3.11**（推奨）
- **Google Chrome**（最新版推奨）
- **ChromeDriver**（webdriver-manager により自動管理）
- 必要な Python パッケージ:
  - `selenium`
  - `webdriver-manager`
  - その他（例: `argparse`, `logging` 等は標準ライブラリ）

---

## インストール

まず、必要なパッケージをインストールしてください。

```bash
pip install selenium webdriver-manager
```

---

## 使い方

### A. SelenTubeUploader の使用方法

#### 1. 設定ファイルの準備

アップロードする動画の情報を記述した JSON ファイル（例: `config.json` または `sample.json`）を用意してください。  
例:

```json
{
  "videos": [
    {
      "video_path": "C:\\path\\to\\video1.mp4",
      "thumbnail": "C:\\path\\to\\thumbnail1.jpg",
      "title": "動画タイトル1",
      "description": "1行目\n2行目\n3行目",
      "post_time": "2030-12-31 12:34"
    }
  ]
}
```

#### 2. ユーザープロファイルの指定

Chrome のユーザーデータディレクトリとプロファイルディレクトリを指定することで、既存のログイン状態を利用できます。  
これらの値は [chrome://version](chrome://version) で確認可能です。  
例:
- **user-data-dir**: `C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data`
- **profile-directory**: `Profile 1`

#### 3. コマンド実行例

以下は、各オプションを指定して SelenTubeUploader を実行するサンプルです。

```bash
python upload_video.py --config sample.json --user-data-dir "C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data" --profile-directory "Profile 1" --debug
```

**オプション説明:**

- `--config`  
  設定ファイルのパスを指定します（デフォルトは `config.json`）。

- `--user-data-dir`  
  Chrome のユーザーデータディレクトリのパスを指定します。  
  ※ この値は [chrome://version](chrome://version) で確認してください。

- `--profile-directory`  
  Chrome のプロファイルディレクトリの名称を指定します。  
  ※ この値も [chrome://version](chrome://version) で確認可能です。

- `--debug`  
  詳細なデバッグログを出力します。指定しない場合は INFO レベルのログになります。

#### 4. YouTube Studio にログイン

指定したユーザープロファイルで YouTube Studio にログイン済みであることを確認してください。  
スクリプト実行中にログイン確認のプロンプトが表示されます。

#### 5. スクリプト実行

上記のコマンド実行例のようにスクリプトを実行すると、設定ファイルに基づいて各動画のアップロードが自動的に開始されます。  
各ステップでログが出力され、次の動画アップロードのタイミングでユーザーの操作を促します。

---

### B. 動画情報 JSON 生成ツール (create_video_json.py) の使用方法

このツールは、指定した親ディレクトリ内の各サブディレクトリから動画情報（動画ファイル、サムネイル、description.txt からタイトルと説明）を抽出し、JSON ファイルにまとめます。

#### 機能

- **出力先ファイルの指定**  
  オプション `--output_file` により、生成した JSON の出力先ファイルを指定できます。  
  指定がなければ `output.json` として実行ディレクトリに保存されます。

- **処理件数の制限**  
  オプション `--limit` により、処理するサブディレクトリの件数を制限可能です。  
  0（デフォルト）の場合は全件を処理します。

- **グループ件数の指定**  
  オプション `--group_count` を追加し、同一の日付で処理する件数を指定できます（デフォルトは2件）。

- **日付のインクリメント**  
  各サブディレクトリの動画情報を処理する際、カウンター `processed_in_group` を利用して、指定件数（group_count）に達したら、`base_date` を `--day_increment` の日数分インクリメントし、カウンターをリセットします。

#### コマンド実行例

以下の例では、親ディレクトリ `./videos_folder` 内の先頭6件の動画情報を、開始日時を `2025-02-28 15:30` とし、出力先を `result.json` に設定して JSON ファイルを生成します。

```bash
python create_video_json.py --base_dir "./videos_folder" --start_date "2025-02-28 15:30" --day_increment 1 --group_count 3 --limit 6 --output_file "result.json"
```

**オプション説明:**

- `--base_dir`  
  動画情報が格納されている親ディレクトリのパスを指定します（デフォルトはカレントディレクトリ）。

- `--start_date`  
  開始日時を `"YYYY-MM-DD HH:MM"` 形式で指定します。指定がない場合は実行日の翌日同時刻が使用されます。

- `--day_increment`  
  グループ毎に加算する日数を指定します（デフォルトは1）。

- `--group_count`  
  同一日付で処理するサブディレクトリ件数を指定します（デフォルトは2件）。

- `--limit`  
  処理するサブディレクトリの件数を制限します。0 の場合は全件処理します（デフォルトは 0）。

- `--output_file`  
  生成した JSON を出力するファイルパスを指定します（デフォルトは `output.json`）。

---

## 注意事項

- **UI の変化**  
  YouTube Studio の UI は頻繁に更新されるため、各要素の XPath や CSS セレクタは最新の DOM 構造に合わせて調整してください。

- **ChromeDriver や Chrome の仕様変更**  
  バージョン変更等でエラーが発生する場合、webdriver-manager のアップデートや Selenium の設定見直しを行ってください。

- **TrustedTypes 対策**  
  説明フィールドの更新には TrustedTypes ポリシーを利用して innerHTML を更新しています。Chrome のバージョンによっては動作に注意が必要です。

- **デバッグログの切り替え**  
  `--debug` オプションにより詳細ログが出力されます。不要な場合はオプションを省略してください。

---

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されています。詳細は LICENSE ファイルをご確認ください。
