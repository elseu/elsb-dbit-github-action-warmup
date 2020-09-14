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
while True:
  asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
  instancesList = asgDescription['AutoScalingGroups'][0]['Instances']

  print("Loop in ASG Instance List")

  if len(instancesList) == 0:
    time.sleep(5)
    continue

  instance = instancesList[0]
  instanceStatus = instance['LifecycleState']

  if instance['LifecycleState'] == 'InService':
    exit(0)
  else:
    time.sleep(5)




