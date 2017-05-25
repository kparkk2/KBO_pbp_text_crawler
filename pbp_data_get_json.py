# pbp_data_get_json.py

import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import time
import re
import http.client
from urllib.parse import urlparse


def checkurl(url):
    p = urlparse(url)
    conn = http.client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def pbp_data_get_json(mon_start, mon_end, year_start, year_end):
    # set url prefix
    schedule_url_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="
    relay_prefix = "http://sportsdata.naver.com/ndata/kbo/"

    # make directory
    if not os.path.isdir("./pbp_data"):
        os.mkdir("./pbp_data")

    for year in range(year_start, year_end + 1):
        # make year directory
        if not os.path.isdir("./pbp_data/" + str(year)):
            os.mkdir("./pbp_data/" + str(year))

        for month in range(mon_start, mon_end + 1):
            if not os.path.isdir("./pbp_data/" + str(year) + "/" + str(month)):
                os.mkdir("./pbp_data/" + str(year) + "/" + str(month))

    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("#######            GET PBP DATA            #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year " + str(year) + "... ")

        for month in range(mon_start, mon_end + 1):
            os.chdir(str(year) + "/" + str(month))
            # current path : ./pbp_data/YEAR/MONTH/

            # get URL
            schedule_url = schedule_url_prefix + str(month) + "&year=" + str(year)

            # progress bar
            print("    Month " + str(month) + "... ")
            bar_prefix = '    Downloading: '
            print('\r%s[waiting]' % bar_prefix, end="")

            # open URL
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year

            # '경기결과' 버튼을 찾아서 tag를 모두 리스트에 저장.
            # parser의 자체 딜레이 때문에 과정 별로 5ms 딜레이를 준다.
            # schedule_button = []
            schedule_html = urlopen(schedule_url).read()
            time.sleep(5.0 / 1000.0)
            schedule_soup = BeautifulSoup(schedule_html, "lxml")
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
            # 중계 텍스트는 nsd파일이 있는 경우만 count
            # 이를 위해 checkurl 함수를 사용
            # done + skipped = mon_file_num
            done = 0
            skipped = 0

            for gameID in gameIDs:
                relay_link = relay_prefix + gameID[:4] + '/' + gameID[4:6] + '/' \
                            + gameID + '.nsd'

                if int(gameID[0:4]) < 2010:
                    continue
                if int(gameID[0:4]) > 2050:
                    continue

                if not checkurl(relay_link):
                    skipped = skipped + 1
                    continue
                else:
                    relay_html = urlopen(relay_link)

                    soup = BeautifulSoup(relay_html.read(), "lxml")
                    script = soup.find('script', text=re.compile('sportscallback_relay'))
                    json_text = re.search(r'({"gameInfo":{.*?}}},.*?}}})', script.string, flags=re.DOTALL).group(1)
                    data = json.loads(json_text)

                    pbp_data_filename = gameID[0:13] + '_pbp.json'
                    with open(pbp_data_filename, 'w') as pbp_data_file:
                        json.dump(data, pbp_data_file, indent=4, ensure_ascii=False)
                    pbp_data_file.close()
                    done = done + 1

                if mon_file_num > 30:
                    progress_pct = (float(done + skipped) / float(mon_file_num))
                    bar = '█' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
                    print('\r%s[%s] %s / %s, %2.1f %%' % (
                        bar_prefix, bar, (done + skipped), mon_file_num, progress_pct * 100), end="")
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing; dummy code
                else:
                    bar = '█' * (done + skipped) + '-' * (mon_file_num - done - skipped)
                    print('\r%s[%s] %s / %s, %2.1f %%' % (
                        bar_prefix, bar, (done + skipped), mon_file_num,
                        float(done + skipped) / float(mon_file_num) * 100), end="")
            print()
            print('        Downloaded ' + str(done) + ' files')
            print('        (Skipped ' + str(skipped) + ' files)')
            os.chdir('../..')
            # current path : ./pbp_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD PBP DATA DONE.")
