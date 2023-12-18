import requests
import json
import os
import hashlib
import secrets

# Subsonic Server information
subsonic_url = 'https://your.navidrome-subsonic-server.tld/rest'
username = 'REPLACE-ME'  # Enter your username here
password = 'REPLACE-ME'  # Enter your password here
api_version = '1.13.0'
client_name = 'new2discord'

# Generate random salt
salt = secrets.token_hex(6)

# Calculate authentication token
token = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

# Discord Webhook information
discord_webhook_url =  'https://discord.com/api/webhooks/xxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Get API endpoint for the latest albums
api_endpoint = f'{subsonic_url}/getAlbumList.view'
params = {
    'u': username,
    't': token,
    's': salt,
    'v': api_version,
    'c': client_name,
    'type': 'newest',
    'f': 'json'  # Set the "f" parameter to "json" here
}

# File path to save the last result
last_result_path = 'lastresult'

# Make the API request
response = requests.get(api_endpoint, params=params)

# Print the API request details
print(f'\nAPI Request Details:\nURL: {response.url}\nParameters: {params}\n')

# Check if the request was successful
if response.ok:
    # Extract information about the latest albums
    try:
        data = response.json()
        latest_albums = data['subsonic-response']['albumList']['album']
    except json.JSONDecodeError:
        print('Error decoding the JSON response')
        latest_albums = []

    # Load the last result from the file
    last_result = None
    if os.path.exists(last_result_path):
        with open(last_result_path, 'r', encoding='utf-8') as file:
            try:
                last_result = json.load(file)
            except json.JSONDecodeError:
                print('Error loading the last result file')

    # Write the information to the "lastresult" file
    with open(last_result_path, 'w', encoding='utf-8') as file:
        json.dump(latest_albums, file, ensure_ascii=False, indent=2)

    # Check if the new result differs from the last one
    if last_result is None or latest_albums != last_result:
        # Send the list of latest albums to Discord via the webhook
        discord_content = '**New Albums:**\n\n'
        for album in latest_albums:
            discord_content += f'__**{album["title"]}**__ by __**{album["artist"]}**__ from __**{album["year"]}**__ has been uploaded \n'

        discord_payload = {
            'content': discord_content[:2000]  # Limit the length to 2000 characters
        }

        response_discord = requests.post(discord_webhook_url, json=discord_payload)

        # Check if the message was successfully sent
        if response_discord.ok:
            print('Message successfully sent to Discord.')
        else:
            print(f'Error sending the message to Discord: {response_discord.status_code} - {response_discord.text}')
else:
    print(f'Error in the request: {response.status_code} - {response.text}')

# Write the information to the "lastresult" file
with open(last_result_path, 'w', encoding='utf-8') as file:
    try:
        json.dump(latest_albums, file, ensure_ascii=False, indent=2)
        print('File "last_result" written successfully.')
    except Exception as e:
        print(f'Error writing the "last_result" file: {e}')
