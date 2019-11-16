from phabricator import Phabricator
from collections import OrderedDict
import sys

# TODO: Too slow, add mutiprocessing [~~ 2 min 30 sec] for single user

def getUserPhid(user):
  result = phab.user.query(usernames=[user])
  user_list = []
  for data in result:
    user_list.append(data['phid'])
  return user_list

def getUserRevisionList(username):
  phid = getUserPhid(username)
  constraints = {"authorPHIDs": phid}
  result = phab.differential.revision.search(constraints=constraints)
  diffIDs = []
  for data in result['data']:
    diffIDs.append(data['id'])
  return diffIDs

def getDiffs(revisions):
  diffs = phab.differential.querydiffs(revisionIDs=revisions)
  return diffs

def getLatestDiffID(diffs):
  sortedDiffs = OrderedDict(sorted(diffs.items(), reverse=True))
  keys = list(sortedDiffs.keys())
  return keys[0]

totalplus = 0
totalminus = 0
phab = Phabricator() #Uses config from local ~/.arcrc file
phab.update_interfaces()

username = sys.argv[1]
revisions = getUserRevisionList(username)
diffcount = len(revisions)

for rev in revisions:
  diffs = getDiffs([rev])
  # Get latest diff from given revision
  latestDiff = getLatestDiffID(diffs)
  for fil in diffs[str(latestDiff)]["changes"]:
    totalplus = totalplus + int(fil["addLines"])
    totalminus = totalminus + int(fil["delLines"])

print("Total Diffs Raised: " + str(diffcount))
print("Total Lines Added: " + str(totalplus))
print("Total Lines Removed: " + str(totalminus))
print("Total Lines: " + str(totalplus + totalminus))