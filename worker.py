import json
import boto3
import paramiko



def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    #Download private key file from secure S3 bucket
    s3_client.download_file('s3-bucket','file.pem', '/tmp/file.pem')

    k = paramiko.RSAKey.from_private_key_file("/tmp/file.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host=event['IP']
    print ("Connecting to " + host)
    c.connect( hostname = host, username = "ec2-user", pkey = k )
    print ("Connected to " + host)

    commands = [
        "aws s3 cp s3://cscie90-finalproject-inputdata/Reviews.csv --region us-east-1 /home/ec2-user/Reviews.csv",
        "python3 /home/ec2-user/kmeans.py",
        "aws s3 cp /home/ec2-user/top_500_summary.csv s3://cscie90-finalproject-results/summary.csv",
        "rm /home/ec2-user/top_500_summary.csv"
        ]

    for command in commands:
        print ("Executing {}".format(command))
        stdin , stdout, stderr = c.exec_command(command)
        print (stdout.read())
        print (stderr.read())

    return
    {
        'message' : "Script execution completed. See Cloudwatch logs for complete output"
    }
    