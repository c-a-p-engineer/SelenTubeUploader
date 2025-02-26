# SelenTubeUploader

[![Build Status](https://img.shields.io/github/actions/workflow/status/your_username/SelenTubeUploader/build.yml?branch=master&label=Build%20Status)](https://github.com/your_username/SelenTubeUploader/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/your_username/SelenTubeUploader?style=social)](https://github.com/your_username/SelenTubeUploader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/your_username/SelenTubeUploader?style=social)](https://github.com/your_username/SelenTubeUploader/network)

SelenTubeUploader is a tool to automate video uploads on YouTube Studio using Python, Selenium, and webdriver-manager.  
It reads video parameters (video file path, thumbnail, title, description, and post time) from a JSON configuration file and uploads multiple videos sequentially.

Moreover, you can preserve your login state by specifying your existing Chrome user profile via the `--user-data-dir` and `--profile-directory` options.  
> **Note:** The values for these options can be verified at [chrome://version](chrome://version).

---

## Features

- **Automated Uploads**  
  Automate all operations in YouTube Studio—from uploading video files and setting titles/descriptions, to configuring thumbnails, post times, and scheduling—using Selenium.

- **Multiple Video Support**  
  Describe multiple video entries in a JSON configuration file, and the videos will be uploaded in the specified order.

- **User Profile Specification**  
  Use the `--user-data-dir` and `--profile-directory` command-line options to run the tool with an existing Chrome profile.

- **Debug Logging Toggle**  
  Activate detailed debug logging with the `--debug` option; if omitted, logging defaults to INFO level.

- **UI-Specific Workarounds**  
  - Title input is handled using ActionChains to select, clear, and then enter text.
  - Description input is updated via a TrustedTypes policy to avoid BMP character errors.
  - The "No, it's not made for kids" radio button is clicked.
  - Date and time are entered directly into text fields (pressing Enter to confirm), with support for adjustments based on Chrome Recorder recordings.
  - The final "Publish/Schedule" button is clicked using a specific element ID (e.g., `second-container-expand-button`) or XPath.

---

## Requirements

- **Python 3.11** (recommended)
- **Google Chrome** (latest version recommended)
- **ChromeDriver** (managed automatically via webdriver-manager)
- Python packages:
  - `selenium`
  - `webdriver-manager`
  - Standard libraries such as `argparse` and `logging`

---

## Installation

Install the required packages using pip:

```bash
pip install selenium webdriver-manager
```

---

## Usage

### A. SelenTubeUploader

#### 1. Configuration File Preparation

Create a JSON file (e.g., `config.json` or `sample.json`) containing video parameters. Example:

```json
{
  "videos": [
    {
      "video_path": "C:\\path\\to\\video1.mp4",
      "thumbnail": "C:\\path\\to\\thumbnail1.jpg",
      "title": "Video Title 1",
      "description": "Line 1\nLine 2\nLine 3",
      "post_time": "2030-12-31 12:34"
    }
  ]
}
```

#### 2. Specify User Profile

Provide your Chrome user data directory and profile directory to retain your login state.  
Values can be found at [chrome://version](chrome://version).  
Example:
- **user-data-dir**: `C:\Users\xxxxx\AppData\Local\Google\Chrome\User Data`
- **profile-directory**: `Profile 1`

#### 3. Command-Line Execution Examples

Run the uploader with the desired options:

```bash
python upload_video.py --config sample.json --user-data-dir "C:\Users\xxxxx\AppData\Local\Google\Chrome\User Data" --profile-directory "Profile 1" --debug
```

**Option Descriptions:**

- `--config`  
  Path to the configuration file (default: `config.json`).

- `--user-data-dir`  
  Path to the Chrome user data directory (verify at [chrome://version](chrome://version)).

- `--profile-directory`  
  Name of the Chrome profile directory (e.g., "Profile 1"; verify at [chrome://version](chrome://version)).

- `--debug`  
  Enable detailed debug logging; if omitted, logs are output at INFO level.

#### 4. Log In to YouTube Studio

Make sure you are logged in to YouTube Studio with the specified profile. The script will prompt you to press Enter after you have logged in.

#### 5. Script Execution

After executing the command, the script will automatically upload videos as specified in your configuration file. Progress and status messages will be logged, and you'll be prompted between uploads if multiple videos are processed.

---

### B. Video Information JSON Generation Tool (`create_video_json.py`)

This tool extracts video information from subdirectories within a parent directory and generates a JSON file. It reads each subdirectory for the necessary files (a .mp4 video file, `thumbnail.jpg`, and `description.txt`) and constructs a JSON structure.

#### Features

- **Output File Specification**  
  Use the `--output_file` option to set the destination for the generated JSON. If not specified, the output is saved as `output.json` in the current directory.

- **Limit on Processed Items**  
  Use the `--limit` option to restrict the number of subdirectories processed. A value of 0 (default) processes all directories.

- **Group Count Option**  
  The `--group_count` option specifies how many items are processed with the same date (default is 2).

- **Date Increment**  
  While processing each subdirectory, a counter (`processed_in_group`) is used. When it reaches the specified `group_count`, the base date is incremented by the number of days specified in `--day_increment`, and the counter resets.

#### Command-Line Example

The following command processes the first 6 subdirectories in `./videos_folder`, starting with a post time of "2025-02-28 15:30", incrementing the date by 1 day for every 3 items, and outputs the result to `result.json`:

```bash
python create_video_json.py --base_dir "./videos_folder" --start_date "2025-02-28 15:30" --day_increment 1 --group_count 3 --limit 6 --output_file "result.json"
```

**Option Descriptions:**

- `--base_dir`  
  Path to the parent directory containing video information subdirectories (default: current directory).

- `--start_date`  
  Starting date/time in the format `"YYYY-MM-DD HH:MM"`. If not specified, the next day at the same time as the current date is used.

- `--day_increment`  
  Number of days to increment after processing each group (default: 1).

- `--group_count`  
  Number of subdirectories to process per date (default: 2).

- `--limit`  
  Limit the total number of subdirectories processed (0 for all, default: 0).

- `--output_file`  
  Path for the output JSON file (default: `output.json`).

---

## Notes

- **UI Changes**  
  YouTube Studio's UI is frequently updated. Adjust XPath and CSS selectors according to the latest DOM structure.

- **ChromeDriver & Chrome Versions**  
  If errors occur due to version changes, update webdriver-manager or review Selenium configurations.

- **TrustedTypes Handling**  
  The description field is updated using a TrustedTypes policy to prevent errors with non-BMP characters. Behavior may vary with different Chrome versions.

- **Debug Logging Toggle**  
  Use the `--debug` option to enable detailed logs. Omit this option to use standard INFO-level logging.

---

## License

This project is licensed under the MIT License. Please refer to the LICENSE file for details.
