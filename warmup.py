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
instancesList = []
while len(instancesList) == 0:
  asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
  instancesList = asgDescription['AutoScalingGroups'][0]['Instances']
  time.sleep(5)
  print("Loop in ASG Instance List")

instance = instancesList[0]

desiredStatus = 'InService'
instanceStatus = instance['LifecycleState']

#We wait for inService status
inService = instanceStatus == desiredStatus
while instanceStatus != desiredStatus:
  print(instance)
  time.sleep(10)

if instanceStatus == desiredStatus:
  exit(0)
else:
  exit(1)






