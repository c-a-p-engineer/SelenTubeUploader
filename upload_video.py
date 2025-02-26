#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SelenTubeUploader - YouTube動画アップロード自動化スクリプト
(複数動画・設定ファイル対応・デバッグログ付き・ユーザープロファイル指定対応)
-----------------------------------------------------------
・Seleniumとwebdriver-managerを利用してChromeブラウザを起動
・設定ファイル（JSON形式）から各動画のパラメータを読み込み、順次アップロードを実施します:
  1. video_path  : アップロードする動画ファイルのパス
  2. thumbnail   : サムネイル画像のパス
  3. title       : 動画タイトル
  4. description : 動画説明文（改行を含む複数行設定可能）
  5. post_time   : 投稿日時 ("YYYY-MM-DD HH:MM"形式)
  
【注意】
- YouTube StudioのUI変更により、XPath等のセレクタは適宜調整してください。
- 自動化検出回避設定は含んでいますが、完全な回避は保証できません。

※ Chrome のユーザープロファイル設定値（--user-data-dir と --profile-directory）は chrome://version で確認できます。
"""

import argparse
import json
import time
from datetime import datetime
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def get_chrome_options(user_data_dir=None, profile_directory=None):
    """
    ChromeOptions を生成します。
    ※ --user-data-dir と --profile-directory の値は chrome://version で確認可能です。
    ※ エラー "session not created: probably user data directory is already in use" が発生する場合は、
       指定するディレクトリが既に使用中である可能性があります。
       ・すべての Chrome インスタンスを閉じるか、または一意のユーザーデータディレクトリを指定してください。
    """
    logging.debug("ChromeOptionsを生成中...")
    options = webdriver.ChromeOptions()
    if user_data_dir:
        logging.debug(f"--user-data-dir を追加: {user_data_dir}")
        options.add_argument(f"--user-data-dir={user_data_dir}")
    if profile_directory:
        logging.debug(f"--profile-directory を追加: {profile_directory}")
        options.add_argument(f"--profile-directory={profile_directory}")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features=TrustedTypes")
    return options

def launch_chrome(user_data_dir=None, profile_directory=None):
    """
    webdriver-managerでChromeDriverを自動インストールし、Chromeブラウザを起動
    また、CDPコマンドを用いてTrustedTypesを無効化する
    """
    logging.debug("Chromeブラウザを起動中...")
    options = get_chrome_options(user_data_dir, profile_directory)
    options.add_argument("--disable-extensions")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "window.TrustedTypes = undefined;"})
    logging.debug("Chromeブラウザの起動完了")
    return driver

def set_contenteditable_text(driver, element, text):
    """
    contenteditable 要素に TrustedTypes ポリシーを利用して text を設定し、input イベントを発火させる。
    """
    script = """
    if (window.trustedTypes && window.trustedTypes.createPolicy) {
        var policy = window.trustedTypes.createPolicy('default', {
            createHTML: function(input) { return input; }
        });
        arguments[0].innerHTML = policy.createHTML(arguments[1]);
    } else {
        arguments[0].innerHTML = arguments[1];
    }
    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
    """
    driver.execute_script(script, element, text)

def find_all(driver, by, value, timeout=15):
    """
    指定したロケータで要素のリストを取得する。timeout 内に見つからない場合は例外を発生させる。
    """
    return WebDriverWait(driver, timeout).until(lambda d: d.find_elements(by, value))

def upload_video(driver, video_config):
    """
    YouTube Studio上で動画アップロード処理を自動化する関数。

    Args:
        driver (webdriver.Chrome): SeleniumのWebDriverオブジェクト
        video_config (dict): 1動画分の設定（video_path, thumbnail, title, description, post_time）
    """
    wait = WebDriverWait(driver, 60)
    
    logging.info("YouTube Studioにアクセス中...")
    driver.get("https://studio.youtube.com")
    
    logging.info("「作成」ボタンをクリック中...")
    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[contains(., '作成')]")))
    create_btn.click()
    
    logging.info("「動画をアップロード」オプションをクリック中...")
    upload_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-item[contains(., '動画をアップロード')]")))
    upload_option.click()
    
    logging.info(f"動画ファイルをアップロード中: {video_config['video_path']}")
    file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    file_input.send_keys(video_config["video_path"])
    
    logging.info("タイトル、説明入力フィールドを取得中...")
    fields = find_all(driver, By.ID, "textbox", timeout=15)
    if len(fields) < 2:
        raise Exception("タイトル、説明の入力フィールドが見つかりませんでした。")
    title_field, description_field = fields[:2]
    
    logging.info("タイトルを設定中...")
    ActionChains(driver).move_to_element(title_field).click()\
        .key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)\
        .send_keys(Keys.DELETE).perform()
    title_field.send_keys(video_config["title"])
    
    logging.info("説明を設定中...")
    set_contenteditable_text(driver, description_field, video_config["description"])
    
    thumbnail = video_config.get("thumbnail", "")
    if thumbnail:
        logging.info(f"サムネイル画像をアップロード中: {thumbnail}")
        thumb_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='file' and contains(@accept, 'image')]")
        ))
        thumb_input.send_keys(thumbnail)
    else:
        logging.info("サムネイルは設定されていません")
    
    logging.info("『いいえ、子ども向けではありません』の選択を実行中...")
    not_for_kids = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@id='radioLabel' and contains(., 'いいえ、子ども向けではありません')]")
    ))
    not_for_kids.click()
    
    for i in range(3):
        logging.info(f"次へボタン（ステップ {i+1}）をクリック中...")
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']")))
        next_btn.click()
        time.sleep(1)
    
    logging.info("「スケジュール」ボタンをクリック中...")
    schedule_btn = wait.until(EC.element_to_be_clickable((By.ID, "second-container-expand-button")))
    schedule_btn.click()
    
    logging.info(f"投稿日時をパース中: {video_config['post_time']}")
    try:
        scheduled_dt = datetime.strptime(video_config["post_time"], "%Y-%m-%d %H:%M")
    except Exception as e:
        logging.error("投稿日時のパースに失敗しました。形式は 'YYYY-MM-DD HH:MM' で指定してください。")
        raise ValueError("投稿日時の形式が正しくありません。'YYYY-MM-DD HH:MM'形式で指定してください。") from e
    
    # 日付選択 (従来のinput型ではなく、カレンダーUIの場合)
    logging.debug("日付ドロップダウンを待機中...")
    date_dropdown = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "span.dropdown-trigger-text.style-scope.ytcp-text-dropdown-trigger")
    ))
    date_dropdown.click()
    logging.debug("日付ドロップダウンをクリックしました")
    
    # ここでカレンダーが展開されるまで少し待機（必要に応じて調整）
    time.sleep(1)
    logging.info("日付入力フィールドを操作中...")
    date_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-labelledby='paper-input-label-2']")))
    date_input.clear()
    date_str = scheduled_dt.strftime("%Y/%m/%d")
    logging.info(f"日付を入力: {date_str}")
    date_input.send_keys(date_str)
    date_input.send_keys(Keys.ENTER)
    
    # 時刻選択
    logging.info("時刻入力フィールドを操作中...")
    time_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-uploads-dialog input")))
    time_input.clear()
    time_str = scheduled_dt.strftime("%H:%M")
    logging.info(f"時刻を入力: {time_str}")
    time_input.send_keys(time_str)
    time_input.send_keys(Keys.ENTER)

    logging.debug("公開/スケジュール設定完了ボタンを待機・クリック中...")
    publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']")))
    publish_btn.click()
    logging.debug("公開/スケジュール設定完了ボタンクリック完了")

    time.sleep(3)

    logging.info("クローズボタンをクリック中...")
    close_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'footer')]//ytcp-button[@id='close-button']"))
    )
    close_button.click()

    logging.info(f"動画「{video_config['title']}」のアップロードが完了しました。")
    print(f"動画「{video_config['title']}」のアップロードが完了しました。")

def load_config(config_path):
    """
    設定ファイルを読み込み、'videos'キーが存在するか検証
    """
    logging.info(f"設定ファイルを読み込み中: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if "videos" not in config or not isinstance(config["videos"], list):
        error_msg = "設定ファイルには 'videos' キーに動画情報のリストを設定してください。"
        logging.error(error_msg)
        raise ValueError(error_msg)
    required_keys = ["video_path", "thumbnail", "title", "description", "post_time"]
    for idx, video in enumerate(config["videos"], start=1):
        for key in required_keys:
            if key not in video:
                error_msg = f"動画{idx}の設定に必須項目 '{key}' が含まれていません。"
                logging.error(error_msg)
                raise ValueError(error_msg)
    logging.info("設定ファイルの読み込み完了")
    return config

def main():
    """
    メイン処理:
    ・コマンドライン引数で設定ファイル、ユーザーデータディレクトリ、プロファイルディレクトリ、ログレベルを受け取り、各動画設定を読み込む
    ・Chromeブラウザを起動し、ユーザーにログイン完了後に動画アップロードを順次実行
    """
    parser = argparse.ArgumentParser(
        description="Chromeを起動してYouTube Studioに動画をアップロードするスクリプト"
                    " (複数動画・設定ファイル対応・ユーザープロファイル指定)"
    )
    parser.add_argument("--config", default="config.json", help="設定ファイルのパス (デフォルト: config.json)")
    parser.add_argument("--user-data-dir", default=None, help="Chromeのユーザーデータディレクトリのパス（chrome://version で確認可能）")
    parser.add_argument("--profile-directory", default=None, help="Chromeのプロファイルディレクトリのパス（chrome://version で確認可能、例: 'Profile 1'）")
    parser.add_argument("--debug", action="store_true", help="デバッグログを有効にする")
    args = parser.parse_args()

    # ログレベルをオプションにより切り替え
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    config = load_config(args.config)
    driver = launch_chrome(user_data_dir=args.user_data_dir, profile_directory=args.profile_directory)
    logging.info("YouTube Studioのトップページを開く")
    driver.get("https://studio.youtube.com/")

    input("YouTube StudioにログインしたらEnterキーを押してください...")

    try:
        for idx, video in enumerate(config["videos"], start=1):
            logging.info(f"\n--- 動画{idx}のアップロード開始 ---")
            print(f"\n--- 動画{idx}のアップロード開始 ---")
            upload_video(driver, video)
            if idx < len(config["videos"]):
                # 大きなファイルの場合、アップロード完了まで時間がかかるため待機
                time.sleep(60)
    except Exception as e:
        logging.error(f"アップロード中にエラーが発生しました: {e}")
        print(f"アップロード中にエラーが発生しました: {e}")
    finally:
        input("終了するにはEnterキーを押してください...")
        driver.quit()
        logging.info("Chromeブラウザを終了しました")

if __name__ == "__main__":
    main()
