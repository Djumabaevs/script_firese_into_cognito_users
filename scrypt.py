import json
import boto3
import requests
import firebase_admin
from firebase_admin import credentials, auth
import base64
import scrypt


def get_password_hash(password):
    signer_key = base64.b64decode(
        "aSjoqCyLRKZP/BkgWmoYvTydvmS0owIJB/GQgGyFYZ+nWH9tlLV7h9tZZNWgIFyAFqJkt9EHe4NwtqiNoCehBw==")
    salt = base64.b64decode("Bw==")
    rounds = 8
    mem_cost = 14

    derived_key = scrypt.hash(password, salt, N=2**rounds, r=8, p=1, buflen=32)
    derived_key_b64 = base64.b64encode(derived_key)

    return scrypt.encrypt(derived_key_b64, signer_key, N=2**rounds, r=8, p=1, buflen=32, maxtime=0.1).hex()


def lambda_handler(event, context):
    print("Function starting")
    s3 = boto3.client("s3")

    s3_response = s3.get_object(Bucket="firebase-prod-admin-creds",
                                Key="memr-e997e-firebase-adminsdk-lorjt-0608a74967.json")

    cert_str = s3_response["Body"].read().decode('utf-8')

    cert_dict = json.loads(cert_str)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(cred)

    firebase_auth = firebase_admin.auth

    firebase_users = firebase_auth.list_users()

    cognito = boto3.client("cognito-idp")

    for firebase_user in firebase_users.users:
        try:
            firebase_user = auth.get_user_by_email(firebase_user.email)
            uid = firebase_user.uid
            password = scrypt.decrypt(base64.b64decode(firebase_user.password_hash), base64.b64decode(
                "aSjoqCyLRKZP/BkgWmoYvTydvmS0owIJB/GQgGyFYZ+nWH9tlLV7h9tZZNWgIFyAFqJkt9EHe4NwtqiNoCehBw=="), maxtime=0.1)
            password_hash = get_password_hash(password.decode("utf-8"))
            response = cognito.admin_create_user(
                UserPoolId='us-east-1_b0gOancme',
                Username=firebase_user.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': firebase_user.email},
                    {'Name': 'email_verified', 'Value': 'true'},
                ],
                TemporaryPassword=password.decode("utf-8"),
                DesiredDeliveryMediums=['EMAIL'],
                MessageAction='SUPPRESS',
                ForceAliasCreation=False
            )
            print(firebase_user.email)
            print(response.text)
            print(f"!!!!!!!!!!!!!!!!!!! {response.text}")
        except Exception as e:
            print(f"Error creating user {firebase_user.email} in Cognito: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Firebase users migrated to Cognito successfully"),
    }
