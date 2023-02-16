import json
import boto3
import firebase_admin
from firebase_admin import credentials, auth


def lambda_handler(event, context):
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
            firebase_usert = firebase_auth.get_user_by_email(
                firebase_user.email)
            password = firebase_usert.password_hash
            cognito.admin_create_user(
                UserPoolId='us-east-1_b0gOancme',
                Username=firebase_user.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': firebase_user.email},
                    {'Name': 'email_verified', 'Value': 'true'},
                ],
                DesiredDeliveryMediums=['EMAIL'],
                MessageAction='SUPPRESS',
                ForceAliasCreation=True,
            )
        except Exception as e:
            print(e)

    return {
        "statusCode": 200,
        "body": json.dumps("Firebase users migrated to Cognito successfully"),
    }
