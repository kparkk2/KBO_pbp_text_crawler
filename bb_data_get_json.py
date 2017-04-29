# bb_data_get_json.py
#-*- coding: utf-8 -*-
#(1) get all matchup gameday(text relay broadcast) URL. all match in YEAR/MONTH.
#(2) open URL and parse.

import sys
import time
import json
import urllib2
import os
from bs4 import BeautifulSoup

def bb_data_get_json( mon_start, mon_end, year_start, year_end ):
    # set url prefix
    scheduleURL_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="
    resultURL_prefix = "http://sports.news.naver.com/gameCenter/gameResult.nhn?category=kbo&gameId="

    # make directory
    if not os.path.isdir("./bb_data"):
        os.mkdir("./bb_data")
    os.chdir("./bb_data")
    # current path : ./bb_data/

    print "##################################################"
    print "######        DOWNLOAD BB DATA             #######"
    print "##################################################"

    for year in range(year_start, year_end+1):
        # make year directory
        if not os.path.isdir("./" + str(year)):
            os.mkdir("./" + str(year))
        os.chdir(str(year))
        # current path : ./bb_data/YEAR/

        print "  for Year " + str(year) + "... "

        for month in range(mon_start, mon_end+1):
            if not os.path.isdir( str(month) ):
                os.mkdir( str(month) )
            os.chdir( str(month) )
            # current path : ./bb_data/YEAR/MONTH/

            # get URL
            scheduleURL = scheduleURL_prefix + str(month) + "&year=" + str(year)

            # open URL
            print "    Month " + str(month) + "... "
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            bar_prefix = '    Downloading: '
            sys.stdout.write('\r%s[waiting]' % (bar_prefix)),
            sys.stdout.flush()

            scheduleButton = []
            scheduleHTML = urllib2.urlopen( scheduleURL ).read()
            time.sleep(300.0/1000.0)
            scheduleSoup = BeautifulSoup( scheduleHTML, "lxml" )
            time.sleep(500.0/1000.0)
            scheduleButton = scheduleSoup.findAll('span', attrs={'class':'td_btn'})
            time.sleep(300.0/1000.0)

            gameIDs = []
            for btn in scheduleButton:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                gameIDs.append( suffix.split('&')[0] )

            mon_file_num = 0

            for gameID in gameIDs:
                if int(gameID[0:4]) > 2050:
                    continue
                else:
                    mon_file_num += 1
            # gameID가 있는 게임은 모두 경기 결과가 있는 것으로 판단함
            i = 0

            for gameID in gameIDs:
                if int(gameID[0:4]) > 2050:
                    continue
                resultURL = resultURL_prefix + gameID

                resultHTML = urllib2.urlopen( resultURL )
                with open( 'temp.html', 'w') as doc:
                    doc.write( resultHTML.read() )

                with open( 'temp.html', 'r' ) as doc:
                    lines = doc.readlines()

                    js = []

                    for line in lines:
                        if line.find("ballsInfo\"") > 0:
                            l = line.split(' : ')
                            data = l[len(l) - 1]
                            jsdata = data[0:len(data)-2]

                            # get match's ball data
                            js = json.loads( jsdata, 'utf-8')
                            break

                    bb_data_filename = gameID[0:13] + '_bb_data.json'
                    with open( bb_data_filename, 'w' ) as bb_data_file:
                        json.dump( js, bb_data_file, indent = 4 )
                    bb_data_file.close()
                    i += 1

                    if mon_file_num > 30 :
                        progress_pct = (float(i) / float(mon_file_num))
                        bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                        sys.stdout.write('\r%s[%s] %s / %s, %2.1f %%' % (bar_prefix, bar, i, mon_file_num, progress_pct*100)),
                        sys.stdout.flush()
                    elif mon_file_num == 0:
                        mon_file_num = 0
                        # do nothing
                    else:
                        bar = '█' * i + '-' * (mon_file_num - i)
                        sys.stdout.write('\r%s[%s] %s / %s, %2.1f %%' % (bar_prefix, bar, i, mon_file_num, float(i)/float(mon_file_num)*100)),
                        sys.stdout.flush()
                doc.close()
                os.remove( 'temp.html' )

            sys.stdout.write('\n')
            sys.stdout.flush()
            print '        Downloaded ' + str(i) + ' files'
            os.chdir('..')
            # current path : ./bb_data/YEAR/
        os.chdir('..')
        # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print "DOWNLOAD BB DATA DONE."
