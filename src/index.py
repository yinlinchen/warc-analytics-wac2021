import json
import urllib.parse
import boto3
import argparse
import os
import sys
import time
import uuid
from datetime import datetime

from botocore.compat import total_seconds

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):

    inputFileName = ""
    bucketName = ""

    for record in event['Records']:
      bucketName = record['s3']['bucket']['name']
      inputFileName = record['s3']['object']['key']

    try:

        response = s3.get_object(Bucket=bucketName, Key=inputFileName)
        print("CONTENT TYPE: " + response['ContentType'])
        filecontent = response['Body'].read().decode('utf-8')
        content = json.loads(filecontent)
        
        region_name = content['region']
        warc_filename = content["WARC_FILENAME"]
        warc_URL = content["WARC_URL"]

        batch = boto3.client(
            service_name='batch',
            region_name=region_name,
            endpoint_url='https://batch.' + region_name + '.amazonaws.com')

        cloudwatch = boto3.client(
            service_name='logs',
            region_name=region_name,
            endpoint_url='https://logs.' + region_name + '.amazonaws.com')

        spin = ['-', '/', '|', '\\', '-', '/', '|', '\\']
        logGroupName = '/aws/batch/job'

        jobName = 'iipc-' + uuid.uuid4().hex
        jobQueue = content['jobQueue']
        jobDefinition = content['jobDefinition']
        command = []
        command.append('/notebooks/setup.sh')
        wait = None

        envlist = createEnvList(warc_filename, warc_URL)

        submitJobResponse = batch.submit_job(
            jobName=jobName,
            jobQueue=jobQueue,
            jobDefinition=jobDefinition,
            containerOverrides={
                'command': command,
                'environment': envlist
            }
        )

        jobId = submitJobResponse['jobId']
        print(
            'Submitted job [%s - %s] to the job queue [%s]' %
            (jobName, jobId, jobQueue))

        spinner = 0
        running = False
        startTime = 0

        while wait:
            time.sleep(1)
            describeJobsResponse = batch.describe_jobs(jobs=[jobId])
            status = describeJobsResponse['jobs'][0]['status']
            if status == 'SUCCEEDED' or status == 'FAILED':
                print('%s' % ('=' * 80))
                print('Job [%s - %s] %s' % (jobName, jobId, status))
                break
            elif status == 'RUNNING':
                logStreamName = getLogStream(logGroupName, jobName, jobId)
                if not running and logStreamName:
                    running = True
                    print('\rJob [%s - %s] is RUNNING.' % (jobName, jobId))
                    print('Output [%s]:\n %s' % (logStreamName, '=' * 80))
                if logStreamName:
                    startTime = printLogs(
                        logGroupName, logStreamName, startTime) + 1
            else:
                print('\rJob [%s - %s] is %-9s... %s' %
                      (jobName, jobId, status, spin[spinner %
                                                    len(spin)]), sys.stdout.flush())
                spinner += 1

        return "Job executed."
    except Exception as e:
        print(e)
        raise e


def printLogs(logGroupName, logStreamName, startTime):
    kwargs = {'logGroupName': logGroupName,
              'logStreamName': logStreamName,
              'startTime': startTime,
              'startFromHead': True}

    lastTimestamp = 0
    while True:
        logEvents = cloudwatch.get_log_events(**kwargs)

        for event in logEvents['events']:
            lastTimestamp = event['timestamp']
            timestamp = datetime.utcfromtimestamp(
                lastTimestamp / 1000.0).isoformat()
            print('[%s] %s' %
                  ((timestamp + ".000")[:23] + 'Z', event['message']))

        nextToken = logEvents['nextForwardToken']
        if nextToken and kwargs.get('nextToken') != nextToken:
            kwargs['nextToken'] = nextToken
        else:
            break
    return lastTimestamp


def getLogStream(logGroupName, jobName, jobId):
    response = cloudwatch.describe_log_streams(
        logGroupName=logGroupName,
        logStreamNamePrefix=jobName + '/' + jobId
    )
    logStreams = response['logStreams']
    if not logStreams:
        return ''
    else:
        return logStreams[0]['logStreamName']


def nowInMillis():
    endTime = long(total_seconds(
        datetime.utcnow() - datetime(1970, 1, 1))) * 1000
    return endTime


def createEnvList(warc_filename, warc_URL):

    envlist = []
    warcFilename = {'name': 'WARC_FILENAME', 'value': warc_filename}
    envlist.append(warcFilename)
    warcURL = {'name': 'WARC_URL', 'value': warc_URL}
    envlist.append(warcURL)

    return envlist
