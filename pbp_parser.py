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

hit_results = ['안타', '2루타', '3루타', '홈런']

out_results = ['땅볼', '플라이', '병살타', '라인드라이브',
               '타구맞음', '번트']

nobb_outs = ['삼진', '낫 아웃', '견제사', '  포스아웃', '  태그아웃',
             '도루실패', '진루실패']

other_results = ['실책', '낫아웃', '포일', '폭투']

# OO XXX (으)로 교체
# OO XXX : OOO(으)로 수비위치 변경
# n번타자 XXX
# n번타자 XXX : 대타 XXX (으)로 교체
# 공격 종료
# OOO : XXX XXXXXX 결과
# OO주자 : 결과

other_swap = '교체'

other_move = '위치 변경'

other_inn_end = '공격 종료'

'''
csv_header = '"date","inn","batterName","pitcherName",' \
             '"batterTeam","pitcherTeam","actual_result","result",' \
             '"gx","gy","pos1","pos2","pos3",' \
             '"pos4","pos5","pos6","pos7","pos8","pos9"\n'

fieldNames = ['date', 'batterName', 'pitcherName', 'inn',
              'gx', 'gy', 'fielder_position', 'actual_result',
              'result', 'batterTeam', 'pitcherTeam', 'seqno']

'''

fieldNames = ['date', 'batterName', 'pitcherName', 'inn',
              'pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'pos6',
              'pos7', 'pos8', 'pos9', 'actual_result',
              'result', 'batterTeam', 'pitcherTeam', 'seqno']

positions = dict(enumerate(pos_string))
results = dict(enumerate(res_string))


def parse_result(text):
    for b in hit_results:
        if text.find(b) > 0:
            return ['h', b]
    for o in out_results:
        if text.find(o) > 0:
            return ['o', o]
    # no bb out, runner out
    for o in nobb_outs:
        if text.find(o) > 0:
            return ['r', o]
    for e in other_results:
        if text.find(e) > 0:
            return ['e', e]
    # 교체/이닝종료/포변
    if text.find(other_swap) > 0:
        return ['s', text]
    elif text.find(other_move) > 0:
        return ['p', text]
    elif text.find(other_inn_end) > 0:
        return ['i', text]
    return ['x', 'Fail']

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

pos_number = {
    '투수': 1,
    '포수': 2,
    '1루수': 3,
    '2루수': 4,
    '3루수': 5,
    '유격수': 6,
    '좌익수': 7,
    '중견수': 8,
    '우익수': 9,
    '지명타자': -1,
    '교체': -2,
    '대타': -3,
    '대주자': -4
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

    csv_year = ''
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
                csv_writer = csv.DictWriter(csv_year, delimiter=',',
                                            dialect='excel', fieldnames=fieldNames,
                                            lineterminator='\n')
                csv_writer.writeheader()

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
            csv_writer = csv.DictWriter(csv_month, delimiter=',',
                                        dialect='excel', fieldnames=fieldNames,
                                        lineterminator='\n')
            csv_writer.writeheader()
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
                home_fielder = {
                    1: '',
                    2: '',
                    3: '',
                    4: '',
                    5: '',
                    6: '',
                    7: '',
                    8: '',
                    9: ''
                }
                away_fielder = {
                    1: '',
                    2: '',
                    3: '',
                    4: '',
                    5: '',
                    6: '',
                    7: '',
                    8: '',
                    9: ''
                }

                for batter in awayTeamLineup['batter']:
                    bname = batter['name']
                    border = batter['batOrder']
                    bcode = batter['pCode']
                    bseqno = batter['seqno']
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

                for order in away_current.keys():
                    cur = min(away_current[order].keys())
                    pos = pos_number[away_current[order][cur][2]]
                    if pos > 0:
                        away_fielder[pos] = away_current[order][cur][0]
                    else:
                        continue

                for order in home_current.keys():
                    cur = min(home_current[order].keys())
                    pos = pos_number[home_current[order][cur][2]]
                    if pos > 0:
                        home_fielder[pos] = home_current[order][cur][0]
                    else:
                        continue

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
                        elif line.find('위치변경') > 0:
                            foo.append([pbp['seqno'], line])
                        elif line.find('공격 종료') > 0:
                            if endmsg is not None:
                                foo.append([max(foo)[0] + 1, endmsg])
                            endmsg = line
                            endmsgline = lastseq - 1
                        elif line.find(' : ') > 0:
                            foo.append([pbp['seqno'], line])
                        lastseq = pbp['seqno']
                    if (endmsgline > 0) & (endmsg is not None):
                        foo.append([endmsgline, endmsg])
                    fulltext += foo
                fulltext.sort()

                game_id = pbpfile[:13]

                if sys.platform == 'win32':
                    csv_file = open('./csv/{0}.csv'.format(game_id), 'w', encoding='cp949')
                else:
                    csv_file = open('./csv/{0}.csv'.format(game_id), 'w', encoding='utf-8')
                csv_writer = csv.DictWriter(csv_file, delimiter=',',
                                            dialect='excel', fieldnames=fieldNames,
                                            lineterminator='\n')
                csv_writer.writeheader()

                # 처음 라인업에서 시작
                # 결과 나올때마다 write row
                # 타순 하나씩 pass
                # 교체 있을 때 현재라인업 수정
                '''
                fieldNames = ['date', 'batterName', 'pitcherName', 'inn',
                              'pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'pos6',
                              'pos7', 'pos8', 'pos9', 'actual_result',
                              'result', 'batterTeam', 'pitcherTeam', 'seqno']
                '''
                # players: [name] = [code, pos, seqno, inout]
                # current: [order][seqno] = [name, code, pos]
                date = '{0}-{1}-{2}'.format(game_id[:4], game_id[4:2], game_id[6:2])
                cur_inn = 1
                TopBot = '초'
                inn = '{}회{}'.format(cur_inn, TopBot)
                order = 1
                batterTeam = game_id[8:2]
                pitcherTeam = game_id[10:2]
                cur_bat_away = away_current[order][min(away_current[order].keys())]
                cur_bat_home = home_current[order][min(away_current[order].keys())]
                cur_pit_away = away_current[0][min(away_current[0].keys())]
                cur_pit_home = home_current[0][min(home_current[0].keys())]
                outs = 0

                d = {
                    'date': date,
                    'batterName': cur_bat_away[0],
                    'pitcherName': cur_pit_home[0],
                    'inn': inn,
                    'pos1': home_fielder[1],
                    'pos2': home_fielder[2],
                    'pos3': home_fielder[3],
                    'pos4': home_fielder[4],
                    'pos5': home_fielder[5],
                    'pos6': home_fielder[6],
                    'pos7': home_fielder[7],
                    'pos8': home_fielder[8],
                    'pos9': home_fielder[9],
                    'actual_result': '',
                    'result': '',
                    'batterTeam': batterTeam,
                    'pitcherTeam': pitcherTeam,
                    'seqno': 0
                }
                for text in fulltext:
                    if (text.find('주자') > 0) and (text.find('아웃') < 0) and (text.find('교체')  < 0):
                        continue
                    [t_type, result] = parse_result(text[1])
                    d['actual_result'] = result
                    d['seqno'] = text[0]
                    if t_type == 'h':
                        d['result'] = '안타'
                    elif t_type == 'o':
                        d['result'] = '아웃'
                        outs += 1
                    elif t_type == 'e':
                        d['result'] = '실책'
                    elif t_type == 'r':
                        outs += 1
                    elif t_type == 's':
                        # swap
                        p1 = text[1].find(': ')
                        p2 = text[1].find('(으)')
                        t1 = text[p1+2:p2-1].split(' ')
                        new_player = t1[0]
                        new_pos = t1[1]
                        t1 = text[1][:p1].split(' ')[0]
                        old_player = t1[0]
                        old_pos = t1[1]
                        if TopBot == '초':
                            att_cur = away_current
                            def_cur = home_current
                            att_ps = away_players
                            def_ps = home_players
                            def_fs = home_fielder
                        else:
                            att_cur = home_current
                            def_cur = away_current
                            att_ps = home_players
                            def_ps = away_players
                            def_fs = away_fielder
                        if text[1].find('타자') or text[1].find('주자'):
                            cur = att_cur
                            ps = att_ps
                        else:
                            cur = def_cur
                            ps = def_ps

                        for name in ps.keys():
                            if name == new_player:
                                if ps[name][3] == False:
                                    ps[name][3] = True
                        for order in cur:
                            curno = min(cur[order].keys())
                            if cur[order][curno][0] == old_player and cur[order][curno][2] == old_pos:
                                oc = cur[order][curno][1]
                                for name in ps.keys():
                                    if name == old_player:
                                        if oc == ps[name][0]:
                                            ps[name][3] = False
                                            break
                                cur[order].pop(curno)
                                cur[order][min(cur[order].keys())][2] = new_pos
                                break
                        if pos_number[new_pos] > 0:
                            def_fs[pos_number[new_pos]] = new_player
                    elif t_type == 'p':
                        p1 = text[1].find(': ')
                        p2 = text[1].find('(으)')
                        new_pos = text[p1 + 2:p2]
                        t1 = text[1][:p1].split(' ')
                        old_pos = t1[0]
                        player = t1[1]
                        if TopBot == '초':
                            cur = home_current
                            field = home_fielder
                        else:
                            cur = away_current
                            field = away_fielder
                        for order in cur:
                            curno = min(cur[order].keys())
                            if cur[order][curno][0] == player and cur[order][curno][2] == old_pos:
                                cur[order][curno][2] = new_pos
                        field[pos_number[new_pos]] = player
                    elif t_type == 'i':
                        if outs != 3:
                            print()
                            print('no 3 out inning change')
                            print('Game ID : {}'.format(game_id))
                            print('Text : {}'.format(text))
                            lm.bugLog('no 3 out inning change')
                            lm.bugLog('Game ID : {}'.format(game_id))
                            lm.bugLog('Text : {}'.format(text))
                            lm.killLogManager()
                            exit(1)
                        else:
                            if TopBot == '초':
                                TopBot = '말'
                            else:
                                TopBot = '초'
                                cur_inn += 1
                            inn = '{}회{}'.format(cur_inn, TopBot)
                            d['inn'] = inn
                    else:
                        print()
                        print('Unexpected type of text')
                        print('Game ID : {}'.format(game_id))
                        print('Text : {}'.format(text))
                        lm.bugLog('Unexpected type of text')
                        lm.bugLog('Game ID : {}'.format(game_id))
                        lm.bugLog('Text : {}'.format(text))
                        lm.killLogManager()
                        exit(1)

                # temporary for debugging
                csv_file.write('AwayTeamLineup\n')
                for order in away_current.keys():
                    firstno = min(away_current[order].keys())
                    if int(order) == 0:
                        csv_file.write('선발 : {}\n'.format(str(away_current[order][firstno])))
                    else:
                        csv_file.write('{}번 : {}\n'.format(order, str(away_current[order][firstno])))

                csv_file.write('HomeTeamLineup\n')
                for order in home_current.keys():
                    firstno = min(home_current[order].keys())
                    if int(order) == 0:
                        csv_file.write('선발 : {}\n'.format(str(home_current[order][firstno])))
                    else:
                        csv_file.write('{}번 : {}\n'.format(order, str(home_current[order][firstno])))

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
