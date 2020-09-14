#!/usr/bin/env python3.8
import sys
import boto3
import time

## Get params
asgName = sys.argv[1]

## Set Desired Instance to 1 in ASG
asgClient = boto3.client('autoscaling')
asgClient.update_auto_scaling_group(AutoScalingGroupName=asgName, DesiredCapacity=1)

#We get first instance of ASG
asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
instancesList = asgDescription['AutoScalingGroups'][0]['Instances']
instance = instancesList[0]


desiredStatus = 'InService'
waitingStatus = 'Pending'
instanceStatus = instance['LifecycleState']

#We wait for inService status
inService = instanceStatus == desiredStatus
while ((not inService) and (waitingStatus in instanceStatus)):
  instanceStatus = instance['LifecycleState']
  inService = instanceStatus == desiredStatus
  time.sleep(10)

if instanceStatus == desiredStatus:
  exit(0)
else:
  exit(1)






