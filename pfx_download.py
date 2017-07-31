# pfx_download.py
# (1) get all match text relay broadcast URL; all match in YEAR/MONTH.
# (2) open URL and parse.

import csv
import math
import datetime
from urllib.request import urlopen
import os
from bs4 import BeautifulSoup
import requests
import collections
import operator

regular_start = {
    '2012': '0407',
    '2013': '0330',
    '2014': '0329',
    '2015': '0328',
    '2016': '0401',
    '2017': '0331'
}

playoff_start = {
    '2012': '1008',
    '2013': '1008',
    '2014': '1019',
    '2015': '1010',
    '2016': '1021',
    '2017': '1010'
}

fieldNames = ['ax', 'ay', 'az', 'ballcount', 'batterName', 'bottomSz',
              'crossPlateX', 'crossPlateY', 'inn', 'pfx_x', 'pfx_z', 'pitchId',
              'pitcherName', 'plateX', 'plateZ', 'speed', 'stance', 'stuff', 't',
              'topSz', 'vx0', 'vy0', 'vz0', 'x0', 'y0', 'z0']


def print_progress(bar_prefix, mon_file_num, done, skipped):
    if mon_file_num > 30:
        progress_pct = (float(done + skipped) / float(mon_file_num))
        bar = '+' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
        print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, (done + skipped), mon_file_num,
                                                   progress_pct * 100), end="")
    elif mon_file_num > 0:
        bar = '+' * (done + skipped) + '-' * (mon_file_num - done - skipped)
        print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, (done + skipped), mon_file_num,
                                                   float(done + skipped) / float(mon_file_num) * 100),
              end="")


def pfx_download(mon_start, mon_end, year_start, year_end, lm=None):
    current_date = datetime.datetime.now().strftime('%Y%m%d')

    # set url prefix
    schedule_url_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?"
    pfx_url = 'http://m.sports.naver.com/ajax/baseball/gamecenter/kbo/pitches.nhn'

    # make directory
    if not os.path.isdir("./pbp_data"):
        os.mkdir("./pbp_data")

    for year in range(year_start, year_end + 1):
        # make year directory
        if not os.path.isdir("./pbp_data/{0}".format(str(year))):
            os.mkdir("./pbp_data/{0}".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)
            if not os.path.isdir("./pbp_data/{0}/{1}".format(str(year), mon)):
                os.mkdir("./pbp_data/{0}/{1}".format(str(year), mon))

    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("######          DOWNLOAD PFX DATA          #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year {0}... ".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)

            os.chdir("{0}/{1}".format(str(year), mon))
            # current path : ./pbp_data/YEAR/MONTH/

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
            skipped = 0

            lm.resetLogHandler()
            lm.setLogPath(os.getcwd() + '/log/')
            lm.setLogFileName('pfxDownloadLog.txt')
            lm.cleanLog()
            lm.createLogHandler()

            for game_id in game_ids:
                if int(game_id[0:4]) < 2010:
                    continue
                if int(game_id[0:4]) > 2050:
                    continue

                if int(regular_start[game_id[:4]]) > int(game_id[4:8]):
                    skipped += 1
                    continue

                if int(playoff_start[game_id[:4]]) <= int(game_id[4:8]):
                    skipped += 1
                    continue

                if int(game_id[:8]) > int(current_date):
                    skipped += 1
                    continue

                pfx_filename = game_id[:13]+'_pfx.csv'

                if os.path.isfile(pfx_filename) and (os.path.getsize(pfx_filename) > 0):
                    done += 1
                    continue

                params = {
                    'gameId': game_id
                }

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Host': 'm.sports.naver.com',
                    'Referer': 'http://m.sports.naver.com/baseball/gamecenter/kbo/index.nhn?&gameId='+game_id+'&tab=relay'
                }

                res = requests.get(pfx_url, params=params, headers=headers)

                pfx = res.json()

                if len(pfx) == 0:
                    lm.bugLog('pfx error in : {}'.format(game_id))
                    skipped += 1
                    continue

                pfx_file = open(pfx_filename, 'w', newline='\n')
                csvwriter = csv.writer(pfx_file)
                csvwriter = csv.DictWriter(pfx_file, delimiter=',',
                                           dialect='excel', fieldnames=fieldNames,
                                           lineterminator='\n')
                csvwriter.writeheader()
                i = 0
                stance = ''
                for p in pfx:
                    p_a = {
                        'ax': p['ax'],
                        'ay': p['ay'],
                        'az': p['az'],
                        'ballcount': p['ballcount'],
                        'batterName': p['batterName'],
                        'bottomSz': p['bottomSz'],
                        'crossPlateX': p['crossPlateX'],
                        'crossPlateY': p['crossPlateY'],
                        'inn': p['inn'],
                        'pfx_x': 0,
                        'pfx_z': 0,
                        'pitchId': p['pitchId'],
                        'pitcherName': p['pitcherName'],
                        'plateX': 0,
                        'plateZ': 0,
                        'speed': p['speed'],
                        'stance': '',
                        'stuff': p['stuff'],
                        't': 0,
                        'topSz': p['topSz'],
                        'vx0': p['vx0'],
                        'vy0': p['vy0'],
                        'vz0': p['vz0'],
                        'x0': p['x0'],
                        'y0': p['y0'],
                        'z0': p['z0']
                    }
                    try:
                        p_a['stance'] = p['stance']
                        stance = p['stance']
                    except KeyError:
                        p_a['stance'] = stance

                    t = (-p['vy0']-math.sqrt(pow(p['vy0'], 2)-2*p['ay']*(p['y0']-p['crossPlateY'])))/p['ay']
                    xp = p['x0']+p['vx0']*t+p['ax']*pow(t, 2)*0.5
                    zp = p['z0']+p['vz0']*t+p['az']*pow(t, 2)*0.5
                    t = round(t, 5)
                    # p_a = p
                    p_a['plateX'] = round(xp, 5)
                    p_a['plateZ'] = round(zp, 5)
                    p_a['t'] = t
                    t40 = (-p['vy0']-math.sqrt(pow(p['vy0'],2)-2*p['ay']*(p['y0']-40)))/p['ay']
                    x40 = p['x0']+p['vx0']*t40+0.5*p['ax']*pow(t40, 2)
                    vx40 = p['vx0']+p['ax']*t40
                    z40 = p['z0'] + p['vz0'] * t40 + 0.5 * p['az'] * pow(t40, 2)
                    vz40 = p['vz0'] + p['az'] * t40
                    th = t-t40
                    x_noair = x40+vx40*th
                    z_noair = z40+vz40*th-0.5*32.174*pow(th, 2)
                    x_break = round(xp - x_noair, 5)
                    z_break = round(zp - z_noair, 5)
                    p_a['pfx_x'] = x_break
                    p_a['pfx_z'] = z_break

                    '''
                    sp = collections.OrderedDict([k, v] for k, v in sorted(p_a.items(), key=operator.itemgetter(0)))

                    if i == 0:
                        csvwriter.writerow(sp.keys())
                        i += 1
                    csvwriter.writerow(sp.values())
                    '''
                    csvwriter.writerow(p_a)
                pfx_file.close()

                # BUGBUG : 20170509 KT-HT 경기 타구 정보 실종
                # 생략

                done += 1
                lm.log('{} download'.format(game_id))

                print_progress(bar_prefix, mon_file_num, done, skipped)
            print_progress(bar_prefix, mon_file_num, done, skipped)
            print()
            print('        Downloaded {0} files.'.format(str(done)))
            print('        (Skipped {0} files)'.format(str(skipped)))
            os.chdir('../..')
            # current path : ./pbp_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD PFX DATA DONE.")
