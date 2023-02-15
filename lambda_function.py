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

    user_records = []

    for firebase_user in firebase_users.users:
        user_record = {
            "Username": firebase_user.email,
            "UserAttributes": [
                {"Name": "email", "Value": firebase_user.email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "custom:firebase_uid", "Value": firebase_user.uid},
            ],
            "MessageAction": "SUPPRESS",
        }
        user_records.append(user_record)

    response = cognito.create_user_import_job(
        JobName="FirebaseUserImport",
        UserPoolId="us-east-1_b0gOancme",
        CloudWatchLogsRoleArn="arn:aws:iam::your-account-id:role/Cognito_User_Import_Service_Role",
        UserRecords=user_records,
    )

    print("User import job created: ", response)

    return {
        "statusCode": 200,
        "body": json.dumps("Firebase users migrated to Cognito successfully"),
    }
