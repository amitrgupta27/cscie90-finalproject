import json
import boto3

# Enter the region your instances are in. Include only the region without specifying Availability Zone; e.g.; 'us-east-1'
region = 'us-east-1'
# Enter your instances here: ex. ['X-XXXXXXXX', 'X-XXXXXXXX']
instances = ['i-0e2202d9daf7340e8']

AWSAccessKeyId='secretid'
AWSSecretKey='secretkey'

def lambda_handler(event, context):
    client = boto3.client('ec2', region_name=region, aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey)
    client.start_instances(InstanceIds=instances)
    print ('started your instances: ' + str(instances))
    
    #Get IP addresses of EC2 instances
    #client = boto3.client('ec2')
    instDict=client.describe_instances(
            Filters=[{'Name':'tag:Environment','Values':['Dev']}]
        )
        
    
    hostList=[]
    
    for r in instDict['Reservations']:
        
        for inst in r['Instances']:
            
            hostList.append(inst['PublicIpAddress'])

    #Invoke worker function for each IP address
    client = boto3.client('lambda')
    
    for host in hostList:
        print ("Invoking worker_function on " + host)
        invokeResponse=client.invoke(
            FunctionName='worker_function',
            InvocationType='Event',
            LogType='Tail',
            Payload='{"IP":"'+ host +'"}'
        )
        print ('response is' + str(invokeResponse))

    return{
        'message' : "Trigger function finished"
    }
