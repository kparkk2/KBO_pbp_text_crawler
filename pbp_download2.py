# pbp_download.py


import os
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import requests
import logManager

from utils import print_progress
from utils import check_url


regular_start = {
    '2008': '0329',
    '2009': '0404',
    '2010': '0327',
    '2011': '0402',
    '2012': '0407',
    '2013': '0330',
    '2014': '0329',
    '2015': '0328',
    '2016': '0401',
    '2017': '0331'
}

playoff_start = {
    '2008': '1008',
    '2009': '0920',
    '2010': '1005',
    '2011': '1008',
    '2012': '1008',
    '2013': '1008',
    '2014': '1019',
    '2015': '1010',
    '2016': '1021',
    '2017': '1010'
}


def get_game_ids(args):
    # set url prefix
    timetable_url = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="

    # parse arguments
    mon_start = args[0]
    mon_end = args[1]
    year_start = args[2]
    year_end = args[3]

    # get game ids
    game_ids = {}

    for year in range(year_start, year_end + 1):
        year_ids = {}
        month_ids = []

        for month in range(mon_start, mon_end + 1):
            timetable = timetable_url + '{}&year={}'.format(str(month), str(year))

            table_page = urlopen(timetable).read()
            soup = BeautifulSoup(table_page, 'lxml')
            buttons = soup.findAll('span', attrs={'class': 'td_btn'})

            for btn in buttons:
                address = btn.a['href']
                game_id = address.split('gameId=')[1]
                month_ids.append(game_id)

            year_ids[month] = month_ids

        game_ids[year] = year_ids

    return game_ids


def download_relay(args, lm=None):
    # return True or False
    relay_url = 'http://m.sports.naver.com/ajax/baseball/gamecenter/kbo/relayText.nhn?gameId='

    game_ids = get_game_ids(args)
    if (game_ids is None) or (len(game_ids) == 0):
        print('no game ids')
        print('args: {}'.format(args))
        if lm is not None:
            lm.log('no game ids')
            lm.log('args: {}'.format(args))
        return False

    if lm is not None:
        lm.resetLogHandler()
        lm.setLogPath(os.getcwd())
        lm.setLogFileName('relay_download_log.txt')
        lm.cleanLog()
        lm.createLogHandler()
        lm.log('---- Relay Text Download Log ----')

    if not os.path.isdir('pbp_data'):
        os.mkdir('pbp_data')
    os.chdir('pbp_data')
    # path: pbp_data

    for year in game_ids.keys():
        if len(game_ids[year]) == 0:
            print('month id is empty')
            print('args: {}'.format(args))
            if lm is not None:
                lm.log('month id is empty')
                lm.log('args : {}'.format(args))
            return False

        if not os.path.isdir(str(year)):
            os.mkdir(str(year))
        os.chdir(str(year))
        # path: pbp_data/year

        for month in game_ids[year].keys():
            if len(game_ids[year][month]) == 0:
                print('month id is empty')
                print('args: {}'.format(args))
                if lm is not None:
                    lm.log('month id is empty')
                    lm.log('args : {}'.format(args))
                return False

            if not os.path.isdir(str(month)):
                os.mkdir(str(month))
            os.chdir(str(month))
            # path: pbp_data/year/month

            # download
            done = 0
            skipped = 0
            for game_id in game_ids[year][month]:
                if int(game_id[4:8]) < int(regular_start[game_id[:4]]):
                    skipped += 1
                    continue
                if int(game_id[4:8]) >= int(playoff_start[game_id[:4]]):
                    skipped += 1
                    continue

                if not check_url(relay_url + game_id):
                    skipped += 1
                    if lm is not None:
                        lm.log('URL error : {}'.format(game_id))
                    continue

                if (os.path.isfile(game_id+'.json')) and\
                        (os.path.getsize(game_id+'.json') > 0):
                    done += 1
                    if lm is not None:
                        lm.log('File Duplicate : {}'.format(game_id))
                    continue

                params = {
                    'gameId': game_id
                }

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Host': 'm.sports.naver.com',
                    'Referer': 'http://m.sports.naver.com/baseball/gamecenter/kbo/index.nhn?&gameId=' + game_id + '&tab=relay'
                }

                res = requests.get(relay_url + game_id, params=params, headers=headers)

                if res is not None:
                    js = res.json()
                    fp = open(game_id + '.json', 'w', encoding='utf-8', newline='\n')
                    json.dump(js, fp, ensure_ascii=False, indent=4)
                    fp.close()
                    done += 1
                else:
                    skipped += 1
                    if lm is not None:
                        lm.log('Cannot get response : {}'.format(game_id))

                print_progress('    Downloading: ', len(game_ids[year][month]), done, skipped)

            # download done
            print('        Downloaded {} files'.format(done))
            print('        (Skipped {} files)'.format(skipped))

            os.chdir('..')
            # path: pbp_data/year
        # months done
        os.chdir('..')
        # path: pbp_data/
    # years done
    os.chdir('..')
    # path: root
    return True


if __name__ == '__main__':
    args = [8, 8, 2017, 2017]
    lm = logManager.LogManager()
    download_relay(args, lm)

    lm.killLogManager()