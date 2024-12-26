import json
import os
import sys
import zipfile
import requests
from mega import Mega
from pathlib import Path
from tqdm import tqdm

# Initialize Mega instance
mega = Mega()

def get_file_name(file_path):
    """Extracts file or folder name from the path."""
    return Path(file_path).name

def password_checker(email, password):
    """Checks if the credentials are valid."""
    try:
        mega.login(email, password)
        return True
    except Exception:
        return False

def login_to_mega(email, password):
    """Logs into Mega and returns the login cookie."""
    if password_checker(email, password):
        return mega.login(email, password)
    return None

def get_storage_details(login_cookie):
    """Retrieves storage details of the logged-in user."""
    if not login_cookie:
        raise ValueError("Invalid login session.")
    
    space = login_cookie.get_storage_space(kilo=True)
    total = space['total']
    used = space['used']
    remain = total - used
    
    return {'total': total, 'used': used, 'remaining': remain}

def upload_and_generate_info(login_cookie, file_path, root_path, email, password):
    """Uploads a file to Mega and generates a shareable link."""
    if not login_cookie:
        raise ValueError("Invalid login session.")
    
    uploaded_file = login_cookie.upload(file_path)
    link = login_cookie.get_upload_link(uploaded_file)
    return [email, password, root_path, link]

def file_size(filepath):
    """Returns the size of the file."""
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError("The specified file does not exist.")
        
        return os.path.getsize(filepath)
    
    except Exception as e:
        return f"Error: {e}"

def load_accounts_from_json(json_file):
    """Loads MEGA account credentials from a JSON file."""
    try:
        with open(json_file, 'r') as file:
            accounts = json.load(file)
            return [(account['email'], account['password']) for account in accounts]
    except Exception as e:
        return f"Error loading JSON file: {e}"

def find_account_with_sufficient_storage(json_file, file_path):
    """Finds an account with enough storage space for the file."""
    accounts = load_accounts_from_json(json_file)
    if isinstance(accounts, str):
        return accounts
    
    file_size_in_bytes = file_size(file_path)
    if isinstance(file_size_in_bytes, str):
        return file_size_in_bytes
    
    for email, password in accounts:
        login_cookie = login_to_mega(email, password)
        if login_cookie:
            storage_details = get_storage_details(login_cookie)
            available_space = storage_details['remaining']
            if available_space >= file_size_in_bytes:
                return [email, password]
    
    return "No account has enough storage for the file upload."

def path_keeper_server(root_path, link_path, text_file):
    """Appends the root path and link to a server file."""
    try:
        with open(text_file, 'a') as file:
            line = f"{root_path} => {link_path}\n"
            file.write(line)
        return "Path added successfully."
    except Exception as e:
        return f"Error appending path: {e}"

def path_keeper(root_path, text_file):
    """Appends the root path to a file."""
    try:
        with open(text_file, 'a') as file:
            line = f"{root_path}\n"
            file.write(line)
        return "Path added successfully."
    except Exception as e:
        return f"Error appending path: {e}"

def upload_folder(login_cookie, folder_path, root_path, email, password):
    """Uploads a folder to MEGA and generates links."""
    links = []
    files = []
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, folder_path)
            current_root_path = os.path.join(root_path, relative_path)
            files.append((file_path, current_root_path))
    
    with tqdm(total=len(files), desc="Uploading Files", unit="file") as progress_bar:
        for file_path, current_root_path in files:
            # Upload the file and get the link
            upload_info = upload_and_generate_info(login_cookie, file_path, current_root_path, email, password)
            links.append(upload_info)
            path_keeper_server(upload_info[2], [upload_info[0], upload_info[1], upload_info[3]], 'SERVER_PATHS.txt')
            path_keeper(upload_info[2], 'SERVER.txt')
            path_keeper_server(upload_info[2], upload_info[3], 'SERVER_PATHS_DOWNLOAD.txt')
            progress_bar.update(1)
    
    return links

def create_folder_if_not_exists(login_cookie, folder_path):
    """Checks if the folder exists on MEGA, and creates it if not."""
    folder = mega.find(folder_path)
    if not folder:
        # If folder doesn't exist, create it
        folder = mega.create_folder(folder_path)
    return folder

def split_large_file(file_path, chunk_size=19 * 1024 * 1024 * 1024):
    """Splits large files into smaller parts (19GB default)."""
    file_parts = []
    with open(file_path, 'rb') as f:
        part_number = 1
        while chunk := f.read(chunk_size):
            part_name = f"{file_path}.part{part_number}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            file_parts.append(part_name)
            part_number += 1
    return file_parts

def download_file_from_url(url, download_path):
    """Downloads a file from a URL."""
    try:
        response = requests.get(url, stream=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {download_path}")
        return download_path
    except Exception as e:
        return f"Error downloading file: {e}"

def main(file_path, target_path='root', url=None):
    print('Welcome to MEGA file uploader')
    
    if url:
        file_path = download_file_from_url(url, 'temp_downloaded_file')
        if file_path.startswith("Error"):
            print(file_path)
            return
    
    if not os.path.exists(file_path):
        print("The specified path does not exist. Please check and try again.")
        return
    
    # Ask for the JSON file with account credentials
    json_file = 'mega_credentials.json'
    if not os.path.exists(json_file):
        print("The JSON file does not exist. Please check and try again.")
        return
    
    email_password = find_account_with_sufficient_storage(json_file, file_path)
    if isinstance(email_password, str):
        print(email_password)
        return
    
    login_cookie = login_to_mega(email_password[0], email_password[1])
    if not login_cookie:
        print("Failed to log in to MEGA.")
        return
    
    # Check if the target folder exists, if not, create it
    folder_path = target_path
    if folder_path != 'root':
        create_folder_if_not_exists(login_cookie, folder_path)
    
    root_path = os.path.join(folder_path, get_file_name(file_path))  # Full path in target folder
    
    # If it's a folder, upload it
    if os.path.isdir(file_path):
        print("Uploading folder...")
        upload_links = upload_folder(login_cookie, file_path, root_path, email_password[0], email_password[1])
        print(f"Folder uploaded successfully!")
    
    # If it's a large file, split it and upload
    elif file_size(file_path) > 19 * 1024 * 1024 * 1024:  # 19GB
        print("File is too large, splitting into smaller parts...")
        file_parts = split_large_file(file_path)
        for part in file_parts:
            upload_info = upload_and_generate_info(login_cookie, part, root_path, email_password[0], email_password[1])
            print(f"Uploaded part: {upload_info[3]}")
        print(f"Large file uploaded successfully!")
    
    # If it's a small file, upload it directly
    else:
        print("Uploading file...")
        with tqdm(total=1, desc="Uploading File", unit="file") as progress_bar:
            upload_info = upload_and_generate_info(login_cookie, file_path, root_path, email_password[0], email_password[1])
            path_keeper_server(upload_info[2], [upload_info[0], upload_info[1], upload_info[3]], 'SERVER_PATHS.txt')
            path_keeper(upload_info[2], 'SERVER.txt')
            path_keeper_server(upload_info[2], upload_info[3], 'SERVER_PATHS_DOWNLOAD.txt')
            progress_bar.update(1)
        print(f"File uploaded successfully! Link: {upload_info[3]}")

    # Clean up the temporary file if it was downloaded
    if url:
        os.remove('temp_downloaded_file')

if __name__ == "__main__":   
    print('\n\n\n'+r'       EXAMPLE : python -u "c:FINAL_SINGLE_SERVER.py" "C:\Users\E.jpg" "root\hello"'+'\n\n\n') 
    if len(sys.argv) < 2:
        print("Usage: python filename.py <file_path> [target_path] [url]")
    else:
        file_path = sys.argv[1].strip("\\/")  # Removes leading and trailing slashes/backslashes
        target_path = sys.argv[2].strip("\\/") if len(sys.argv) > 2 else 'root'
        url = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Call the main function with the sanitized file_path, target_path, and url
        main(file_path, target_path, url)
