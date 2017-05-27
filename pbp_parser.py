# pbp_parser.py

import os
import json
import sys
import csv
from collections import OrderedDict
import errorManager as em

'''
pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수", "좌중간", "우중간"]
'''
pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "지명타자", "대타", "대주자"]


res_string = ["안타", "2루타", "3루타", "홈런", "실책", "땅볼",
              "뜬공", "희생플라이", "희생번트", "야수선택", "삼진",
              "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타"]

csv_header = '"date","inn","batterName","pitcherName",' \
             '"batterTeam","pitcherTeam","actual_result","result",' \
             '"gx","gy","pos1","pos2","pos3",' \
             '"pos4","pos5","pos6","pos7","pos8","pos9"\n'

fieldNames = ['date', 'batterName', 'pitcherName', 'inn',
              'gx', 'gy', 'fielder_position', 'actual_result',
              'result', 'batterTeam', 'pitcherTeam', 'seqno']

positions = dict(enumerate(pos_string))
results = dict(enumerate(res_string))


find_position = {
    '투': '투수',
    '포': '포수',
    '一': '1루수',
    '二': '2루수',
    '三': '3루수',
    '유': '유격수',
    '좌': '좌익수',
    '중': '중견수',
    '우': '우익수',
    '지': '지명타자',
    '교': '교체'
}


def pbp_parser(mon_start, mon_end, year_start, year_end, lm=None):
    if not os.path.isdir("./pbp_data"):
        print("DOWNLOAD DATA FIRST")
        exit(1)
    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("###### CONVERT PBP DATA(JSON) TO CSV FORMAT ######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year " + str(year) + "...")

        if not os.path.isdir('./{0}'.format(str(year))):
            print(os.getcwd())
            print("DOWNLOAD YEAR {0} DATA FIRST".format(str(year)))
            continue

        for month in range(mon_start, mon_end + 1):
            print("  for Month {0}...".format(str(month)))

            if month == mon_start:
                if sys.platform == 'win32':
                    csv_year = open("{0}/{1}.csv".format(str(year), str(year)), 'w',
                                    encoding='cp949')
                else:
                    csv_year = open("{0}/{1}.csv".format(str(year), str(year)), 'w',
                                    encoding='utf-8')
                csv_year.write(csv_header)

            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)
            if not os.path.isdir('./{0}/{1}'.format(str(year), mon)):
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                continue

            os.chdir('./{0}/{1}'.format(str(year), mon))
            # current path : ./pbp_data/YEAR/MONTH/

            # 파일 끝에 'pbp.json'이 붙고 사이즈 512byte 이상인 파일만 체크
            pbpfiles = [f for f in os.listdir('.') if (os.path.isfile(f) and
                                                       (f.find('pbp.json') > 0) and
                                                       (os.path.getsize(f) > 512))]
            # 파일 끝에 'pbp.json'이 붙고 사이즈 512byte 이상인 파일만 체크
            lineupfiles = [f for f in os.listdir('.') if (os.path.isfile(f) and
                                                          (f.find('lineup.json') > 0) and
                                                          (os.path.getsize(f) > 512))]

            mon_file_num = len(pbpfiles)

            if not mon_file_num > 0:
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                os.chdir('../../')
                # current path : ./pbp_data/
                continue

            if not len(pbpfiles) == len(lineupfiles):
                print(os.getcwd())
                print("LINEUP FILES != PBP FILES COUNT - MONTH{}".format(str(month)))
                os.chdir('../../')
                # current path : ./pbp_data/
                continue

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            if not os.path.isdir("./csv"):
                os.mkdir("./csv")

            csv_month_name = "./{0}_{1}.csv".format(str(year), mon)

            if sys.platform == 'win32':
                csv_month = open(csv_month_name, 'w', encoding='cp949')
            else:
                csv_month = open(csv_month_name, 'w', encoding='utf-8')
            csv_month.write(csv_header)

            # write csv file for year
            # write csv file for month
            # csv column 목록
            # 날짜, 이닝+초말, 타자이름, 투수이름, 타자팀, 투수팀, 결과1, 결과2(상세), gx, gy, 포지션1-9

            # bb json 파일에서 매칭되는 목록 찾기
            # date, 타자이름, 투수이름, 이닝+초말

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            lm.resetLogHandler()
            lm.setLogPath(os.getcwd() + '/log/')
            lm.setLogFileName('pbpParseLog.txt')
            lm.cleanLog()
            lm.createLogHandler()

            done = 0

            for z in zip(pbpfiles, lineupfiles):
                pbpfile = z[0]
                lineupfile = z[1]
                # dummy code for debug
                js_in = open(pbpfile, 'r', encoding='utf-8')
                pbpjs = json.loads(js_in.read(), 'utf-8', object_pairs_hook=OrderedDict)
                js_in.close()

                js_in = open(lineupfile, 'r', encoding='utf-8')
                lineupjs = json.loads(js_in.read(), 'utf-8', object_pairs_hook=OrderedDict)
                js_in.close()

                # (1) 초기 라인업 생성.
                # (2) 전체 라인업 목록 생성.
                # (3) 문자 로드.
                #   (3)-1. 교체 상황마다 라인업 교체.
                #   (3)-2. 타격시 포지션 기록.

                awayTeamBatters = lineupjs['battersBoxscore']['away']
                homeTeamBatters = lineupjs['battersBoxscore']['home']
                # awayTeamPitchers = lineupjs['pitchersBoxscore']['away']
                # homeTeamPitchers = lineupjs['pitchersBoxscore']['home']

                awayTeamLineup = pbpjs['awayTeamLineUp']
                homeTeamLineup = pbpjs['homeTeamLineUp']

                # players: [name] = [code, pos, seqno, inout]
                # current: [order][seqno] = [name, code, pos]
                home_players = {
                }
                away_players = {
                }
                home_current = {
                    1: {},
                    2: {},
                    3: {},
                    4: {},
                    5: {},
                    6: {},
                    7: {},
                    8: {},
                    9: {},
                    0: {},  # pitcher
                }
                away_current = {
                    1: {},
                    2: {},
                    3: {},
                    4: {},
                    5: {},
                    6: {},
                    7: {},
                    8: {},
                    9: {},
                    0: {},  # pitcher
                }

                for batter in awayTeamLineup['batter']:
                    bname = batter['name']
                    border = batter['batOrder']
                    bcode = batter['pCode']
                    bseqno = batter['seqno']
                    # bpos =batter['pos'][0]
                    bpos = ''  # 임시

                    # 같은 PID 선수 추가 방지
                    try:
                        keys = away_current[border].keys()
                        dupCode = False
                        for key in keys:
                            if away_current[border][key][1] == bcode:
                                dupCode = True
                                break
                        if dupCode:
                            raise KeyError

                        keys = away_players.keys()
                        dupCode = False
                        for key in keys:
                            if away_players[key][0] == bcode:
                                dupCode = True
                                break
                        if dupCode:
                            raise KeyError
                    except KeyError:
                        print()
                        print(em.getTracebackStr())
                        lm.bugLog(em.getTracebackStr())
                        lm.bugLog("Lineup Duplicate PID Error : {}".format(bcode))
                        lm.bugLog("Player Name : {}".format(bname))
                        lm.bugLog("Player Order : {}".format(border))
                        lm.bugLog("Player Position : {}".format(bpos))
                        lm.bugLog("Player Seqno : {}".format(bseqno))
                        lm.killLogManager()
                        exit(1)
                    except:
                        print()
                        print(em.getTracebackStr())
                        lm.bugLog(em.getTracebackStr())
                        lm.bugLog('Unexpected Error')
                        lm.killLogManager()
                        exit(1)
                    else:
                        away_current[border][bseqno] = [bname, bcode, bpos]
                        away_players[bname] = [bcode, bpos, bseqno, False]  # 포지션은 임시로

                for batter in homeTeamLineup['batter']:
                    bname = batter['name']
                    border = batter['batOrder']
                    bcode = batter['pCode']
                    bseqno = batter['seqno']
                    # bpos =batter['pos'][0]
                    bpos = ''  # 임시

                    # 같은 PID 선수 추가 방지
                    try:
                        keys = home_current[border].keys()
                        dupCode = False
                        for key in keys:
                            if home_current[border][key][1] == bcode:
                                dupCode = True
                                break
                        if dupCode:
                            raise KeyError

                        keys = home_players.keys()
                        dupCode = False
                        for key in keys:
                            if home_players[key][0] == bcode:
                                dupCode = True
                                break
                        if dupCode:
                            raise KeyError
                    except KeyError:
                        print()
                        print(em.getTracebackStr())
                        lm.bugLog(em.getTracebackStr())
                        lm.bugLog("Lineup Duplicate PID Error : {}".format(bcode))
                        lm.bugLog("Player Name : {}".format(bname))
                        lm.bugLog("Player Order : {}".format(border))
                        lm.bugLog("Player Position : {}".format(bpos))
                        lm.bugLog("Player Seqno : {}".format(bseqno))
                        lm.killLogManager()
                        exit(1)
                    except:
                        print()
                        print(em.getTracebackStr())
                        lm.bugLog(em.getTracebackStr())
                        lm.bugLog('Unexpected Error')
                        lm.killLogManager()
                        exit(1)
                    else:
                        home_current[border][bseqno] = [bname, bcode, bpos]
                        home_players[bname] = [bcode, bpos, bseqno, False]  # 포지션은 임시로

                for pitcher in awayTeamLineup['pitcher']:
                    pname = pitcher['name']
                    pcode = pitcher['pCode']
                    pseqno = pitcher['seqno']
                    porder = 0  # 투수
                    ppos = '투수'

                    # 같은 PID 선수 추가 방지
                    keys = away_current[porder].keys()
                    dupCode = False
                    for key in keys:
                        if away_current[porder][key][1] == pcode:
                            dupCode = True
                            break
                    if not dupCode:
                        away_current[porder][pseqno] = [pname, pcode, ppos]

                    keys = away_players.keys()
                    dupCode = False
                    for key in keys:
                        if away_players[key][0] == pcode:
                            dupCode = True
                            break
                    if not dupCode:
                        away_players[pname] = [pcode, ppos, pseqno, False]

                for pitcher in homeTeamLineup['pitcher']:
                    pname = pitcher['name']
                    pcode = pitcher['pCode']
                    pseqno = pitcher['seqno']
                    porder = 0  # 투수
                    ppos = '투수'

                    # 같은 PID 선수 추가 방지
                    keys = home_current[porder].keys()
                    dupCode = False
                    for key in keys:
                        if home_current[porder][key][1] == pcode:
                            dupCode = True
                            break
                    if not dupCode:
                        home_current[porder][pseqno] = [pname, pcode, ppos]

                    keys = home_players.keys()
                    dupCode = False
                    for key in keys:
                        if home_players[key][0] == pcode:
                            dupCode = True
                            break
                    if not dupCode:
                        home_players[pname] = [pcode, ppos, pseqno, False]

                for batter in awayTeamBatters:
                    for name in away_players.keys():
                        p = away_players[name]
                        if batter['playerCode'] == p[0]:
                            p[1] = find_position[batter['pos'][0]]
                    for order in away_current.keys():
                        for seq in away_current[order].keys():
                            p = away_current[order][seq]
                            if batter['playerCode'] == p[1]:
                                p[2] = find_position[batter['pos'][0]]

                for batter in homeTeamBatters:
                    for name in home_players.keys():
                        p = home_players[name]
                        if batter['playerCode'] == p[0]:
                            p[1] = find_position[batter['pos'][0]]
                    for order in home_current.keys():
                        for seq in home_current[order].keys():
                            p = home_current[order][seq]
                            if batter['playerCode'] == p[1]:
                                p[2] = find_position[batter['pos'][0]]

                # last_inn = pbpjs['currentInning']
                # assert last_inn.isdigit()

                relayjs = pbpjs['relayTexts']
                relay = {}
                for key in relayjs.keys():
                    if key.isdigit():
                        relay[key] = relayjs[key]
                    elif key.find('currentBatterTexts') >= 0:
                        if type(relayjs[key]) is list:
                            relay[key] = relayjs[key]

                # 추출 대상 텍스트
                # OO XXX (으)로 교체
                # OO XXX : OOO(으)로 수비위치 변경
                # n번타자 XXX
                # n번타자 XXX : 대타 XXX (으)로 교체
                # 공격 종료
                # OOO : XXX XXXXXX 결과
                #### OO주자 : 결과

                fulltext = []

                for inn in relay.keys():
                    foo = []
                    endmsg = None
                    endmsgline = 0
                    lastseq = 0
                    for pbp in relay[inn]:
                        line = pbp['liveText']
                        if line.find('교체') > 0:
                            foo.append([pbp['seqno'], line])
                        elif line.find('변경') > 0:
                            foo.append([pbp['seqno'], line])
                        elif line.find('공격 종료') > 0:
                            if endmsg is not None:
                                foo.append([max(foo)[0]+1, endmsg])
                            endmsg = line
                            endmsgline = lastseq-1
                        elif line.find(' : ') > 0:
                            foo.append([pbp['seqno'], line])
                        lastseq = pbp['seqno']
                    if (endmsgline > 0) & (endmsg is not None):
                        foo.append([endmsgline, endmsg])
                    fulltext += foo
                fulltext.sort()

                gameID = pbpfile[:13]

                if sys.platform == 'win32':
                    csv_file = open('./csv/{0}.csv'.format(gameID), 'w', encoding='cp949')
                else:
                    csv_file = open('./csv/{0}.csv'.format(gameID), 'w', encoding='utf-8')

                # temporary for debugging
                for f in fulltext:
                    csv_file.write(str(f))
                    csv_file.write('\n')
                csv_file.close()

                done = done + 1

                if mon_file_num > 30:
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '+' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               progress_pct * 100), end="")
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '+' * done + '-' * (mon_file_num - done)
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               float(done) / float(mon_file_num) * 100), end="")
                lm.log('pbp parser test')
            csv_month.close()

            # kill log
            lm.killLogManager()

            print()
            print('        Converted {0} files.'.format(str(done)))
            os.chdir('../../')
            # return to pbp root dir
        csv_year.close()
