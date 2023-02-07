import firebase_admin 
from firebase_admin import credentials 
from firebase_admin import auth 
 
def lambda_handler(event, context): 
    s3 = boto3.client("s3") 
 
    s3_response = s3.get_object(Bucket="s3://firebase-prod-admin-creds/", Key="memr-prod-firebase-adminsdk-19tek-256f2956ce.json") 
 
    cred = credentials.Certificate(s3_response["Body"].read()) 
 
    firebase_admin.initialize_app(cred) 
 
    firebase_auth = firebase_admin.auth 
 
    firebase_users = firebase_auth.list_users() 
 
    cognito = boto3.client("cognito-idp") 
 
    for firebase_user in firebase_users.users: 
        try: 
            response = cognito.admin_create_user( 
                UserPoolId="us-east-1_b0gOancme", 
                Username=firebase_user.email, 
                UserAttributes=[ 
                     { 
                        "Name": "email", 
                        "Value": firebase_user.email 
                     }, 
                     { 
                        "Name": "password", 
                        "Value": str(firebase_user.password) 
                     }, 
                ], 
                MessageAction="SUPPRESS" 
            ) 
            cognito.admin_confirm_sign_up( 
                UserPoolId="us-east-1_b0gOancme", 
                Username=firebase_user.email, 
            ) 
 
            cognito.admin_update_user_attributes( 
                UserPoolId="us-east-1_b0gOancme", 
                Username=firebase_user.email, 
                UserAttributes=[ 
                     {"Name": "password", "Value": firebase_user.password }, 
                ], 
            ) 
            print("Successfully migrated user:", firebase_user.email) 
        except Exception as e: 
            print("Failed to migrate user:", firebase_user.email, "Error:", e) 
 
    return  { 
        "statusCode": 200, 
        "body": json.dumps("Firebase users migrated to Cognito successfully") 
     } 
