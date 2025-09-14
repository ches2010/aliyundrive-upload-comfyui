# find_folder_id.py
import sys
import subprocess

# --- 1. Ensure aligo is installed ---
try:
    from aligo import Aligo
except ImportError:
    print("Aligo not found. Installing...")
    subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install', 'aligo'])
    from aligo import Aligo

# --- 2. Replace with YOUR valid refresh token ---
YOUR_REFRESH_TOKEN = "your_actual_valid_refresh_token_here"

def find_folders(ali_instance, parent_id='root', search_name=None, level=0):
    """
    Recursively list folders.
    If search_name is provided, it will look for a folder with that name.
    """
    indent = "  " * level
    try:
        # List files (including folders) in the given parent folder
        file_list = ali_instance.get_file_list(parent_file_id=parent_id)
        if not file_list:
             print(f"{indent}No files/folders found in parent ID: {parent_id}")
             return None

        found_folder = None
        for file in file_list:
            if file.type == 'folder':
                print(f"{indent}[Folder] Name: '{file.name}', ID: '{file.file_id}'")
                # If we are searching for a specific name
                if search_name and file.name == search_name:
                    print(f"{indent}>>> Found target folder '{search_name}' with ID: {file.file_id}")
                    return file.file_id # Return the ID immediately if found
                # Recursively search within this folder (optional, can be commented out for large drives)
                # found_in_sub = find_folders(ali_instance, file.file_id, search_name, level + 1)
                # if found_in_sub:
                #     return found_in_sub # Propagate the found ID up the call stack
        return found_folder # Return None if not found at this level
    except Exception as e:
        print(f"{indent}Error listing files in parent ID '{parent_id}': {e}")
        return None

def main():
    """Main function to run the folder finder."""
    if not YOUR_REFRESH_TOKEN or YOUR_REFRESH_TOKEN == "your_actual_valid_refresh_token_here":
        print("Error: Please replace 'your_actual_valid_refresh_token_here' with your real refresh token in the script.")
        return

    try:
        print("Initializing Aligo with your refresh token...")
        ali = Aligo(refresh_token=YOUR_REFRESH_TOKEN)
        print("Aligo initialized successfully.\n")

        print("--- Listing folders in Root Directory ---")
        # List folders in the root directory
        find_folders(ali, parent_id='root')

        print("\n--- Searching for a specific folder (example: 'MyUploads') ---")
        # Example: Search for a folder named 'MyUploads' in the root
        # Change 'MyUploads' to the name of the folder you are looking for
        target_folder_name = "MyUploads"
        print(f"Searching for folder named: '{target_folder_name}'")
        folder_id = find_folders(ali, parent_id='root', search_name=target_folder_name)
        if not folder_id:
            print(f"Folder named '{target_folder_name}' not found in root directory.")
        # Note: This simple search only looks in the root. For nested folders,
        # a more complex recursive search or path-based lookup is needed.

        print("\n--- End of Listing ---")
        print("\nPlease copy the correct 'ID' of the folder you want to use and paste it into the ComfyUI node's 'folder_id' field.")

    except Exception as e:
        print(f"An error occurred during initialization or listing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
