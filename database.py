import boto3
import json
import os

sqs = boto3.client('sqs')
aws_lambda = boto3.client('lambda')
iam_client = boto3.client('iam')
role = iam_client.get_role(RoleName='LabRole')
s3 = boto3.client('s3')
rds = boto3.client('rds')
sfn = boto3.client('stepfunctions')

def setup(keyword):
    # Create S3 bucket to store raw JSON data
    s3.create_bucket(Bucket=f'{keyword}-bucket')
    # Create RDS
    try:
        response = rds.create_db_instance(
            DBInstanceIdentifier='relational-db',
            DBName=f'twitter_sentiment_{keyword}',
            MasterUsername='username',
            MasterUserPassword='password',
            DBInstanceClass='db.t2.micro',
            Engine='MySQL',
            AllocatedStorage=5
        )
    except:
        pass

    # Wait until DB is available to continue
    rds.get_waiter('db_instance_available').wait(DBInstanceIdentifier='relational-db')

    # Describe where DB is available and on what port
    db = rds.describe_db_instances()['DBInstances'][0]
    ENDPOINT = db['Endpoint']['Address']
    PORT = db['Endpoint']['Port']
    DBID = db['DBInstanceIdentifier']
    print(DBID,
        "is available at", ENDPOINT,
        "on Port", PORT,
        )   

    # Get Name of Security Group
    SGNAME = db['VpcSecurityGroups'][0]['VpcSecurityGroupId']

    # Adjust Permissions for that security group so that we can access it on Port 3306
    # If already SG is already adjusted, print this out
    try:
        ec2 = boto3.client('ec2')
        data = ec2.authorize_security_group_ingress(
                GroupId=SGNAME,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                    'FromPort': PORT,
                    'ToPort': PORT,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                ]
        )
    except ec2.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == 'InvalidPermission.Duplicate':
            print("Database permissions already adjusted.")
        else:
            print(e)

    # Create the lambda function for 10 parallel lambda workers
    with open('../twitter_sentiment_deployment_package.zip', 'rb') as f:
        lambda_zip = f.read()

    try:
        # If function hasn't yet been created, create it
        response = aws_lambda.create_function(
            FunctionName='twitter_sentiment',
            Runtime='python3.9',
            Role=role['Role']['Arn'],
            Handler='lambda_function.lambda_handler',
            Code=dict(ZipFile=lambda_zip),
            Timeout=100
        )
    except aws_lambda.exceptions.ResourceConflictException:
        # If function already exists, update it based on zip
        # file contents
        response = aws_lambda.update_function_code(
        FunctionName='twitter_sentiment',
        ZipFile=lambda_zip
        )

    lambda_arn = response['FunctionArn']    

    # Create state machine
    os.system("python ../sfn_setup.py")

    return 


def send_data(data, keyword, file=False):
    if file:
        # print(data)
        setup(keyword=keyword)
        data = json.load(open(f'../{data}'))
        data = list(data.values())
    response = distribute_data(data, keyword)
                                
    return response['ResponseMetadata']['HTTPStatusCode']

def distribute_data(response, keyword):
    raw_bucket_name = f'{keyword}-bucket'
    tweet_batches = [{'batch': []} for i in range(10)]
    batch_size = int(len(response)/10)
    remaining = len(response)%10
    batch_num = 0

    for r in response:

        tweet = {
            'tweet_id': r['id'],
            'datestamp': r['date'],
            'timezone': r['timezone'],
            'user_id': r['user_id'],
            'num_retweets': r['nretweets'],
            'num_likes': r['nlikes'],
            'in_reply_to': r['user_rt_id'],
            'text': r['tweet']
        }

        tweet_batches[batch_num]['batch'].append(tweet)
        if len(tweet_batches[batch_num]['batch']) == batch_size:
            if remaining > 0:
                remaining -=1 
                continue
            batch_num += 1

    data_files = [{'batch': []} for _ in range(10)]

    for batch_id in range(10):
        batch = tweet_batches[batch_id]
        raw_file_name = f"{keyword}_batch_{batch_id}.json"
        with open('/tmp/' + raw_file_name, "w") as outfile:
            json.dump(batch, outfile)
        s3.upload_file('/tmp/' + raw_file_name, raw_bucket_name, raw_file_name)
        data_files[batch_id]['batch'] = [raw_bucket_name, raw_file_name]
    

    # step function for activating 10 lambda workers
    response = sfn.list_state_machines()
    state_machine_arn = [sm['stateMachineArn'] 
                        for sm in response['stateMachines'] 
                        if sm['name'] == 'twitter_sm'][0]

    response = sfn.start_sync_execution(
        stateMachineArn=state_machine_arn,
        name='sentiment',
        input=json.dumps(data_files)
    )
    return response


def main(data, user_keyword):
    setup(keyword=user_keyword)
    print(send_data(data, user_keyword))




