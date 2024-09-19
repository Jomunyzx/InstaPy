import os
import time
from instagrapi import Client

# Function to get environment variables or prompt user for input
def get_env_variable(var_name, prompt):
    value = os.getenv(var_name)
    if not value:
        value = input(prompt)
    return value

# Get credentials from environment variables or user input
USERNAME = get_env_variable('INSTA_USERNAME', 'Enter your Instagram username: ')
PASSWORD = get_env_variable('INSTA_PASSWORD', 'Enter your Instagram password: ')

# Login to Instagram
def login_to_instagram(username, password):
    try:
        api = Client()
        api.login(username, password)
        print(f"Successfully logged in as {username}")
        return api
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return None

# Show DMs
def show_dms(api):
    try:
        threads = api.direct_threads()
        for i, thread in enumerate(threads):
            users = ", ".join([user.username for user in thread.users])
            print(f"{i + 1}: {users}")
        return threads
    except Exception as e:
        print(f"An error occurred while fetching DMs: {e}")
        return []

# View messages from a user with live updates
# View messages from a user with live updates
def view_messages(api, thread_id):
    seen_messages = set()
    try:
        while True:
            thread = api.direct_thread(thread_id)
            new_messages = []
            for message in thread.messages:
                if message.id not in seen_messages:
                    sender = message.user_id
                    text = message.text or '[No Text]'
                    new_messages.append(f"{sender}: {text}")
                    seen_messages.add(message.id)
            if new_messages:
                for msg in reversed(new_messages):
                    print(msg)
            time.sleep(0.5)  # Wait for 2 seconds before checking for new messages
    except Exception as e:
        print(f"An error occurred while fetching messages: {e}")

# Send a message
def send_message(api, thread_id, message):
    try:
        api.direct_send(message, thread_ids=[thread_id])
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")

# Download media from messages
def download_media(api, thread_id, download_path='./downloads'):
    try:
        thread = api.direct_thread(thread_id)
        os.makedirs(download_path, exist_ok=True)
        for message in thread.messages:
            if message.media:
                media_url = message.media.url
                media_id = message.id
                filename = os.path.join(download_path, f"{media_id}.jpg")
                with open(filename, 'wb') as f:
                    f.write(api.get_media(media_url).content)
                print(f"Downloaded {filename}")
    except Exception as e:
        print(f"An error occurred while downloading media: {e}")

# Main function to interact with the user
def main():
    api = login_to_instagram(USERNAME, PASSWORD)
    if api:
        threads = show_dms(api)
        if threads:
            choice = int(input("Select a user by number to view messages: ")) - 1
            if 0 <= choice < len(threads):
                thread_id = threads[choice].id
                # Start live updating messages in a separate thread
                import threading
                threading.Thread(target=view_messages, args=(api, thread_id), daemon=True).start()
                while True:
                    message = input("> ")
                    if message.lower() == 'exit':
                        break
                    send_message(api, thread_id, message)

if __name__ == '__main__':
    main()
