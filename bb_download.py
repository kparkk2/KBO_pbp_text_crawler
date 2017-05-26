# bb_download.py
# (1) get all match text relay broadcast URL; all match in YEAR/MONTH.
# (2) open URL and parse.

import json
from urllib.request import urlopen
import os
from bs4 import BeautifulSoup
import re
import sys

def bb_download(mon_start, mon_end, year_start, year_end, lm=None):
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
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)
            if not os.path.isdir("./bb_data/{0}/{1}".format(str(year), mon)):
                os.mkdir("./bb_data/{0}/{1}".format(str(year), mon))

    os.chdir("./bb_data")
    # current path : ./bb_data/

    print("##################################################")
    print("######        DOWNLOAD BB DATA             #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year {0}... ".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)

            os.chdir("{0}/{1}".format(str(year), mon))
            # current path : ./bb_data/YEAR/MONTH/

            # get URL
            schedule_url = "{0}month={1}&year={2}".format(schedule_url_prefix, str(month), str(year))

            # open URL
            print("    Month {0}... ".format(str(month)))
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            bar_prefix = '    Downloading: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            # '경기결과' 버튼을 찾아서 태그를 모두 리스트에 저장.
            schedule_html = urlopen(schedule_url).read()
            schedule_soup = BeautifulSoup(schedule_html, 'lxml')
            schedule_button = schedule_soup.findAll('span', attrs={'class': 'td_btn'})

            # '경기결과' 버튼을 찾아서 태그를 모두 리스트에 저장.
            game_ids = []
            for btn in schedule_button:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                game_ids.append(suffix)

            mon_file_num = sum(1 for game_id in game_ids if int(game_id[:4]) <= 2050)

            # gameID가 있는 게임은 모두 경기 결과가 있는 것으로 판단함
            done = 0

            lm.resetLogHandler()
            lm.setLogPath(os.getcwd() + '/log/')
            lm.setLogFileName('bbDownloadLog.txt')
            lm.cleanLog()
            lm.createLogHandler()

            for game_id in game_ids:
                if int(game_id[0:4]) < 2010:
                    continue
                if int(game_id[0:4]) > 2050:
                    continue

                result_html = urlopen(result_url_prefix + game_id)

                soup = BeautifulSoup(result_html.read(), 'lxml')
                script = soup.find('script', text=re.compile('ChartDataClass'))
                json_text = re.search(r'({"teamsInfo":{.*?}}}})', script.string, flags=re.DOTALL).group(1)

                bb_data_filename = game_id[:12] + '_bb.json'

                if sys.platform == 'win32':
                    data = json.loads(json_text, encoding='iso-8859-1')
                    with open(bb_data_filename, 'w', encoding='utf-8') as bb_data_file:
                        bb_data_file.write(json.dumps(data, indent=4, ensure_ascii=False))
                    bb_data_file.close()
                else:
                    data = json.loads(json_text)
                    with open(bb_data_filename, 'w') as bb_data_file:
                        json.dump(data, bb_data_file, indent=4, ensure_ascii=False)
                    bb_data_file.close()

                done += 1
                lm.log('{} download'.format(game_id))

                if mon_file_num > 30:
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '+' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
                    bar = bar.encode('utf-8').decode('utf-8')
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               progress_pct * 100), end="")
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '+' * done + '-' * (mon_file_num - done)
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               float(done) / float(mon_file_num) * 100), end="")

            print()
            print('        Downloaded {0} files.'.format(str(done)))
            os.chdir('../..')
            # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD BB DATA DONE.")
