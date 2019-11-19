from phabricator import Phabricator
from collections import OrderedDict
from multiprocessing import Process
from multiprocessing import Manager
import os
import time
import sys

# TODO: Too slow, add mutiprocessing [~~ 2 min 30 sec] for single user
# Time reduced to [~~ 20 sec]

def getUserPhid(user):
  result = phab.user.query(usernames=[user])
  user_list = []
  for data in result:
    user_list.append(data['phid'])
  return user_list

def getEpochTime(t):
  pattern = '%Y-%m-%d'
  try:
    return int(time.mktime(time.strptime(t, pattern)))
  except ValueError:
    return 0

def getUserRevisionList(username, startDate, endDate):
  phid = getUserPhid(username)

  constraints = {}
  if startDate != 0 and endDate != 0:
    constraints = {"authorPHIDs": phid, "createdStart": startDate, "createdEnd": endDate}
  elif startDate != 0:
    constraints = {"authorPHIDs": phid, "createdStart": startDate}
  elif endDate != 0:
    constraints = {"authorPHIDs": phid, "createdEnd": endDate}
  else:
    constraints = {"authorPHIDs": phid}

  return getRevisionsWithConstraints(constraints)

def getRevisionsWithConstraints(constraints):
  diffIDs = []
  after = None
  for i in range(0, 1000, 100):
    result = phab.differential.revision.search(constraints=constraints, order='newest', after=after, limit=100)
    after = result['cursor']['after']
    # print(len(result['data']))
    for data in result['data']:
      diffIDs.append(data['id'])

    if after == None:
      break

  return diffIDs

def getDiffs(revisions):
  diffs = phab.differential.querydiffs(revisionIDs=revisions)
  return diffs

def getLatestDiffID(diffs):
  sortedDiffs = OrderedDict(sorted(diffs.items(), reverse=True))
  keys = list(sortedDiffs.keys())
  return keys[0]

# def process_info(title):
#   print(title)
#   print('module name:', __name__)
#   print('parent process:', os.getppid())
#   print('process id:', os.getpid())

def processLatestDiff(rev, shared_dict):
  # process_info(rev)
  allDiffs = getDiffs([rev])                #Get all diffs from current revision
  latestDiffID = getLatestDiffID(allDiffs)  #Get latest diff from current revision
  for changedFile in allDiffs[str(latestDiffID)]["changes"]:
    shared_dict["addLines"] = shared_dict["addLines"] + int(changedFile["addLines"])
    shared_dict["delLines"] = shared_dict["delLines"] + int(changedFile["delLines"])

def getUserDiffHistory(username, startDate = "", endDate = ""):
  revisions = getUserRevisionList(username, getEpochTime(startDate), getEpochTime(endDate))
  diffcount = len(revisions)

  processes = []
  manager = Manager()
  shared_dict = manager.dict()
  shared_dict["addLines"] = 0
  shared_dict["delLines"] = 0

  for rev in revisions:
    p = Process(target = processLatestDiff, args = (rev, shared_dict))
    p.start()
    processes.append(p)

  for p in processes:
    p.join()

  print("Total Diffs Raised: " + str(diffcount) + " [" + ','.join(map(str,revisions)) + "]")
  print("Total Lines Added: " + str(shared_dict["addLines"]))
  print("Total Lines Removed: " + str(shared_dict["delLines"]))
  print("Total Lines: " + str(shared_dict["addLines"] + shared_dict["delLines"]))

phab = Phabricator() #Uses config from local ~/.arcrc file
phab.update_interfaces()

username = sys.argv[1]
startDate = sys.argv[2]
endDate = sys.argv[3]
getUserDiffHistory(username, startDate, endDate)