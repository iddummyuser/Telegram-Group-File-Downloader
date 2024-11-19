from telethon import TelegramClient, events
from telethon.errors import FileMigrateError
from telethon.tl.types import MessageMediaDocument, Channel, Chat
import yaml
import os
import shutil
from tqdm import tqdm

# Load API keys and other configurations from the YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

api_id = config["api_id"]
api_hash = config["api_hash"]
phone_number = config["phone_number"]
group_usernames = config["group_usernames"]  # Now expects an array of group usernames
download_path = config["download_path"]

# Minimum free disk space in bytes to allow download (e.g., 100 MB)
MIN_FREE_SPACE = 100 * 1024 * 1024
MAX_RETRIES = 5  # Maximum retry limit for file download

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def check_disk_space():
    """Check if there is enough disk space to download files."""
    total, used, free = shutil.disk_usage(download_path)
    return free >= MIN_FREE_SPACE

async def reconnect_to_dc(new_dc):
    """Reconnect to a new data center if FileMigrateError occurs."""
    await client.disconnect()
    client.session.set_dc(new_dc, client.session.server_address, client.session.port)
    await client.connect()

async def process_group(group_username):
    """Process a single group's downloads."""
    print(f"\nProcessing group: {group_username}")
    
    # Get the group by username
    try:
        group = await client.get_entity(group_username)
    except Exception as e:
        print(f"Error accessing group {group_username}: {e}")
        return
    
    # Check if the entity is a group or channel
    if not isinstance(group, (Channel, Chat)):
        print(f"The provided username {group_username} does not correspond to a group or channel.")
        return
    
    # Create group-specific folder
    group_folder = os.path.join(download_path, group_username)
    if not os.path.exists(group_folder):
        os.makedirs(group_folder)

    # Load previously downloaded files from a tracking file
    downloaded_files_path = os.path.join(group_folder, "downloaded_files.txt")
    if os.path.exists(downloaded_files_path):
        with open(downloaded_files_path, "r") as f:
            downloaded_files = set(line.strip() for line in f)
    else:
        downloaded_files = set()

    # Count total new files in the group
    total_files = 0
    async for message in client.iter_messages(group):
        if message.media and isinstance(message.media, MessageMediaDocument) and str(message.id) not in downloaded_files:
            total_files += 1

    print(f"Total new files found in {group_username}: {total_files}")

    if total_files == 0:
        print(f"No new files to download in {group_username}")
        return

    # Set up the progress bar
    progress_bar = tqdm(total=total_files, desc=f"Downloading files from {group_username}", unit="file")

    # Download new files with progress tracking
    async for message in client.iter_messages(group):
        if message.media and isinstance(message.media, MessageMediaDocument):
            if str(message.id) in downloaded_files:
                continue  # Skip already downloaded files
            
            password = None

            # Extract password from the message text or caption if present
            if message.message:
                if 'password:' in message.message.lower():
                    password = message.message.split('password:')[-1].strip()
                    password = password.split()[0]  # Extract the first word after "password:"
            
            # Check disk space before downloading
            if not await check_disk_space():
                print("Insufficient disk space. Skipping download.")
                progress_bar.update(1)
                continue
            
            retries = 0
            success = False
            while not success and retries < MAX_RETRIES:
                try:
                    # Attempt to download the file
                    file_name = await client.download_media(message, group_folder)
                    success = True  # Mark as successful if no exception
                except FileMigrateError as e:
                    retries += 1
                    print(f"File is in DC {e.new_dc}. Reconnecting... (Attempt {retries}/{MAX_RETRIES})")
                    await reconnect_to_dc(e.new_dc)
                except Exception as e:
                    print(f"An error occurred: {e}. Skipping file.")
                    break

            if not success:
                print(f"Failed to download file {message.id} after {MAX_RETRIES} attempts. Skipping.")
                progress_bar.update(1)
                continue

            # Rename the file with password if available
            if password:
                new_file_name = os.path.join(group_folder, f"pass_{password}_{os.path.basename(file_name)}")
                os.rename(file_name, new_file_name)
                print(f"Downloaded and renamed to: {new_file_name}")
            else:
                print(f"Downloaded: {file_name}")
            
            # Save the downloaded file ID
            downloaded_files.add(str(message.id))
            with open(downloaded_files_path, "a") as f:
                f.write(f"{message.id}\n")

            # Update progress bar
            progress_bar.update(1)

    # Close the progress bar after download completion
    progress_bar.close()

async def main():
    # Connect to the client
    await client.start(phone=phone_number)
    print("Client Created")

    # Process each group in the list
    for group_username in group_usernames:
        await process_group(group_username)

    print("\nAll groups processed! Download completed!")

# Run the client
with client:
    client.loop.run_until_complete(main())
