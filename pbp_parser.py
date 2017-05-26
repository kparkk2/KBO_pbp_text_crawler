# pbp_parser.py

import os
import json
import platform
import time
import logManager

# from baseball_game import gameData

pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수", "좌중간", "우중간"]

res_string = ["안타", "2루타", "3루타", "홈런", "실책", "땅볼",
              "뜬공", "희생플라이", "희생번트", "야수선택", "삼진",
              "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타"]

csv_header = '"date","inn","batterName","pitcherName",' \
             '"batterTeam","pitcherTeam","actual_result","result",' \
             '"gx","gy","pos1","pos2","pos3",' \
             '"pos4","pos5","pos6","pos7","pos8","pos9"\n'

'''
def write_csv(csv_file, csv_month, csv_year, game_id):
    write_data(csv_file, game_id)
    write_data(csv_month, game_id)
    write_data(csv_year, game_id)
'''


def pbp_parser(mon_start, mon_end, year_start, year_end, lm=None):
    if not os.path.isdir("./pbp_data"):
        print("DOWNLOAD DATA FIRST")
        exit(1)
    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("###### CONVERT PBP DATA(JSON) TO CSV FORMAT ######")
    print("##################################################")

    # check OS
    is_windows = (platform.system() == 'Windows')  # Win: True, Other: False

    for year in range(year_start, year_end + 1):
        print("  for Year " + str(year) + "...")

        if not os.path.isdir('./{0}'.format(str(year))):
            print(os.getcwd())
            print("DOWNLOAD YEAR {0} DATA FIRST".format(str(year)))
            continue

        csv_year = open("{0}/{1}.csv".format(str(year), str(year)), 'w')
        if is_windows:
            # csv_year.write('\xEF\xBB\xBF')
            csv_year.write('\n')
        csv_year.write(csv_header)

        for month in range(mon_start, mon_end + 1):
            print("  for Month {0}...".format(str(month)))

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

            # 파일 끝에 'pbp.json'이 붙고 사이즈 1024byte 이상인 파일만 체크
            files = [f for f in os.listdir('.') if (os.path.isfile(f) and
                                                    (f.find('pbp.json') > 0) and
                                                    (os.path.getsize(f) > 1024))]

            mon_file_num = len(files)

            if not mon_file_num > 0:
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                os.chdir('../../')
                # current path : ./pbp_data/
                continue

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            if not os.path.isdir("./csv"):
                os.mkdir("./csv")

            csv_month_name = "./{0}_{1}.csv".format(str(year), mon)

            csv_month = open(csv_month_name, 'w')
            if is_windows:
                # csv_month.write('\xEF\xBB\xBF')
                csv_month.write('')
            csv_month.write(csv_header)

            # write csv file for year
            # write csv file for month
            # csv column 목록
            # 날짜, 이닝+초말, 타자이름, 투수이름, 타자팀, 투수팀, 결과1, 결과2(상세), gx, gy, 포지션1-9

            # bb json 파일에서 매칭되는 목록 찾기
            # date, 타자이름, 투수이름, 이닝+초말

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            # crate log
            lm = logManager.LogManager()
            lm.setLogPath('{0}/log'.format(os.getcwd()))
            lm.setLogFileName('pbp_log.txt')
            lm.cleanLog()
            lm.createLogHandler()

            done = 0
            for f in files:
                # dummy code for debug
                js_in = open(f, 'r', encoding='utf-8')
                js = json.loads(js_in.read(), 'utf-8')
                js_in.close()

                done = done + 1
                time.sleep(10.0 / 1000.0)

                # (1) 초기 라인업 생성.
                # (2) 전체 라인업 목록 생성.
                # (3) 문자 로드.
                #   (3)-1. 교체 상황마다 라인업 교체.
                #   (3)-2. 타격시 포지션 기록.

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
                lm.log('print log test')
            csv_month.close()

            # kill log
            lm.killLogManager()

            print()
            print('        Converted {0} files.'.format(str(done)))
            os.chdir('../../')
            # return to pbp root dir
        csv_year.close()
