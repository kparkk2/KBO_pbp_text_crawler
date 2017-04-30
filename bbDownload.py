# bbDownload.py
#-*- coding: utf-8 -*-
#(1) get all matchup gameday(text relay broadcast) URL. all match in YEAR/MONTH.
#(2) open URL and parse.

import sys
import time
import json
from urllib.request import urlopen
import os
from bs4 import BeautifulSoup
import re

def bbDownload( mon_start, mon_end, year_start, year_end ):
    # set url prefix
    scheduleURL_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?"
    resultURL_prefix = "http://sports.news.naver.com/gameCenter/gameResult.nhn?category=kbo&gameId="

    # make directory
    if not os.path.isdir("./bb_data"):
        os.mkdir("./bb_data")

    for year in range(year_start, year_end + 1):
        # make year directory
        if not os.path.isdir("./bb_data/" + str(year)):
            os.mkdir("./bb_data/" + str(year))

        for month in range(mon_start, mon_end + 1):
            if not os.path.isdir("./bb_data/" + str(year) + "/" + str(month)):
                os.mkdir("./bb_data/" + str(year) + "/" + str(month))

    os.chdir("./bb_data")
    # current path : ./bb_data/

    print("##################################################")
    print("######        DOWNLOAD BB DATA             #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year " + str(year) + "... ")

        for month in range(mon_start, mon_end + 1):
            os.chdir(str(year) + "/" + str(month))
            # current path : ./bb_data/YEAR/MONTH/

            # get URL
            scheduleURL = scheduleURL_prefix + "month=" + str(month) + "&year=" + str(year)

            # open URL
            print("    Month " + str(month) + "... ")
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            bar_prefix = '    Downloading: '
            print('\r%s[waiting]' % (bar_prefix), end="")

            # '경기결과' 버튼을 찾아서 tag를 모두 리스트에 저장.
            # parser의 자체 딜레이 때문에 과정 별로 5ms 딜레이를 준다.
            scheduleButton = []
            scheduleHTML = urlopen(scheduleURL).read()
            time.sleep(5.0 / 1000.0)
            scheduleSoup = BeautifulSoup(scheduleHTML, "lxml")
            time.sleep(5.0 / 1000.0)
            scheduleButton = scheduleSoup.findAll('span', attrs={'class': 'td_btn'})
            time.sleep(5.0 / 1000.0)

            # '경기결과' 버튼을 찾아서 tag를 모두 리스트에 저장.
            gameIDs = []
            for btn in scheduleButton:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                gameIDs.append(suffix)

            mon_file_num = sum(1 for gameID in gameIDs if int(gameID[:4]) <= 2050)

            # gameID가 있는 게임은 모두 경기 결과가 있는 것으로 판단함
            i = 0

            for gameID in gameIDs:
                if int(gameID[0:4]) > 2050:
                    continue

                resultHTML = urlopen(resultURL_prefix + gameID)

                soup = BeautifulSoup(resultHTML.read(), "lxml")
                script = soup.find('script', text=re.compile('ChartDataClass'))
                json_text = re.search(r'({"teamsInfo":{.*?}}}})', script.string, flags=re.DOTALL).group(1)
                data = json.loads(json_text, 'utf-8')

                bb_data_filename = gameID[0:13] + '_bb_data.json'
                with open(bb_data_filename, 'w') as bb_data_file:
                    json.dump(data, bb_data_file, indent=4)
                bb_data_file.close()
                i += 1

                if mon_file_num > 30:
                    progress_pct = (float(i) / float(mon_file_num))
                    bar = '█' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
                    print('\r%s[%s] %s / %s, %2.1f %%' % (bar_prefix, bar, i, mon_file_num, progress_pct * 100), end="")
                    sys.stdout.flush()
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * i + '-' * (mon_file_num - i)
                    print('\r%s[%s] %s / %s, %2.1f %%' % (
                        bar_prefix, bar, i, mon_file_num, float(i) / float(mon_file_num) * 100), end="")
                    sys.stdout.flush()
            print()
            print('        Downloaded ' + str(i) + ' files')
            os.chdir('../..')
            # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD BB DATA DONE.")