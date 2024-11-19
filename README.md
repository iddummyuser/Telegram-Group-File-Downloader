# Telegram Group File Downloader

A Python script that downloads files from multiple Telegram groups/channels automatically. It includes features like password detection, progress tracking, and duplicate file prevention.

## Features

- Download files from multiple Telegram groups/channels
- Track download progress with progress bars
- Detect and include passwords in filenames (if specified in messages)
- Skip previously downloaded files
- Create separate folders for each group
- Check available disk space before downloading
- Handle file migration between Telegram data centers
- Retry mechanism for failed downloads
- Detailed logging and error handling

## Prerequisites

- Python 3.7 or higher
- Telegram API credentials (api_id and api_hash)
- Telegram account with access to target groups/channels

### Required Python Packages

```bash
pip install -r requirements.txt
```

The following packages are required:
- telethon
- pyyaml
- tqdm

## Setup

1. **Get Telegram API Credentials**
   - Visit https://my.telegram.org/auth
   - Log in with your phone number
   - Go to 'API development tools'
   - Create a new application
   - Note down the `api_id` and `api_hash`

2. **Configure the Application**
   - Create a `config.yaml` file in the script directory
   - Use the following format:

```yaml
api_id: "your_api_id"
api_hash: "your_api_hash"
phone_number: "your_phone_number"
group_usernames: 
  - "group1_username"
  - "group2_username"
  - "group3_username"
download_path: "path/to/download/folder"
```

3. **Create Requirements File**
   - Create a `requirements.txt` file with the following content:

```
telethon
pyyaml
tqdm
```

## Usage

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python telegram_downloader.py
```

On first run:
- You'll be prompted to enter your phone number
- Telegram will send you a verification code
- Enter the code when prompted
- The script will create a session file for future use

## File Organization

The script organizes downloaded files as follows:
```
download_path/
├── group1_username/
│   ├── downloaded_files.txt
│   └── [downloaded files]
├── group2_username/
│   ├── downloaded_files.txt
│   └── [downloaded files]
└── group3_username/
    ├── downloaded_files.txt
    └── [downloaded files]
```

## Password Detection

If a message contains "password:" followed by a word, the downloaded file will be renamed with the format:
```
pass_[password]_[original_filename]
```

## Error Handling

The script includes several error handling features:
- Checks for sufficient disk space before downloads
- Retries downloads on failure (maximum 5 attempts)
- Handles Telegram data center migrations
- Skips problematic files after maximum retry attempts
- Continues to next file/group if an error occurs

## Limitations

- Downloads files sequentially (not parallel)
- Requires member access to groups/channels
- Subject to Telegram's rate limits
- Minimum free disk space requirement: 100MB

## Troubleshooting

1. **Authentication Issues**
   - Delete the `session_name.session` file and restart the script
   - Verify your API credentials in config.yaml
   - Ensure your account has access to the specified groups

2. **Download Errors**
   - Check your internet connection
   - Verify sufficient disk space
   - Ensure group usernames are correct
   - Check group access permissions

3. **Rate Limiting**
   - If you encounter rate limits, the script will automatically handle most cases
   - For persistent issues, try reducing the number of groups or increasing delays

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Ensure you have permission to download content from the target groups/channels. Respect copyright and terms of service of both Telegram and the content providers.
