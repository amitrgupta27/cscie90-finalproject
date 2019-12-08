import json
import boto3
import paramiko

# Enter the region your instances are in. Include only the region without specifying Availability Zone; e.g.; 'us-east-1'
#region = 'us-east-1'
# Enter your instances here: ex. ['X-XXXXXXXX', 'X-XXXXXXXX']
#instances = ['i-XXXXXXXX']

def lambda_handler(event, context):

    print(event)
    #Get IP addresses of EC2 instances
    client = boto3.client('ec2')
    instDict=client.describe_instances(
        Filters=[{'Name':'tag:Text-Summarizer','Values':['FinalProject']}]
        )

    hostList=[]
    for r in instDict['Reservations']:
        for inst in r['Instances']:
            hostList.append(inst['PublicIpAddress'])

    print(hostList)
    s3_client = boto3.client('s3')
    #Download private key file from secure S3 bucket
    s3_client.download_file('s3 bucket','file.pem', '/tmp/file.pem')

    k = paramiko.RSAKey.from_private_key_file("/tmp/file.pem")
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host=hostList[0]
    print ("Connecting to " + host)
    conn = c.connect( hostname = host, username = "ec2-user", pkey = k, timeout=10 )
    if conn is None:
         print ("Successfully Authenticated")
    else:
        print("Connection Not Successful")
    print ("Connected to " + host)

    input = event['Text']
    input_str = "\"" + input + "\""
    command_str = f'python3 kmeans.py {input_str}'
    print(command_str)
    commands = [
        command_str
        ]

    for command in commands:
        print ("Executing {}".format(command))
        stdin , stdout, stderr = c.exec_command(command, timeout=120)
        result = stdout.read().decode('ascii')

    return result
