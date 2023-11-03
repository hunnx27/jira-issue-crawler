import sys
global JIRA_URL
JIRA_URL = sys.argv[0]
global TOKEN
TOKEN = sys.argv[1]

import requests
global is_print
is_print = False
MAX_RESULTS = 5000

#
# JIRA Issue 정보 취합
#
# Issue 상세 조회 함수
def getIssueDetail(issueMap):
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/issue/{issueMap['key']}",
        headers={"Authorization":f"Bearer {TOKEN}"}    
    )
    #print('[########START####### Detail]')
    #print(response.json())
    detail = response.json()

    id = detail['id']
    key = detail['key']
    self = detail['self']
    projectId = detail['fields']['project']['id']
    projectKey = detail['fields']['project']['key']
    projectName = detail['fields']['project']['name']
    summary = detail['fields']['summary']
    description = detail['fields']['description']
    assigneeName = detail['fields']['assignee']['name'] if detail['fields']['assignee'] != None else None
    assigneeKey = detail['fields']['assignee']['key'] if detail['fields']['assignee'] != None else None
    assigneeEmailAddress = detail['fields']['assignee']['emailAddress'] if detail['fields']['assignee'] != None else None
    assigneeDisplayName = detail['fields']['assignee']['displayName'] if detail['fields']['assignee'] != None else None

    if(is_print):
        print('id :', id)
        print('key :', key)
        print('self :', self)
        print('projectId :', projectId)
        print('projectKey :', projectKey)
        print('projectName :', projectName)
        print('summary :', summary)
        print('description :', description)
        print('assigneeName :', assigneeName)
        print('assigneeKey :', assigneeKey)
        print('assigneeEmailAddress :', assigneeEmailAddress)
        print('assigneeDisplayName :', assigneeDisplayName)

    map = {}
    map['id'] = id
    map['key'] = key
    map['self'] = self
    map['projectId'] = projectId
    map['projectKey'] = projectKey
    map['projectName'] = projectName
    map['summary'] = summary
    map['description'] = description
    map['assigneeName'] = assigneeName
    map['assigneeKey'] = assigneeKey
    map['assigneeEmailAddress'] = assigneeEmailAddress
    map['assigneeDisplayName'] = assigneeDisplayName

    return map


# Issue 전체 검색(5000개씩)
def search(page, maxResults):
    # Issue 전체 검색
    response = requests.get(
        f'{JIRA_URL}/rest/api/2/search',
        headers={"Authorization":f"Bearer {TOKEN}"},
        params={'maxResults':maxResults, 'startAt':page*maxResults}
        )

    total = response.json()['total']
    print('startAt', response.json()['startAt'])
    print('maxResults', maxResults)
    print('total', total)
    #print('issues', response.json()['issues'])
    issues = response.json()['issues']
    print(type(issues))
    newList = []
    for (idx, issue) in enumerate(issues):
        #if idx > 0:
        #    break
        param = {}
        param['key'] = issue['key']

        map = getIssueDetail(param)
        map['issueTypeId'] = issue['fields']['issuetype']['id'] if issue['fields']['issuetype'] != None else None
        map['issueTypeName'] = issue['fields']['issuetype']['name'] if issue['fields']['issuetype'] != None else None
        map['issueTypeDescription'] = issue['fields']['issuetype']['description'] if issue['fields']['issuetype'] != None else None
        map['created'] = issue['fields']['created']
        map['updated'] = issue['fields']['updated']
        map['resolutiondate'] = issue['fields']['resolutiondate']

        newList.append(map)
        if idx%100 == 0:
            print('[',idx,']#########################')

    print(len(newList))
    curPageSize = (page+1) * maxResults
    result = {
        'total': total,
        'maxResults' : maxResults,
        'curPage': page,
        'curPageSize':curPageSize,
        'list': newList
    }
    return result


import pandas as pd
# CSV 저장 함수
def saveCSV(rsList):
    # csv 작업
    df = pd.DataFrame(rsList)
    #print(df)
    df.to_csv('f:\develop_ai\EXTRACT_CSV\jira_issue.csv', encoding='utf-8-sig')


# 일단 첫 호출
rs = search(0, MAX_RESULTS)
total = rs['total']
curPageSize = rs['curPageSize']
print('curPageSize', curPageSize)
print('total : ', total)

rsList = []
rsList.extend(rs['list'])

# Total까지 반복
MAX_ITR = 20
idx = 0
while True:
    if(MAX_ITR <= idx):
        print('맥스 이터레이트 초과')
        break

    print('idx : ', idx)
    curPage = rs['curPage']
    rs = search(curPage+1, MAX_RESULTS)
    rsList.extend(rs['list'])
    curPageSize = rs['curPageSize']
    print('[curPage][curPageSize]', curPage, curPageSize)
    saveCSV(rsList)
    if(total <= curPageSize):
        print('*****전체 저장 완료*****')
        break
    idx = idx+1


print('fianl list len : ',len(rsList))
saveCSV(rsList)