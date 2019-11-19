# Phabulous

- This script fetches, diff stats from Phabricator given the username of the person.
  - Diff raised count
  - Total lines added
  - Total lines removed
  - Total lines changed(added or removed)

- How to Run
  - python3 script.py username startDate endDate
  - All fields are necessary
  - Date Format : '%Y-%m-%d'
  - Leave date as empty string("") if not required

- Examples:
  - python3 script.py dragonslayer "" "" (Fetches summary of all diffs of user dragonslayer)
  - python3 script.py dragonslayer "2019-11-01" "" (Fetches summary of all diffs created after 1st Nov 2019 of user dragonslayer)
  - python3 script.py dragonslayer "" "2019-11-11" (Fetches summary of all diffs created before 11th Nov 2019 of user dragonslayer)
  - python3 script.py dragonslayer "2019-11-01" "2019-11-01" (Fetches summary of all diffs created between 1st and 11th Nov 2019 of user dragonslayer)
