import json
import boto3

# Enter the region your instances are in. Include only the region without specifying Availability Zone; e.g.; 'us-east-1'
region = 'us-east-1'
instances = ['X-XXXXXXXXX']

AWSAccessKeyId='secretId'
AWSSecretKey='secretKey'

def lambda_handler(event, context):
    
    client = boto3.client('ec2', region_name=region, aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey)
    client.stop_instances(InstanceIds=instances)
    print ('stopped your instances: ' + str(instances))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully stopped EC2 from stopEC2 Lambda')
    }
