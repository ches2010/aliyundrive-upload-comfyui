# test_aligo.py
import sys
import subprocess

# --- 1. Ensure aligo is installed ---
try:
    from aligo import Aligo
except ImportError:
    print("Aligo not found. Installing...")
    subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install', 'aligo'])
    from aligo import Aligo

# --- 2. Replace with YOUR actual refresh token ---
YOUR_REFRESH_TOKEN = "your_actual_refresh_token_here"

def test_refresh_token(token):
    """Test if the provided refresh token is valid."""
    if not token or token == "your_actual_refresh_token_here":
         print("Error: Please replace 'your_actual_refresh_token_here' with your real refresh token in the script.")
         return False

    try:
        print("Attempting to initialize Aligo with the provided refresh token...")
        # Initialize Aligo. This will use the refresh token to get an access token.
        ali = Aligo(refresh_token=token)
        
        # Perform a simple action to verify the token works, e.g., get user info or root folder
        user_info = ali.get_user()
        if user_info:
            print(f"Success! Refresh token is valid. User: {user_info.nick_name} (ID: {user_info.user_id})")
            return True
        else:
             print("Warning: Aligo initialized but failed to retrieve user info.")
             return False

    except Exception as e:
        print(f"Error: Failed to initialize Aligo or perform test action. The refresh token is likely invalid.")
        print(f"Details: {e}")
        # Optionally print traceback for more details
        # import traceback
        # traceback.print_exc()
        return False

if __name__ == "__main__":
    is_valid = test_refresh_token(YOUR_REFRESH_TOKEN)
    if not is_valid:
        print("\nPlease obtain a new, valid refresh token and try again.")
        exit(1) # Exit with error code
    else:
        print("\nRefresh token test passed.")
        exit(0) # Exit successfully
