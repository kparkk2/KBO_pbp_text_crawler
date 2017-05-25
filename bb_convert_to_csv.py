# bb_convert_to_csv.py
#
# IN: year/month - target match time period
# OUT: CSV files for target match time period
#
# (1) read each JSON files.
# (2) load JSON data structure.
# (3) reconstruct as string list.
# (4) dump to the CSV file.

import os
import json
# import random
import platform

positions = [
    # 투수, 포수, 1루수, 2루수
    u'\ud22c\uc218', u'\ud3ec\uc218', u'1\ub8e8\uc218', u'2\ub8e8\uc218',
    # 3루수, 유격수, 좌익수, 중견수
    u'3\ub8e8\uc218', u'\uc720\uaca9\uc218', u'\uc88c\uc775\uc218', u'\uc911\uacac\uc218',
    # 우익수, 좌중간, 우중간
    u'\uc6b0\uc775\uc218', u'\uc88c\uc911\uac04', u'\uc6b0\uc911\uac04']

results = [
    # 1루타, 2루타, 3루타, 홈런, 실책
    u'1\uB8E8\uD0C0', u'2\uB8E8\uD0C0', u'3\uB8E8\uD0C0', u'\uD648\uB7F0', u'\uC2E4\uCC45',
    # 땅볼, 플라이 아웃, 희생플라이
    u'\uB545\uBCFC', u'\uD50C\uB77C\uC774 \uC544\uC6C3', u'\uD76C\uC0DD\uD50C\uB77C\uC774',
    # 희생번트, 야수선택, 삼진
    u'\uD76C\uC0DD\uBC88\uD2B8', u'\uC57C\uC218\uC120\uD0DD', u'\uC0BC\uC9C4',
    # 스트라이크(낫 아웃), 타격방해
    u'\uC2A4\uD2B8\uB77C\uC774\uD06C', u'\uD0C0\uACA9\uBC29\uD574',
    # 라인드라이브, 병살타
    u'\uB77C\uC778\uB4DC\uB77C\uC774\uBE0C', u'\uBCD1\uC0B4\uD0C0',
    # 번트(일반), 내야안타
    u'\uBC88\uD2B8', u'\uB0B4\uC57C\uC548\uD0C0']


def find_pos(detail_result, num):
    position = positions[num]

    pos_index = 0
    for i in range(len(detail_result)):
        if position[pos_index] == detail_result[i]:
            pos_index = pos_index + 1
            if pos_index == len(position):
                break
        else:
            pos_index = 0

    if pos_index == len(position):
        return True
    else:
        return False


def find_result(detail_result, num):
    result = results[num]

    res_index = 0
    for i in range(len(detail_result)):
        if result[res_index] == detail_result[i]:
            res_index = res_index + 1
            if res_index == len(result):
                break
        else:
            res_index = 0

    if res_index == len(result):
        return True
    else:
        return False


def get_team(team_name):
    if team_name == "HT":
        return "KIA"
    elif team_name == "SS":
        return "삼성"
    elif team_name == "WO":
        return "넥센"
    elif team_name == "SK":
        return "SK"
    elif team_name == "HH":
        return "한화"
    elif team_name == "LG":
        return "LG"
    elif team_name == "OB":
        return "두산"
    elif team_name == "LT":
        return "롯데"
    elif team_name == "NC":
        return "NC"
    else:
        return "KT"

pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수",
              "좌중간", "우중간"]

res_string = ["안타", "2루타", "3루타", "홈런", "실책", "땅볼", "뜬공",
              "희생플라이", "희생번트", "야수선택", "삼진", "낫아웃", "타격방해",
              "직선타", "병살타", "번트", "내야안타"]

csv_header = '"date","batterName","pitcherName","inn",' \
             '"gx","gy","fielder_position","actual_result",' \
             '"result","batterTeam","pitcherTeam","seqno"\n'


def write_in_csv(filename, data, is_comma):
    filename.write('"' + data + '"')
    if is_comma:
        filename.write(',')


def write_data(ball_ids, csv_file, js, match_info, is_home):
    if is_home is True:
        homeaway = 'home'
    else:
        homeaway = 'away'

    match_date = str(match_info[0:8])
    match_away = str(match_info[8:10])
    match_home = str(match_info[10:12])
    date = '{0}-{1}-{2}'.format(match_date[0:4], match_date[4:6], match_date[6:8])

    for ball in ball_ids:
        ball_key = str(ball)

        # initialization
        batter_name = pitcher_name = result = gx = gy = detail_result = inn = seq_no = ''

        try:
            batter_name = js['ballsInfo'][homeaway][ball_key]['batterName']
            pitcher_name = js['ballsInfo'][homeaway][ball_key]['pitcherName']
            result = js['ballsInfo'][homeaway][ball_key]['result']
            gx = js['ballsInfo'][homeaway][ball_key]['gx']
            gy = js['ballsInfo'][homeaway][ball_key]['gy']
            detail_result = js['ballsInfo'][homeaway][ball_key]['detailResult']
            inn = js['ballsInfo'][homeaway][ball_key]['inn']
            seq_no = js['ballsInfo'][homeaway][ball_key]['seqno']
        except KeyError as e:
            print()
            print("Key Value Error : {}".format(e))
            print("Match Info : {}".format(match_info))
            print("homeaway : {}".format(homeaway))
            print("ball id : {}".format(ball))
            print("all ball id : {}".format(ball_ids))
            # print("js values : ")
            # print(json.dumps(js['ballsInfo'][homeaway], sort_keys=True, indent=4, ensure_ascii=False))
            exit(1)
        batter_team = match_away
        pitcher_team = match_home

        fielder_position = ""
        actual_result = ""

        for i in range(len(pos_string)):
            if find_pos(detail_result, i) is True:
                fielder_position = pos_string[i]
                break

        for i in range(len(res_string)):
            if find_result(detail_result, i) is True:
                actual_result = res_string[i]
                # strike out, not out, interference -> no fielder
                if (i == 10) or (i == 11) or (i == 12):
                    fielder_position = ""
                break

        # python3에서는 utf-8 인코딩 변환이 필요 없는듯
        # batterName = batterName.encode('utf-8')
        # pitcherName = pitcherName.encode('utf-8')
        # result = result.encode('utf-8')
        # inn = inn.encode('utf-8')
        '''
        # TO ADD RANDOM NUMBERS TO X/Y COORDINATE, INCLUDE CODES BELOW:
            rx = random.randrange(1, 11) * random.choice([-1, 1])
            ry = random.randrange(1, 11) * random.choice([-1, 1])
            if not ((gx == 0) and (gy == 0)):
                gx = gx + rx
                gy = gy + ry
        # (COMMENTED)
        '''
        write_in_csv(csv_file, date, True)
        write_in_csv(csv_file, batter_name, True)
        write_in_csv(csv_file, pitcher_name, True)
        write_in_csv(csv_file, inn, True)
        write_in_csv(csv_file, str(gx), True)
        write_in_csv(csv_file, str(gy), True)
        write_in_csv(csv_file, fielder_position, True)
        write_in_csv(csv_file, actual_result, True)
        write_in_csv(csv_file, result, True)
        write_in_csv(csv_file, get_team(batter_team), True)
        write_in_csv(csv_file, get_team(pitcher_team), True)
        write_in_csv(csv_file, str(seq_no), False)
        csv_file.write('\n')


def write_csv(csv_file, csv_month, csv_year, js, match_info):
    # away first
    hr_id = js['teamsInfo']['away']['hr']
    hit_id = js['teamsInfo']['away']['hit']
    o_id = js['teamsInfo']['away']['o']

    write_data(hr_id, csv_file, js, match_info, False)
    write_data(hit_id, csv_file, js, match_info, False)
    write_data(o_id, csv_file, js, match_info, False)

    write_data(hr_id, csv_month, js, match_info, False)
    write_data(hit_id, csv_month, js, match_info, False)
    write_data(o_id, csv_month, js, match_info, False)

    write_data(hr_id, csv_year, js, match_info, False)
    write_data(hit_id, csv_year, js, match_info, False)
    write_data(o_id, csv_year, js, match_info, False)

    # home next
    hr_id = js['teamsInfo']['home']['hr']
    hit_id = js['teamsInfo']['home']['hit']
    o_id = js['teamsInfo']['home']['o']

    write_data(hr_id, csv_file, js, match_info, True)
    write_data(hit_id, csv_file, js, match_info, True)
    write_data(o_id, csv_file, js, match_info, True)

    write_data(hr_id, csv_month, js, match_info, True)
    write_data(hit_id, csv_month, js, match_info, True)
    write_data(o_id, csv_month, js, match_info, True)

    write_data(hr_id, csv_year, js, match_info, True)
    write_data(hit_id, csv_year, js, match_info, True)
    write_data(o_id, csv_year, js, match_info, True)


def bb_convert_to_csv(mon_start, mon_end, year_start, year_end):
    if not os.path.isdir("./bb_data"):
        print("DOWNLOAD DATA FIRST")
        exit(1)
    os.chdir("./bb_data")
    # current path : ./bb_data/
    print("##################################################")
    print("###### CONVERT BB DATA(JSON) TO CSV FORMAT #######")
    print("##################################################")

    # check OS
    is_windows = (platform.system() == 'Windows')
    # Win: True, Other: False

    for year in range(year_start, year_end+1):
        print("  for Year {0}...".format(str(year)))

        if not os.path.isdir("./{0}".format(str(year))):
            print(os.getcwd())
            print("DOWNLOAD YEAR {0} DATA FIRST".format(str(year)))
            continue

        csv_year = ''  # dummy
        for month in range(mon_start, mon_end+1):
            print("    Month {0}... ".format(str(month)))

            if month == mon_start:
                csv_year = open("{0}/{1}.csv".format(str(year), str(year)), 'w')
                if is_windows:
                    csv_year.write('\xEF\xBB\xBF')
                csv_year.write(csv_header)

            mon = '0{}'.format(str(month)) if month < 10 else str(month)

            if not os.path.isdir("./{0}/{1}".format(str(year), mon)):
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                continue
            os.chdir("{0}/{1}".format(str(year), mon))
            # current path : ./bb_data/YEAR/MONTH/

            # 파일 이름에 'bb.json'이 붙고 사이즈 1024byte 이상인 파일만 체크
            files = [f for f in os.listdir('.') if (os.path.isfile(f) and
                                                    (f.find('bb.json') > 0) and
                                                    (os.path.getsize(f) > 1024))
                     ]
            mon_file_num = len(files)

            if not mon_file_num > 0:
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                os.chdir('../../')
                # current path : ./bb_data/
                continue

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            if not os.path.isdir("./csv"):
                os.mkdir("./csv")

            csv_month_name = "./{0}_".format(str(year))
            if month < 10:
                csv_month_name = "{0}0".format(csv_month_name)
            csv_month_name = "{0}{1}.csv".format(csv_month_name, str(month))

            csv_month = open(csv_month_name, 'w')
            if is_windows:
                csv_month.write('\xEF\xBB\xBF')
            csv_month.write(csv_header)

            done = 0
            for f in files:
                js_in = open(f, 'r')
                js = json.loads(js_in.read(), 'utf-8')
                js_in.close()

                match_info = f[:15]

                # (5) open csv file
                csv_file = open('./csv/{0}.csv'.format(match_info), 'w')
                if is_windows:
                    csv_file.write('\xEF\xBB\xBF')
                csv_file.write(csv_header)

                write_csv(csv_file, csv_month, csv_year, js, match_info)

                csv_file.close()
                done += 1

                if mon_file_num > 30:
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               progress_pct * 100), end="")
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * done + '-' * (mon_file_num - done)
                    print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, done, mon_file_num,
                                                               float(done) / float(mon_file_num) * 100), end="")

            csv_month.close()
            print()
            print('        Converted {0} files'.format(str(done)))
            os.chdir('../../')
            # current path : ./bb_data/

        csv_year.close()
        # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print("JSON to CSV convert Done.")
