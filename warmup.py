#!/usr/bin/env python3.8
import sys
import boto3
import time

asgList = {}

# Get list of instances attached to ASG
def get_asg_list_instance(asgName):
  asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
  if ('AutoScalingGroups' in asgDescription) and (len(asgDescription['AutoScalingGroups'])>0):
    return asgDescription['AutoScalingGroups'][0]['Instances']
  else :
    return []

# Test if deployment is running (Created, Queues, InProgress, Baking)
def deployment_is_terminated(client, codedeploy_app, codedeploy_deployment_group):
  response = client.list_deployments(
    applicationName=codedeploy_app,
    deploymentGroupName=codedeploy_deployment_group,
    includeOnlyStatuses=['Created','Queued','InProgress'])
  return len(response['deployments']) == 0



## Get params and test if we can run warmup
if len(sys.argv) != 4:
  print("Usage : warmup.py \"<AsgName1> [<AsgName2> <AsgName2> ....]\" <CodeDeployApp> <CodeDeployDeploymentGroup>")
  exit(-1)


## Set Desired Instance to 1 in ASG if not already starter
## ASG list is passed with space between each one
list_asg = sys.argv[1].split(' ')

codedeploy_app = sys.argv[2]
codedeploy_deployment_group = sys.argv[3]

codedeployClient = boto3.client('codedeploy')
asgClient = boto3.client('autoscaling')

# For all ASG, we test if instances are already running, if not, we had it to list
print("Number of ASG to process : %s" % str(len(list_asg)))
for asgName in list_asg:
  if len(get_asg_list_instance(asgName)) == 0:
    print("-- Process ASG %s" % asgName)
    asgClient.update_auto_scaling_group(AutoScalingGroupName=asgName, DesiredCapacity=1)
    print("******* Number instance start : %s" % str(len(get_asg_list_instance(asgName))))
    while (get_asg_list_instance(asgName)) == 0:
      print ("***** INSTANCE NOT START : update desired again ------------")
      asgClient.update_auto_scaling_group(AutoScalingGroupName=asgName, DesiredCapacity=1)
    asgList[asgName] = "startup"
  else :
    print("-- ASG %s have already running instances -> No start needed" % asgName)


## Wait instance are running and InService for all ASG (and no codeploy in progress)
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
        print("******* TEST ASG WARMUP -> UPDATE DESIRED")
        asgClient.update_auto_scaling_group(AutoScalingGroupName=asgName, DesiredCapacity=1)
    else:
      if len(instancesList) == 0:
        print("-- ASG %s warmup failed" % asgName)
        exit(-1)
      asgList[asgName] = instancesList[0]
      if asgList[asgName]['LifecycleState'] == 'InService':
        print("-- Instance for ASG %s is InService" % asgName)
        if deployment_is_terminated(codedeployClient, codedeploy_app, codedeploy_deployment_group):
          listAsgToWarmup.remove(asgName)
          print("-- ASG %s warmup ok" % asgName)
        else:
          print("-- Deployement %s is already in progress" % codedeploy_deployment_group)

  time.sleep(5)
  numberIter = len(listAsgToWarmup)

exit(0)




