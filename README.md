# SelenTubeUploader

SelenTubeUploader は、Python と Selenium、webdriver-manager を利用して YouTube Studio 上での動画アップロードを自動化するツールです。  
このツールは、JSON 形式の設定ファイルから動画のパラメータ（動画ファイルパス、サムネイル、タイトル、説明、投稿日時）を読み込み、複数の動画を順次アップロードします。

また、Chrome のユーザープロファイルを利用することで、既存のログイン状態を保持したまま自動化処理を実行できます。  
※ **--user-data-dir** と **--profile-directory** の値は、Chrome の [chrome://version](chrome://version) で確認できます。

---

## 特徴

- **自動化アップロード**  
  YouTube Studio の操作を Selenium により自動化し、動画ファイルのアップロード、タイトル・説明の入力、サムネイル設定、投稿日時の設定、スケジュール設定まで一括で処理します。

- **複数動画対応**  
  JSON 設定ファイルに複数の動画情報を記述可能。設定した順にアップロードを実施します。

- **ユーザープロファイル指定**  
  コマンドライン引数 `--user-data-dir` および `--profile-directory` により、Chrome の既存プロファイルを利用し、ログイン状態を維持できます。

- **デバッグログ出力**  
  各処理ステップのログを出力し、エラー発生時も詳細情報を確認可能です。

- **UI 固有の対策**  
  - タイトル入力は ActionChains を利用して全選択・削除後に入力。
  - 説明入力は TrustedTypes ポリシーを用いて innerHTML を更新し、BMP 外文字のエラーを回避。
  - 「いいえ、子ども向けではありません」のラジオボタンをクリック。
  - 日付・時刻は直接テキスト入力フィールドに値を入力し、Enter キーで確定。（Chrom レコーダーの記録を参考に、オフセットクリックなども実装可能）

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

### 1. 設定ファイルの準備

リポジトリ内の `config.json`（または `sample.json`）に、アップロードする各動画の情報を記述します。  
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

### 2. ユーザープロファイルの指定

Chrome のユーザーデータディレクトリおよびプロファイルディレクトリを指定することで、既存のログイン状態を利用できます。  
これらの値は [chrome://version](chrome://version) で確認可能です。  
例:
- **user-data-dir**: `C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data`
- **profile-directory**: `Profile 1`

### 3. コマンド実行例

以下は、各オプションを指定してスクリプトを実行するサンプルです。

```bash
python upload_video.py --config sample.json --user-data-dir "C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data" --profile-directory "Profile 1"
```

#### オプション説明

- `--config`  
  設定ファイルのパスを指定します。デフォルトは `config.json` です。

- `--user-data-dir`  
  Chrome のユーザーデータディレクトリのパスを指定します。  
  （例: `C:\Users\xxxxx\AppData\Local\Google\Chrome\User Data`）  
  この値は [chrome://version](chrome://version) で確認してください。

- `--profile-directory`  
  Chrome のプロファイルディレクトリの名称を指定します。  
  （例: `Profile 1`）  
  この値も [chrome://version](chrome://version) で確認可能です。

### 4. YouTube Studio にログイン

指定したユーザープロファイルで YouTube Studio にログイン済みであることを確認してください。  
スクリプト実行中にログイン確認のプロンプトが表示されます。

### 5. スクリプト実行

上記のコマンド実行例のように、スクリプトを実行すると、設定ファイルに基づいて各動画のアップロードが自動的に開始されます。  
アップロード完了後、各ステップのログが出力され、次の動画アップロードなどのタイミングでユーザーの操作を促します。

---

## 注意事項

- **UI の変化**  
  YouTube Studio の UI は頻繁に更新されるため、各要素の XPath や CSS セレクタは最新の DOM 構造に合わせて調整してください。

- **ChromeDriver や Chrome の仕様変更**  
  バージョン変更等でエラーが発生する場合、webdriver-manager のアップデートや Selenium の設定見直しを行ってください。

- **TrustedTypes 対策**  
  説明フィールドの更新には TrustedTypes ポリシーを利用しています。Chrome のバージョンによっては挙動に注意が必要です。

---

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されています。詳細は LICENSE ファイルをご確認ください。
