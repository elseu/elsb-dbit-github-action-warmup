#!/usr/bin/env python3.8
import sys
import boto3
import time

asgList = {}

def get_asg_list_instance(asgName):
  asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
  if ('AutoScalingGroups' in asgDescription) and (len(asgDescription['AutoScalingGroups'])>0):
    return asgDescription['AutoScalingGroups'][0]['Instances']
  else :
    return []


## Get params
if len(sys.argv) < 2:
  print("Usage : warmup.py <AsgName1> [<AsgName2> <AsgName2> ....]")
  exit(-1)

## Set Desired Instance to 1 in ASG if not already starter
paramIndice = 1
print("Number of ASG to process : %s" % str(len(sys.argv)-1))
while (paramIndice < len(sys.argv)):
  asgName = sys.argv[paramIndice]
  asgClient = boto3.client('autoscaling')

  if len(get_asg_list_instance(asgName)) == 0:
    print("-- Process ASG %s" % asgName)
    asgClient.update_auto_scaling_group(AutoScalingGroupName=asgName, DesiredCapacity=1)
    asgList[asgName] = "startup"
  else :
    print("-- ASG %s have already running instances -> No start needed" % asgName)
  paramIndice += 1


## Wait instance are running and InService for all ASG
listAsgToWarmup = list(asgList.keys())
numberIter = len(listAsgToWarmup)
print("-- %s ASG To warmup ! " % numberIter)

while numberIter > 0:
  for asgName in listAsgToWarmup:
    instancesList = get_asg_list_instance(asgName)
    if asgList[asgName] == "startup":
      print("-- Wait InService Instance for ASG %s" % asgName)
      if len(instancesList) != 0:
        asgList[asgName] = instancesList[0]
        print("-- Instance for ASG %s is Pending" % asgName)
    else:
      if len(instancesList) == 0:
        print("-- ASG %s warmup failed" % asgName)
        exit(-1)
      asgList[asgName] = instancesList[0]
      if asgList[asgName]['LifecycleState'] == 'InService':
        listAsgToWarmup.remove(asgName)
        print("-- ASG %s warmup ok" % asgName)
  time.sleep(1)
  numberIter = len(listAsgToWarmup)

exit(0)




