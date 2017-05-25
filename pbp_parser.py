import os
# import sys
# import csv
# import json
import platform
import time
# from baseball_game import gameData


def pbp_parser(mon_start, mon_end, year_start, year_end):
    if not os.path.isdir("./pbp_data"):
        print("DOWNLOAD DATA FIRST")
        exit(1)
    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("###### CONVERT PBP DATA(JSON) TO CSV FORMAT ######")
    print("##################################################")

    # check OS
    isWindows = (platform.system() == 'Windows')  # Win: True, Other: False

    for year in range(year_start, year_end+1):
        if not os.path.isdir('./{0}'.format(str(year))):
            print(os.getcwd())
            print("DOWNLOAD YEAR {0} DATA FIRST".format(str(year)))
            continue

        print("  for Year " + str(year) + "...")

        for month in range(mon_start, mon_end+1):
            if not os.path.isdir('./{0}/{1}'.format(str(year), str(month))):
                print(os.getcwd())
                print("DOWNLOAD MONTH {0} DATA FIRST".format(str(month)))
                continue

            print("  for Month {0}...".format(str(month)))

            os.chdir('./{0}/{1}'.format(str(year), str(month)))

            # 파일 끝에 'pbp.json'이 붙고 사이즈 1024byte 이상인 파일만 체크
            files = [f for f in os.listdir('.') if (os.path.isfile(f) and
                                                    (f.find('pbp.json')>0) and
                                                    (os.path.getsize(f) > 1024))]

            mon_file_num = sum(1 for f in files)

            # write csv file for year
            # write csv file for month

            bar_prefix = '    Converting: '
            print('\r{}[waiting]'.format(bar_prefix), end="")

            done = 0
            for f in files:
                done = done + 1
                time.sleep(5.0 / 1000.0)

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
            print('        Converted {0} files.'.format(str(done)))
            os.chdir('../../')
            # return to pbp root dir
