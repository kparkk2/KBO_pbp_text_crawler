# bbDownload.py
# (1) get all matchup gameday(text relay broadcast) URL. all match in YEAR/MONTH.
# (2) open URL and parse.

import time
import json
from urllib.request import urlopen
import os
from bs4 import BeautifulSoup
import re


def bbDownload(mon_start, mon_end, year_start, year_end):
    # set url prefix
    schedule_url_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?"
    result_url_prefix = "http://sports.news.naver.com/gameCenter/gameResult.nhn?category=kbo&gameId="

    # make directory
    if not os.path.isdir("./bb_data"):
        os.mkdir("./bb_data")

    for year in range(year_start, year_end + 1):
        # make year directory
        if not os.path.isdir("./bb_data/{0}".format(str(year))):
            os.mkdir("./bb_data/{0}".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if not os.path.isdir("./bb_data/{0}/{1}".format(str(year), str(month))):
                os.mkdir("./bb_data/{0}/{1}".format(str(year), str(month)))

    os.chdir("./bb_data")
    # current path : ./bb_data/

    print("##################################################")
    print("######        DOWNLOAD BB DATA             #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year {0}... ".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            os.chdir("{0}/{1}".format(str(year), str(month)))
            # current path : ./bb_data/YEAR/MONTH/

            # get URL
            schedule_url = schedule_url_prefix + "month=" + str(month) + "&year=" + str(year)

            # open URL
            print("    Month {0}... ".format(str(month)))
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            bar_prefix = '    Downloading: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            # '경기결과' 버튼을 찾아서 tag를 모두 리스트에 저장.
            # parser의 자체 딜레이 때문에 과정 별로 5ms 딜레이를 준다.
            # schedule_button = []
            schedule_html = urlopen(schedule_url).read()
            time.sleep(5.0 / 1000.0)
            schedule_soup = BeautifulSoup(schedule_html, 'lxml')
            time.sleep(5.0 / 1000.0)
            schedule_button = schedule_soup.findAll('span', attrs={'class': 'td_btn'})
            time.sleep(5.0 / 1000.0)

            # '경기결과' 버튼을 찾아서 tag를 모두 리스트에 저장.
            gameIDs = []
            for btn in schedule_button:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                gameIDs.append(suffix)

            mon_file_num = sum(1 for gameID in gameIDs if int(gameID[:4]) <= 2050)

            # gameID가 있는 게임은 모두 경기 결과가 있는 것으로 판단함
            done = 0

            for gameID in gameIDs:
                if int(gameID[0:4]) < 2010:
                    continue
                if int(gameID[0:4]) > 2050:
                    continue

                result_html = urlopen(result_url_prefix + gameID)

                soup = BeautifulSoup(result_html.read(), "lxml")
                script = soup.find('script', text=re.compile('ChartDataClass'))
                json_text = re.search(r'({"teamsInfo":{.*?}}}})', script.string, flags=re.DOTALL).group(1)
                data = json.loads(json_text, 'utf-8')

                bb_data_filename = gameID[0:13] + '_bb_data.json'
                with open(bb_data_filename, 'w') as bb_data_file:
                    json.dump(data, bb_data_file, indent=4)
                bb_data_file.close()
                done += 1

                if mon_file_num > 30:
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '█' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               progress_pct * 100), end="")
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * done + '-' * (mon_file_num - done)
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               float(done) / float(mon_file_num) * 100), end="")

            print()
            print('        Downloaded {0} files.'.format(str(done)))
            os.chdir('../..')
            # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD BB DATA DONE.")
