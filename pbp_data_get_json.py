#pbp_data_get_json.py
#-*- coding: utf-8 -*-
# main.py

import sys
import os
import urllib2
from bs4 import BeautifulSoup
import json
from checkURL import checkURL
import datetime

excps = {
            0: { 'date': '20160407', 'homeaway': 'LGHT', 'data': [6, 48, 36] },
            1: { 'date': '20160722', 'homeaway': 'WOSK', 'data': [9, 22, 52] },
            2: { 'date': '20100403', 'homeaway': 'LTHT', 'data': [7, 0, 26] },
            3: { 'date': '20100416', 'homeaway': 'WOHH', 'data': [8, 0, 42] }
}
# n회의 A번 텍스트를 B번 뒤 위치로 옮기라
# ex) 6, 48, 36 -> 6회 48번 텍스트를 36번 뒤 - 37번 - 로 바꿀 것

dels = {
            0: { 'date': '20160901', 'homeaway': 'SKWO', 'data': [7, 39] },
}

repls = {
}

adds = {
            0: { 'date': '20100403', 'homeaway': 'LTHT', 'location': [7, 0],
                 'data': {'seqno': 344, 'inn': 7, 'liveText': '7회말 KIA 공격 종료', 'btop': 0, 'textStyle': 8} },
            1: { 'date': '20100413', 'homeaway': 'SKHH', 'location': [8, 63],
                 'data': {'seqno': 370, 'inn': 8, 'liveText': '1루주자 박정권 : 대주자 모창민(으)로 교체', 'btop': 1, 'textStyle': 2} },
            2: { 'date': '20100416', 'homeaway': 'WOHH', 'location': [8, 0],
                 'data': {'seqno': 370, 'inn': 8, 'liveText': '8회말 한화 공격 종료', 'btop': 0, 'textStyle': 8} },
            3: { 'date': '20100416', 'homeaway': 'WOHH', 'location': [8, 0],
                 'data': {'seqno': 370, 'inn': 8, 'liveText': '8회말 한화 공격 종료', 'btop': 0, 'textStyle': 8} }

}
# n회의 A번 텍스트를 B번 위치에 추가해라
# ex) 6, 63 -> 6회 63번 위치에 텍스트 추가, 기존 63번은 64번으로

def findInExcps( gameID ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range( len(excps) ):
        if matchdate.find( excps[i]['date'] ) >= 0:
            if matchhw.find( excps[i]['homeaway'] ) >= 0:
                return int(i)
    return -1

def findInDels( gameID ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range( len(dels) ):
        if matchdate.find( dels[i]['date'] ) >= 0:
            if matchhw.find( dels[i]['homeaway'] ) >= 0:
                return int(i)
    return -1

def delTexts( gameID, js ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range(len(dels)):
        for i in range( len(dels) ):
            if matchdate.find( dels[i]['date'] ) >= 0:
                if matchhw.find( dels[i]['homeaway'] ) >= 0:
                    lis = dels[i]['data']
                    targetInn = lis[0]
                    target = lis[1]
                    rts = js['relayTexts'][str(targetInn)]
                    rts[target:target+1] = []
                    js['relayTexts'][str(targetInn)] = rts

def findInRepls( gameID ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range( len(repls) ):
        if matchdate.find( repls[i]['date'] ) >= 0:
            if matchhw.find( repls[i]['homeaway'] ) >= 0:
                return int(i)
    return -1

def replTexts( gameID, js ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range(len(repls)):
        for i in range( len(repls) ):
            if matchdate.find( repls[i]['date'] ) >= 0:
                if matchhw.find( repls[i]['homeaway'] ) >= 0:
                    lis = repls[i]['location']
                    targetInn = lis[0]
                    target = lis[1]
                    data = repls[i]['data']
                    rts = js['relayTexts'][str(targetInn)]
                    rts[target]['liveText'] = data
                    js['relayTexts'][str(targetInn)] = rts

def findInAdds( gameID ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range( len(adds) ):
        if matchdate.find( adds[i]['date'] ) >= 0:
            if matchhw.find( adds[i]['homeaway'] ) >= 0:
                return int(i)
    return -1

def addTexts( gameID, js ):
    matchdate = gameID[0:8]
    matchhw = gameID[8:12]
    for i in range(len(adds)):
        for i in range( len(adds) ):
            if matchdate.find( adds[i]['date'] ) >= 0:
                if matchhw.find( adds[i]['homeaway'] ) >= 0:
                    lis = adds[i]['location']
                    targetInn = lis[0]
                    target = lis[1]
                    data = adds[i]['data']
                    rts = js['relayTexts'][str(targetInn)]
                    rts[target:] = [data] + rts[target:]
                    js['relayTexts'][str(targetInn)] = rts


def pbp_data_get_json( mon_start, mon_end, year_start, year_end ):
    # set url prefix
    scheduleURL_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="
    relay_prefix = "http://sportsdata.naver.com/ndata//kbo/"

    # make directory
    if not os.path.isdir("./pbp_data"):
        os.mkdir("./pbp_data")
    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print "##################################################"
    print "#######            GET PBP DATA            #######"
    print "##################################################"
    year_max = datetime.datetime.now().year
    for year in range(year_start, year_end+1):
        # make year directory
        if not os.path.isdir("./" + str(year)):
            os.mkdir("./" + str(year))
        os.chdir(str(year))
        # current path : ./pbp_data/YEAR/

        print "  for Year " + str(year) + "... "

        for month in range(mon_start, mon_end+1):
            if not os.path.isdir( str(month) ):
                os.mkdir( str(month) )
            os.chdir( str(month) )
            # current path : ./pbp_data/YEAR/MONTH/

            # clear path
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for file_name in files:
                os.remove( file_name )

            # get URL
            scheduleURL = scheduleURL_prefix + str(month) + "&year=" + str(year)

            # progress bar
            print "    Month " + str(month) + "... "
            sys.stdout.write('\r    [waiting]'),
            sys.stdout.flush()

            # open URL
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            scheduleHTML = urllib2.urlopen(scheduleURL).read()
            soup = BeautifulSoup( scheduleHTML, "lxml" )
            schedule_button = soup.findAll('span', attrs={'class':'td_btn'})

            gameIDs = []
            for btn in schedule_button:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                gameIDs.append( suffix.split('&')[0] )

            done = 0
            mon_file_num = 0
            for gameID in gameIDs:
                if month < 10:
                    relayLink = relay_prefix + str(year) + '/' + '0' + str(month) + '/' + gameID + '.nsd'
                else:
                    relayLink = relay_prefix + str(year) + '/' + str(month) + '/' + gameID + '.nsd'

                if int(gameID[0:4]) > year_max:
                    continue
                if int(gameID[0:4]) < 2010:
                    continue

                if checkURL(relayLink) :
                    mon_file_num += 1

            for gameID in gameIDs:
                pbp_data_filename = gameID[0:13] + '_pbp.json'

                if month < 10:
                    relayLink = relay_prefix + str(year) + '/' + '0' + str(month) + '/' + gameID + '.nsd'
                else:
                    relayLink = relay_prefix + str(year) + '/' + str(month) + '/' + gameID + '.nsd'

                if int(gameID[0:4]) > year_max:
                    continue
                if int(gameID[0:4]) < 2010:
                    continue

                if checkURL(relayLink) :
                    done = done + 1
                    if os.path.isfile( pbp_data_filename ):
                        os.remove( pbp_data_filename )

                    relay = urllib2.urlopen(relayLink).read()
                    text = relay.split("document, ")[1]
                    jsontext = text.split(");")[0]
                    js = json.loads(jsontext, 'utf-8')

                    if findInExcps( gameID ) >= 0:
                        key = findInExcps( gameID )
                        lis = excps[key]['data']
                        targetInn = lis[0]
                        tSrc = lis[1]   # 48
                        tDst = lis[2]   # 36
                        rts = js['relayTexts'][str(targetInn)]
                        if tSrc > tDst:
                            rts[ tDst+1:tSrc+1 ] = [rts[tSrc]]+rts[tDst+1:tSrc]
                        else:
                            rts[ tSrc:tDst+1 ] = rts[tSrc+1:tDst+1] + [rts[tSrc]]
                        js['relayTexts'][str(targetInn)] = rts

                    if findInDels( gameID ) >= 0:
                        delTexts( gameID, js )
                        key = findInDels( gameID )
                        lis = dels[key]['data']
                        targetInn = lis[0]
                        target = lis[1]
                        rts = js['relayTexts'][str(targetInn)]
                        rts[target:target+1] = []
                        js['relayTexts'][str(targetInn)] = rts

                    if findInRepls( gameID ) >= 0:
                        key = findInRepls( gameID )
                        lis = repls[key]['location']
                        targetInn = lis[0]
                        target = lis[1]
                        data = repls[key]['data']
                        rts = js['relayTexts'][str(targetInn)]
                        rts[target]['liveText'] = data
                        js['relayTexts'][str(targetInn)] = rts

                    if findInAdds( gameID ) >= 0:
                        addTexts( gameID, js )

                    with open(pbp_data_filename, 'w') as pbp_data_file:
                        pbp_data_file.write( json.dumps( js, indent = 4) )


                if mon_file_num > 30 :
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, progress_pct*100)),
                    sys.stdout.flush()
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * done + '-' * (mon_file_num - done)
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, float(done)/float(mon_file_num)*100)),
                    sys.stdout.flush()

            sys.stdout.write('\n')
            sys.stdout.flush()
            print '        Downloaded ' + str(done) + ' files'
            os.chdir('..')
            # current path : ./pbp_data/YEAR/
        os.chdir('..')
        # current path : ./pbp_data/
    os.chdir('..')
    # current path : ./
    print "DOWNLOAD PBP DATA DONE."
