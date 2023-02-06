import csv
import json

# Load the JSON data from the exported Firebase Auth file
with open('firebase_users.json', 'r') as f:
    data = json.load(f)

# Create a new CSV file for the Cognito import data
with open('cognito_import.csv', 'w', newline='') as csvfile:
    fieldnames = ['name', 'given_name', 'family_name', 'middle_name', 'nickname', 'preferred_username', 'profile', 'picture', 'website', 'email', 'email_verified', 'gender', 'birthdate', 'zoneinfo', 'locale', 'phone_number', 'phone_number_verified', 'address', 'updated_at', 'cognito:mfa_enabled', 'cognito:username']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header row to the CSV file
    writer.writeheader()

    # Loop through each user in the Firebase Auth data
    for user in data['users']:
        # Create a new row in the CSV file for the user
        row = {
            'name': user['email'],
            'given_name': '',
            'family_name': '',
            'middle_name': '',
            'nickname': '',
            'preferred_username': user['email'],
            'profile': '',
            'picture': user.get('photoUrl', ''),
            'website': '',
            'email': user['email'],
            'email_verified': 'true' if user.get('emailVerified', False) else 'true',
            'gender': '',
            'birthdate': '',
            'zoneinfo': '',
            'locale': '',
            'phone_number':'+19999999999',
            'phone_number_verified': False,
            'address': '',
            'updated_at': '',
            'cognito:mfa_enabled': 'false',
            'cognito:username': user['email']
        }
        writer.writerow(row)
        
        
        
        








