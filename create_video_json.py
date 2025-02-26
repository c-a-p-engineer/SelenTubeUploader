r"""
説明
- 出力先ファイルの指定
    - オプション --output_file で出力先ファイルを指定できます。指定がなければ output.json として実行ディレクトリに保存されます。
- 処理件数の制限
    - オプション --limit により、処理するディレクトリの件数を制限可能です。0（デフォルト）の場合は全件を処理します。

- グループ件数のオプション化
    - オプション --group_count を追加し、同一の日付で処理する件数を指定可能にしています（デフォルトは2件）。
- 日付のインクリメント
    - 各ディレクトリの動画情報を処理する際、カウンター processed_in_group を使って、指定件数（group_limit）に達したら、base_date を --day_increment の日数分インクリメントし、カウンターをリセットします。

- 実行例
    以下の例では、親ディレクトリ ./videos_folder 内の先頭6件を、開始日時を 2025-02-28 15:30 とし、出力先を result.json に設定して JSON を生成します。
    ```bash
    python create_video_json.py --base_dir "./videos_folder" --start_date "2025-02-28 15:30" --day_increment 1 --group_count 3 --limit 6 --output_file "result.json"
    ```
"""

import os
import json
import argparse
from datetime import datetime, timedelta

def parse_description_file(desc_path):
    """
    description.txt を読み込み、
    2行目をタイトル、3行目以降を説明文として返す。
    行数が足りない場合は適宜空文字を返します。
    """
    with open(desc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    title = lines[1].strip() if len(lines) >= 2 else ""
    description = "".join(lines[2:]).strip() if len(lines) >= 3 else ""
    return title, description

def find_mp4_file(directory_path):
    """
    指定ディレクトリ内で拡張子 .mp4 のファイルを探し、そのパスを返します。
    存在しない場合は None を返します。
    """
    for entry in os.listdir(directory_path):
        if entry.lower().endswith(".mp4"):
            return os.path.abspath(os.path.join(directory_path, entry))
    return None

def process_directory(directory_path, current_post_time):
    """
    ディレクトリ内の必要ファイル（thumbnail.jpg, *.mp4, description.txt）から
    動画情報の辞書を生成します。
    """
    thumb_path = os.path.join(directory_path, "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        raise FileNotFoundError(f"thumbnail.jpg が {directory_path} に見つかりません")
    thumb_path = os.path.abspath(thumb_path)
    
    video_path = find_mp4_file(directory_path)
    if video_path is None:
        raise FileNotFoundError(f"拡張子 .mp4 の動画ファイルが {directory_path} に見つかりません")
    
    desc_path = os.path.join(directory_path, "description.txt")
    if not os.path.exists(desc_path):
        raise FileNotFoundError(f"description.txt が {directory_path} に見つかりません")
    title, description = parse_description_file(desc_path)
    
    video_info = {
        "video_path": video_path,
        "thumbnail": thumb_path,
        "title": title,
        "description": description,
        "post_time": current_post_time.strftime("%Y-%m-%d %H:%M")
    }
    return video_info

def main():
    parser = argparse.ArgumentParser(
        description="各ディレクトリから動画情報の JSON を作成し、ファイル出力します"
    )
    parser.add_argument(
        "--base_dir", type=str, default=".",
        help="動画情報が格納されているディレクトリの親ディレクトリ (default: カレントディレクトリ)"
    )
    parser.add_argument(
        "--start_date", type=str, default=None,
        help='開始日時の指定 "YYYY-MM-DD HH:MM" （指定がない場合は実行日の次の日の同時刻）'
    )
    parser.add_argument(
        "--day_increment", type=int, default=1,
        help="グループ毎に加算する日数（default: 1）"
    )
    parser.add_argument(
        "--group_count", type=int, default=2,
        help="同一日付で処理する件数の指定（default: 2）"
    )
    parser.add_argument(
        "--output_file", type=str, default="output.json",
        help="生成した JSON を出力するファイルパス (default: output.json)"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="JSON化する件数（0の場合は全件、指定値があればその件数のみ処理）"
    )
    args = parser.parse_args()

    # 開始日時の設定
    if args.start_date:
        try:
            base_date = datetime.strptime(args.start_date, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError('start_date は "YYYY-MM-DD HH:MM" の形式で指定してください')
    else:
        now = datetime.now()
        base_date = now + timedelta(days=1)

    videos = []
    count = 0
    processed_in_group = 0  # 現在のグループで処理した件数
    group_limit = args.group_count  # 同一日付に割り当てる件数

    # 指定したディレクトリ内のサブディレクトリを処理（隠しディレクトリは除外）
    for item in sorted(os.listdir(args.base_dir)):
        if args.limit and count >= args.limit:
            break
        item_path = os.path.join(args.base_dir, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            try:
                video_info = process_directory(item_path, base_date)
                videos.append(video_info)
                count += 1
                processed_in_group += 1
                # グループ件数に達したら日付をインクリメントし、カウンターをリセット
                if processed_in_group >= group_limit:
                    base_date += timedelta(days=args.day_increment)
                    processed_in_group = 0
            except FileNotFoundError as e:
                print(f"[WARNING] {e}")

    output = {"videos": videos}
    # JSON を整形して指定ファイルへ出力
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"JSONファイルを {args.output_file} に出力しました。")

if __name__ == "__main__":
    main()
