# pbp_parser.py

import os
import json
import sys
import csv
from collections import OrderedDict
import errorManager as em


pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수",
              "지명타자", "대타", "대주자"]

bb_dir_string = ["투수", "포수", "1루수", "2루수", "3루수",
                 "유격수", "좌익수", "중견수", "우익수",
                 "우중간", "좌중간"]

res_string = ["1루타", "안타" "2루타", "3루타", "홈런", "실책", "땅볼",
              "뜬공", "희생플라이", "희생번트", "야수선택", "삼진",
              "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타"]

hit_results = ['안타', '1루타', '2루타', '3루타', '홈런']

out_results = ['땅볼', '플라이', '병살타', '라인드라이브',
               ' 번트', '희생번트', '삼중살']

nobb_outs = ['삼진', '낫 아웃', '타구맞음', '쓰리번트']

runner_outs = ['견제사', '  포스아웃', '  태그아웃',
               '도루실패', '진루실패', '터치아웃', '공과']

other_errors = '실책'
other_kn = '낫아웃'
other_fc = '야수선택'
other_bb = '볼넷'
other_ibb = '고의4구'
other_hbp = '몸에 맞는 볼'
other_reach = '출루'

other_swap = '교체'
other_move = '위치 변경'
other_inn_end = '공격 종료'

# BUGBUG 예상치 못한 텍스트 종류 - 패스하는 경우
other_pass = ['경고', '부상', '~', '쉬프트', '코치']

fieldNames = ['Date', 'Batter', 'Pitcher', 'Inning',
              'X', 'Y', 'Fielder', 'Ball Direction',
              'pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'pos6',
              'pos7', 'pos8', 'pos9', 'Detail Result',
              'Result', 'Batter Team', 'Pitcher Team',
              'Home', 'Away', 'seqno']

teams = {
    'HH': '한화',
    'HT': 'KIA',
    'LG': 'LG',
    'SK': 'SK',
    'KT': 'kt',
    'WO': '넥센',
    'OB': '두산',
    'NC': 'NC',
    'LT': '롯데',
    'SS': '삼성'
}

positions = dict(enumerate(pos_string))
results = dict(enumerate(res_string))
bb_dirs = dict(enumerate(bb_dir_string, start=1))
bb_dirs = dict((v,k) for k, v in bb_dirs.items())


def parse_result(text):
    # hit
    for b in hit_results:
        if text.find(b) > 0:
            return ['h', b]
    # out
    for o in out_results:
        if text.find(o) > 0:
            if text.find('출루') < 0:
                return ['o', o]
    # 실책
    if text.find(other_errors) > 0:
        if text.find('낫아웃') < 0:
            return ['e', text]
    # 낫아웃 폭투포일
    if text.find(other_kn) > 0:
        return ['k', text]
    # 야수선택
    if text.find(other_fc) > 0:
        return ['f', text]
    # no bb out; 삼진, 낫 아웃, 타구맞음
    for n in nobb_outs:
        if text.find(n) > 0:
            return ['n', n]
    # 4사구
    if text.find(other_bb) > 0:
        return ['b', text]
    if text.find(other_ibb) > 0:
        return ['b', text]
    if text.find(other_hbp) > 0:
        return ['b', text]
    # 출루에 아웃은 왜 붙어서 이 난리인지 모르겠는데 그냥 c로 해서 패스하자
    if text.find(other_reach) > 0:
        return ['c', text]
    # runner out
    for o in runner_outs:
        if text.find(o) > 0:
            return ['r', o]
    # 교체/이닝종료/포변
    if text.find(other_swap) > 0:
        if text.find('(으)로') > 0:
            return ['s', text]
    elif text.find(other_move) > 0:
        return ['p', text]
    elif text.find(other_inn_end) > 0:
        return ['i', text]
    # BUGBUG 예상치 못한 텍스트 종류 - 패스하는 경우
    for z in other_pass:
        if text.find(z) >= 0:
            return ['z', text]
    return ['x', 'Fail']


def out_type(otype):
    if otype == '땅볼':
        return '땅볼 아웃'
    elif otype == '플라이':
        return '플라이 아웃'
    elif otype == '병살타':
        return '병살타'
    elif otype == '라인드라이브':
        return '라인드라이브 아웃'
    elif otype == ' 번트':
        return '번트 아웃'
    elif otype == '희생번트':
        return '희생번트 아웃'
    elif otype == '삼중살':
        return '삼중살 아웃'


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
                csv_year_writer = csv.DictWriter(csv_year, delimiter=',',
                                            dialect='excel', fieldnames=fieldNames,
                                            lineterminator='\n')
                csv_year_writer.writeheader()

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
            csv_month_writer = csv.DictWriter(csv_month, delimiter=',',
                                        dialect='excel', fieldnames=fieldNames,
                                        lineterminator='\n')
            csv_month_writer.writeheader()

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            lm.resetLogHandler()
            lm.setLogPath(os.getcwd() + '/log/')
            lm.setLogFileName('pbpParseLog.txt')
            lm.cleanLog()
            lm.createLogHandler()

            done = 0

            for z in zip(pbpfiles, lineupfiles):
                game_id = z[0][:13]
                if game_id[:8] == '20170509':
                    done += 1
                    continue

                pbpfile = z[0]
                lineupfile = z[1]

                js_in = open(pbpfile, 'r', encoding='utf-8')
                pbpjs = json.loads(js_in.read(), 'utf-8', object_pairs_hook=OrderedDict)
                js_in.close()

                js_in = open(lineupfile, 'r', encoding='utf-8')
                lineupjs = json.loads(js_in.read(), 'utf-8', object_pairs_hook=OrderedDict)
                js_in.close()

                bb_json_filename = '../../../bb_data/{}/{}/{}_bb.json'.format(game_id[:4], game_id[4:6], game_id)
                if os.path.isfile(bb_json_filename):
                    js_in = open(bb_json_filename, 'r', encoding='utf-8')
                    bbjs = json.loads(js_in.read(), 'utf-8')
                    js_in.close()
                else:
                    print()
                    print("DOWNLOAD BB DATA FILE FIRST : {}".format(game_id))
                    lm.bugLog("DOWNLOAD BB DATA FILE FIRST : {}".format(game_id))
                    lm.bugLog(os.getcwd())
                    csv_month.close()
                    csv_year.close()
                    os.chdir('../../')
                    # current path : ./pbp_data/
                    lm.killLogManager()
                    exit(1)

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
                # OO주자 : 결과

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

                # structure memo
                # players: [name] = [code, pos, seqno, inout]
                # current: [order][seqno] = [name, code, pos]
                date = '{0}-{1}-{2}'.format(game_id[:4], game_id[4:6], game_id[6:8])
                cur_inn = 1
                TopBot = '초'
                inn = '{}회{}'.format(cur_inn, TopBot)
                away_order = 1
                home_order = 1
                batterTeam = game_id[8:10]
                pitcherTeam = game_id[10:12]
                cur_bat_away = away_current[away_order][min(away_current[away_order].keys())]
                cur_pit_home = home_current[0][min(home_current[0].keys())]
                outs = 0

                d = {
                    'Date': date,
                    'Batter': cur_bat_away[0],
                    'Pitcher': cur_pit_home[0],
                    'Inning': inn,
                    'X': 0,
                    'Y': 0,
                    'Fielder': '',
                    'Ball Direction': '',
                    'pos1': home_fielder[1],
                    'pos2': home_fielder[2],
                    'pos3': home_fielder[3],
                    'pos4': home_fielder[4],
                    'pos5': home_fielder[5],
                    'pos6': home_fielder[6],
                    'pos7': home_fielder[7],
                    'pos8': home_fielder[8],
                    'pos9': home_fielder[9],
                    'Detail Result': '',
                    'Result': '',
                    'Batter Team': batterTeam,
                    'Pitcher Team': pitcherTeam,
                    'Home': teams[game_id[10:12]],
                    'Away': teams[game_id[8:10]],
                    'seqno': 0
                }

                for text in fulltext:
                    if (text[1].find('주자') > 0) and (text[1].find('아웃') < 0) and (text[1].find('교체')  < 0) and (text[1].find('변경') < 0):
                        continue
                    [t_type, result] = parse_result(text[1])
                    d['seqno'] = text[0]
                    if t_type == 'h' or t_type == 'o' or t_type == 'f' or t_type == 'e':
                        # 인플레이 타구
                        if t_type == 'h':
                            d['Result'] = '안타'
                            for htype in hit_results:
                                if text[1].find(htype) >= 0:
                                    d['Detail Result'] = htype
                                    break
                        elif t_type == 'o':
                            # xx 어쩌구저쩌구 아웃
                            d['Result'] = '아웃'
                            for otype in out_results:
                                if text[1].find(otype) >= 0:
                                    d['Detail Result'] = out_type(otype)
                            if text[1].find('아웃') > 0:
                                outs += 1
                        elif t_type == 'f':
                            d['Result'] = '야수선택'
                            d['Detail Result'] = '야수선택'
                        else:
                            if text[1].find('낫아웃') > 0:
                                d['Result'] = '낫아웃'
                                d['Detail Result'] = '낫아웃'
                            else:
                                d['Result'] = '실책'
                                d['Detail Result'] = '실책'
                        p1 = text[1].find(':')
                        d['Ball Direction'] = text[1][p1+2:].split(' ')[0]
                        if TopBot == '초':
                            d['Batter'] = away_current[away_order][min(away_current[away_order].keys())][0]
                            d['Pitcher'] = home_current[0][min(home_current[0].keys())][0]
                            d['pos1'] = home_fielder[1]
                            d['pos2'] = home_fielder[2]
                            d['pos3'] = home_fielder[3]
                            d['pos4'] = home_fielder[4]
                            d['pos5'] = home_fielder[5]
                            d['pos6'] = home_fielder[6]
                            d['pos7'] = home_fielder[7]
                            d['pos8'] = home_fielder[8]
                            d['pos9'] = home_fielder[9]
                            if bb_dirs[d['Ball Direction']] < 10:
                                d['Fielder'] = home_fielder[bb_dirs[d['Ball Direction']]]
                            else:
                                d['Fielder'] = 'None'
                            d['Batter Team'] = teams[game_id[8:10]]
                            d['Pitcher Team'] = teams[game_id[10:12]]
                            away_order += 1
                            if away_order == 10:
                                away_order = 1
                            try:
                                x = bbjs['ballsInfo']['away'][str(d['seqno'])]['gx']
                                y = bbjs['ballsInfo']['away'][str(d['seqno'])]['gy']
                                if (x == 0) and (y == 0):
                                    x = 247
                                    y = 461
                                d['X'] = round(x * 355/500 + 46, 1)
                                d['Y'] = round(y * 375/500 - 31, 1)
                            except:
                                print()
                                print(game_id)
                                print(d['seqno'])
                                print(text[1])
                                print(parse_result(text[1]))
                                print(bbjs['ballsInfo']['away'].keys())
                                exit(1)
                        else:
                            d['Batter'] = home_current[home_order][min(home_current[home_order].keys())][0]
                            d['Pitcher'] = away_fielder[1]
                            d['pos1'] = away_fielder[1]
                            d['pos2'] = away_fielder[2]
                            d['pos3'] = away_fielder[3]
                            d['pos4'] = away_fielder[4]
                            d['pos5'] = away_fielder[5]
                            d['pos6'] = away_fielder[6]
                            d['pos7'] = away_fielder[7]
                            d['pos8'] = away_fielder[8]
                            d['pos9'] = away_fielder[9]
                            try:
                                if bb_dirs[d['Ball Direction']] < 10:
                                    d['Fielder'] = away_fielder[bb_dirs[d['Ball Direction']]]
                                else:
                                    d['Fielder'] = 'None'
                            except KeyError:
                                try:
                                    pos_text = text[1][p1+2:].split(' ')[0]
                                    for bds in bb_dir_string:
                                        if pos_text.find(bds) >= 0:
                                            d['Ball Direction'] = bds
                                            break
                                    if bb_dirs[d['Ball Direction']] < 10:
                                        d['Fielder'] = away_fielder[bb_dirs[d['Ball Direction']]]
                                    else:
                                        d['Fielder'] = 'None'
                                except:
                                    print()
                                    print(game_id)
                                    print(d['seqno'])
                                    print(text[1])
                                    print(parse_result(text[1]))
                                    exit(1)
                            d['Batter Team'] = teams[game_id[10:12]]
                            d['Pitcher Team'] = teams[game_id[8:10]]
                            home_order += 1
                            if home_order == 10:
                                home_order = 1
                            try:
                                x = bbjs['ballsInfo']['home'][str(d['seqno'])]['gx']
                                y = bbjs['ballsInfo']['home'][str(d['seqno'])]['gy']
                                if (x == 0) and (y == 0):
                                    x = 247
                                    y = 461
                                d['X'] = round(x * 355/500 + 46, 1)
                                d['Y'] = round(y * 375/500 - 31, 1)
                            except:
                                print()
                                print(text[1])
                                print(parse_result(text[1]))
                                print(game_id)
                                print(d['seqno'])
                                print(bbjs['ballsInfo']['home'].keys())
                                exit(1)
                        csv_writer.writerow(d)
                        csv_month_writer.writerow(d)
                        csv_year_writer.writerow(d)
                    elif t_type == 'k' or t_type == 'n' or t_type == 'c':
                        # 낫아웃 폭투포일
                        # 삼진, 낫 아웃, 타구맞음
                        if t_type == 'n':
                            outs += 1
                        if TopBot == '초':
                            away_order += 1
                            if away_order == 10:
                                away_order = 1
                        else:
                            home_order += 1
                            if home_order == 10:
                                home_order = 1
                    elif t_type == 'b':
                        # 4사구
                        if TopBot == '초':
                            away_order += 1
                            if away_order == 10:
                                away_order = 1
                        else:
                            home_order += 1
                            if home_order == 10:
                                home_order = 1
                    elif t_type == 'r':
                        outs += 1
                    elif t_type == 's':
                        # 선수 교체
                        p1 = text[1].find(': ')
                        p2 = text[1].find('(으)')
                        t1 = text[1][p1+2:p2-1].split(' ')
                        new_player = t1[1]
                        new_pos = t1[0]

                        t1 = text[1][:p1].split(' ')
                        old_player = t1[1]
                        old_pos = t1[0]

                        if TopBot == '초':
                            if (new_pos == '대타') or (new_pos == '대주자'):
                                cur = away_current
                                ps = away_players
                            else:
                                cur = home_current
                                ps = home_players
                                def_fs = home_fielder
                        else:

                            if (new_pos == '대타') or (new_pos == '대주자'):
                                cur = home_current
                                ps = home_players
                            else:
                                cur = away_current
                                ps = away_players
                                def_fs = away_fielder

                        # 새로 들어간 선수 inout True
                        for name in ps.keys():
                            if name == new_player:
                                if ps[name][3] == False:
                                    ps[name][3] = True
                                    break

                        # 나가는 선수 inout False
                        # 나가는 선수 current 에서 pop

                        for order in cur:
                            curno = min(cur[order].keys())
                            if old_pos.find('타자') < 0:
                                # 수비 교체
                                if cur[order][curno][0] == old_player:
                                    if cur[order][curno][2] == old_pos:
                                        oc = cur[order][curno][1]
                                        for name in ps.keys():
                                            if (name == old_player) and (oc == ps[name][0]):
                                                ps[name][3] = False
                                                break
                                        cur[order].pop(curno)
                                        if len(cur[order]) > 0:
                                            cur[order][min(cur[order].keys())][2] = new_pos
                                            lm.log('ORDER {} 교체 : {} {} -> {} {}'.format(order, old_pos, old_player, new_pos, str(cur[order][min(cur[order].keys())][0])))
                                        if new_pos != '투수':
                                            break
                            else:
                                # 대타/대주자
                                if cur[order][curno][0] == old_player:
                                    oc = cur[order][curno][1]
                                    for name in ps.keys():
                                        if (name == old_player) and (oc == ps[name][0]):
                                            ps[name][3] = False
                                            break
                                    cur[order].pop(curno)
                                    try:
                                        if len(cur[order]) > 0:
                                            cur[order][min(cur[order].keys())][2] = new_pos
                                            lm.log('ORDER {} 교체 : {} {} -> {} {}'.format(order, old_pos, old_player, new_pos,
                                                                                         str(cur[order][min(cur[order].keys())][
                                                                                                 0])))
                                    except:
                                        print()
                                        print(text[1])
                                        print(order)
                                        print(cur[order])
                                        print(game_id)
                                        exit(1)

                        # 필딩 라인업 교체
                        try:
                            if pos_number[new_pos] > 0:
                                def_fs[pos_number[new_pos]] = new_player
                        except:
                            print()
                            print(text[1])
                            print(new_pos)
                            print(game_id)
                            exit(1)
                    elif t_type == 'p':
                        # 포지션 변경
                        p1 = text[1].find(': ')
                        p2 = text[1].find('(으)')
                        new_pos = text[1][p1 + 2:p2]
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
                            if cur[order][curno][0] == player:
                                if cur[order][curno][2] == old_pos:
                                    cur[order][curno][2] = new_pos
                                    break
                        if pos_number[new_pos] > 0:
                            field[pos_number[new_pos]] = player
                    elif t_type == 'i':
                        if outs != 3:
                            print()
                            print('no 3 out inning change : outcount = {}'.format(outs))
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
                            d['Inning'] = inn
                            outs = 0
                    elif t_type == 'z':
                        # BUGBUG 예상치 못한 텍스트 종류 - 패스하는 경우
                        outs = outs  # dummy code
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

                csv_file.close()

                done = done + 1
                lm.log('{} convert'.format(game_id))

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
            csv_month.close()

            print()
            print('        Converted {0} files.'.format(str(done)))
            os.chdir('../../')
            # return to pbp root dir
        csv_year.close()
