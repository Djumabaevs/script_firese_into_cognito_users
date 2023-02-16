import json
import boto3
import firebase_admin
from firebase_admin import credentials, auth


def lambda_handler(event, context):
    s3 = boto3.client("s3")

    s3_response = s3.get_object(Bucket="firebase-prod-admin-creds",
                                Key="memr-prod-firebase-adminsdk-19tek-256f2956ce.json")

    cert_str = s3_response["Body"].read().decode('utf-8')

    cert_dict = json.loads(cert_str)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(cred)

    firebase_auth = firebase_admin.auth

    firebase_users = firebase_auth.list_users()

    cognito = boto3.client("cognito-idp")

    for firebase_user in firebase_users.users:
        try:
            cognito.admin_create_user(
                UserPoolId='us-east-1_b0gOancme',
                Username=firebase_user.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': firebase_user.email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'custom:firebase_uid', 'Value': firebase_user.uid},
                ],
                DesiredDeliveryMediums=['EMAIL'],
            )
        except Exception as e:
            print(e)

    return {
        "statusCode": 200,
        "body": json.dumps("Firebase users migrated to Cognito successfully"),
    }
