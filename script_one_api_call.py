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

def getLatestDiffIDs(diffs):
  sortedDiffs = OrderedDict(sorted(diffs.items(), key=lambda x: int(x[0]), reverse=True))
  marked = {}
  keys = []
  for key, value in sortedDiffs.items():
    if value['revisionID'] in marked:
      continue
    else:
      keys.append(key)
      marked[value['revisionID']] = 1
  return keys

def processRevisions(revisions, shared_dict):
  allDiffs = getDiffs(revisions)              #Get all diffs from all revision
  latestDiffIDs = getLatestDiffIDs(allDiffs)  #Get latest diffs from all revision

  for latestDiffID in latestDiffIDs:
    for changedFile in allDiffs[latestDiffID]["changes"]:
      shared_dict["addLines"] = shared_dict["addLines"] + int(changedFile["addLines"])
      shared_dict["delLines"] = shared_dict["delLines"] + int(changedFile["delLines"])

def getUserDiffHistory(username, startDate = "", endDate = ""):
  revisions = getUserRevisionList(username, getEpochTime(startDate), getEpochTime(endDate))
  diffcount = len(revisions)

  shared_dict = {}
  shared_dict["addLines"] = 0
  shared_dict["delLines"] = 0

  processRevisions(revisions, shared_dict)

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