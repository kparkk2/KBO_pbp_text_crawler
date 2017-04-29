#-*- coding: utf-8 -*-
#bb_data_json_to_csv.py
#
# IN: year/month - target match time period
# OUT: CSV files for target match time period
#
#(1) read each JSON files.
#(2) load JSON data structure.
#(3) reconstruct as string list.
#(4) dump to the CSV file.

import os
import sys
import csv
import json
import random
import platform

positions = [ \
    #투수, 포수, 1루수, 2루수
    u'\ud22c\uc218', u'\ud3ec\uc218', u'1\ub8e8\uc218', u'2\ub8e8\uc218', \
    #3루수, 유격수, 좌익수, 중견수
    u'3\ub8e8\uc218', u'\uc720\uaca9\uc218', u'\uc88c\uc775\uc218', u'\uc911\uacac\uc218', \
    #우익수, 좌중간, 우중간
    u'\uc6b0\uc775\uc218', u'\uc88c\uc911\uac04', u'\uc6b0\uc911\uac04' ]

results = [ \
    #1루타, 2루타, 3루타, 홈런, 실책
    u'1\uB8E8\uD0C0', u'2\uB8E8\uD0C0', u'3\uB8E8\uD0C0', u'\uD648\uB7F0', u'\uC2E4\uCC45', \
    #땅볼, 플라이 아웃, 희생플라이
    u'\uB545\uBCFC', u'\uD50C\uB77C\uC774 \uC544\uC6C3', u'\uD76C\uC0DD\uD50C\uB77C\uC774', \
    #희생번트, 야수선택, 삼진
    u'\uD76C\uC0DD\uBC88\uD2B8', u'\uC57C\uC218\uC120\uD0DD', u'\uC0BC\uC9C4', \
    #스트라이크(낫 아웃), 타격방해
    u'\uC2A4\uD2B8\uB77C\uC774\uD06C', u'\uD0C0\uACA9\uBC29\uD574',\
    #라인드라이브, 병살타
    u'\uB77C\uC778\uB4DC\uB77C\uC774\uBE0C', u'\uBCD1\uC0B4\uD0C0',\
    #번트(일반), 내야안타
    u'\uBC88\uD2B8', u'\uB0B4\uC57C\uC548\uD0C0' ]


def find_pos( detailResult, num ):
    position = positions[num]

    pos_index = 0
    for i in range( len(detailResult) ):
        if ( position[pos_index] == detailResult[i] ):
            pos_index = pos_index + 1
            if pos_index == len(position):
                break
        else:
            pos_index = 0

    if pos_index == len(position):
        return True
    else:
        return False

def find_result( detailResult, num ):
    result = results[num]

    res_index = 0
    for i in range( len(detailResult) ):
        if ( result[res_index] == detailResult[i] ):
            res_index = res_index + 1
            if res_index == len(result):
                break
        else:
            res_index = 0

    if res_index == len(result):
        return True
    else:
        return False

def get_team( team_name ):
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

pos_string = [ "투수", "포수", "1루수", "2루수", "3루수", "유격수", "좌익수", "중견수", "우익수", "좌중간", "우중간" ]

res_string = ["안타", "2루타", "3루타", "홈런", "실책", "땅볼", "뜬공", "희생플라이", "희생번트", "야수선택", "삼진", "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타" ]

def write_in_csv( filename, data, isComma ):
    filename.write( '"' + data + '"' )
    if isComma == True:
        filename.write( ',' )

def write_balls( ball_ids, csv_file, js, matchInfo, year, isHome ):
    homeaway = ''
    if isHome == True:
        homeaway = 'home'
    else:
        homeaway = 'away'

    match_date = matchInfo[0:8]
    match_away = matchInfo[8:10]
    match_home = matchInfo[10:12]

    for ball in ball_ids:
        ball_key = str(ball)
        batterName = js['ballsInfo'][homeaway][ball_key]['batterName']
        pitcherName = js['ballsInfo'][homeaway][ball_key]['pitcherName']
        result = js['ballsInfo'][homeaway][ball_key]['result']
        gx = js['ballsInfo'][homeaway][ball_key]['gx']
        gy = js['ballsInfo'][homeaway][ball_key]['gy']
        detailResult = js['ballsInfo'][homeaway][ball_key]['detailResult']
        inn = js['ballsInfo'][homeaway][ball_key]['inn']
        date = str(match_date[0:4]) + '-' + str(match_date[4:6]) + '-' + str(match_date[6:8])
        seqno = js['ballsInfo'][homeaway][ball_key]['seqno']
        batterTeam = match_away
        pitcherTeam = match_home

        fielder_position = ""
        actual_result = ""

        for i in range( len(pos_string) ):
            if find_pos( detailResult, i ) == True:
                fielder_position = pos_string[i]
                break

        for i in range( len(res_string) ):
            if find_result ( detailResult, i ) == True:
                actual_result = res_string[i]
                # strike out, not out, interference -> no fielder
                if i == 10 or i == 11 or i == 12:
                    fielder_position = ""
                break

        batterName = batterName.encode('utf-8')
        pitcherName = pitcherName.encode('utf-8')
        result = result.encode('utf-8')
        inn = inn.encode('utf-8')
        """
	# TO ADD RANDOM NUMBERS TO X/Y COORDINATE, INCLUDE CODES BELOW:
        rx = random.randrange( 1, 11 ) * random.choice( [-1, 1] )
        ry = random.randrange( 1, 11 ) * random.choice( [-1, 1] )
        if not ( (gx == 0) and (gy == 0) ):
            gx = gx + rx
            gy = gy + ry
	# (COMMENTED)
        """
        write_in_csv( csv_file, batterName, True )
        write_in_csv( csv_file, pitcherName, True )
        write_in_csv( csv_file, inn, True )
        write_in_csv( csv_file, str(gx), True )
        write_in_csv( csv_file, str(gy), True )
        write_in_csv( csv_file, fielder_position, True )
        write_in_csv( csv_file, actual_result, True )
        write_in_csv( csv_file, result, True )
        write_in_csv( csv_file, date, True )
        write_in_csv( csv_file, get_team( batterTeam ), True )
        write_in_csv( csv_file, get_team( pitcherTeam ), True )
        write_in_csv( csv_file, str(seqno), False )
        csv_file.write('\n')


def bb_data_json_to_csv( mon_start, mon_end, year_start, year_end ):
    if not os.path.isdir("./bb_data"):
        print "DOWNLOAD DATA FIRST"
        exit(1)
    os.chdir("./bb_data")
    # current path : ./bb_data/
    print "##################################################"
    print "###### CONVERT BB DATA(JSON) TO CSV FORMAT #######"
    print "##################################################"

    isWindows = False # Win: True, Other: False
    # check OS
    if platform.system() == 'Windows':
        isWindows = True

    for year in range(year_start, year_end+1):
        print "  for Year " + str(year) + "..."
        # (1) move into YEAR dir

        if not os.path.isdir("./" + str(year)):
            print os.getcwd()
            print "DOWNLOAD YEAR " + str(year) + " DATA FIRST"
            continue
        os.chdir( "./" + str(year) )
        # current path : ./bb_data/YEAR/

        csv_year_filename = str(year) + ".csv"
        csv_year_file = open( csv_year_filename, 'w' )
        if isWindows:
            csv_year_file.write( '\xEF\xBB\xBF' )
        csv_year_file.write( '"batterName","pitcherName","inn","gx","gy","fielder_position","actual_result","result","date","batterTeam","pitcherTeam","seqno"\n')

        for month in range(mon_start, mon_end+1):
            print "    Month " + str(month) + "... "
            i = 0
            mon_file_num = 0

            # (2) move into MONTH dir
            if not os.path.isdir( "./" + str(month) ):
                print os.getcwd()
                print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                continue
            os.chdir( "./" + str(month) )
            # current path : ./bb_data/YEAR/MONTH/

            # (3) check if file exists
            files = [f for f in os.listdir('.') if os.path.isfile(f)]

            for file_name in files:
                if file_name.find( 'bb_data' ) > 0:
                    mon_file_num += 1

            if not mon_file_num > 0:
                print os.getcwd()
                print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                os.chdir('..')
                # current path : ./bb_data/YEAR/
                continue

            bar_prefix = '    Converting: '
            sys.stdout.write('\r%s[waiting]' % (bar_prefix)),

            # (4) create 'csv' folder
            if not os.path.isdir( "./csv" ):
                os.mkdir( "./csv" )

            csv_month_filename = ""
            if month < 10:
                csv_month_filename = "./" + str(year) + "_0" + str(month) + ".csv"
            else:
                csv_month_filename = "./" + str(year) + "_" + str(month) + ".csv"
            csv_month_file = open( csv_month_filename, 'w' )
            if isWindows:
                csv_month_file.write( '\xEF\xBB\xBF' )
            csv_month_file.write( '"batterName","pitcherName","inn","gx","gy","fielder_position","actual_result","result","date","batterTeam","pitcherTeam","seqno"\n')

            empty_files = 0
            for file_name in files:
                if file_name.find( 'bb_data' ) <= 0:
                    continue

                if os.path.getsize( file_name ) > 1024:
                    js_in = open( file_name, 'r' )
                    js = json.loads( js_in.read(), 'utf-8' )
                    js_in.close()

                    matchInfo = file_name.split('_bb')[0]
                    match_date = matchInfo[0:8]
                    match_away = matchInfo[8:10]
                    match_home = matchInfo[10:12]

                    # (5) open csv file
                    csv_file = open( './csv/' + matchInfo + '_bb.csv', 'w')
                    if isWindows:
                        csv_file.write( '\xEF\xBB\xBF' )
                    csv_file.write( '"batterName","pitcherName","inn","gx","gy","fielder_position","actual_result","result","date","batterTeam","pitcherTeam","seqno"\n')

                    # away first
                    hr_id = js['teamsInfo']['away']['hr']
                    hit_id = js['teamsInfo']['away']['hit']
                    o_id = js['teamsInfo']['away']['o']

                    write_balls( hr_id, csv_file, js, matchInfo, year, False )
                    write_balls( hit_id, csv_file, js, matchInfo, year, False )
                    write_balls( o_id, csv_file, js, matchInfo, year, False )

                    write_balls( hr_id, csv_month_file, js, matchInfo, year, False )
                    write_balls( hit_id, csv_month_file, js, matchInfo, year, False )
                    write_balls( o_id, csv_month_file, js, matchInfo, year, False )

                    write_balls( hr_id, csv_year_file, js, matchInfo, year, False )
                    write_balls( hit_id, csv_year_file, js, matchInfo, year, False )
                    write_balls( o_id, csv_year_file, js, matchInfo, year, False )

                    # home next
                    hr_id = js['teamsInfo']['home']['hr']
                    hit_id = js['teamsInfo']['home']['hit']
                    o_id = js['teamsInfo']['home']['o']

                    write_balls( hr_id, csv_file, js, matchInfo, year, True )
                    write_balls( hit_id, csv_file, js, matchInfo, year, True )
                    write_balls( o_id, csv_file, js, matchInfo, year, True )

                    write_balls( hr_id, csv_month_file, js, matchInfo, year, True )
                    write_balls( hit_id, csv_month_file, js, matchInfo, year, True )
                    write_balls( o_id, csv_month_file, js, matchInfo, year, True )

                    write_balls( hr_id, csv_year_file, js, matchInfo, year, True )
                    write_balls( hit_id, csv_year_file, js, matchInfo, year, True )
                    write_balls( o_id, csv_year_file, js, matchInfo, year, True )

                    csv_file.close()
                    i += 1

                else:
                    i += 1
                    empty_files += 1

                if mon_file_num > 30 :
                    progress_pct = (float(i) / float(mon_file_num))
                    bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                    sys.stdout.write('\r%s[%s] %s / %s, %2.1f %%' % (bar_prefix, bar, i, mon_file_num, progress_pct*100)),
                    sys.stdout.flush()
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * i + '-' * (mon_file_num - i)
                    sys.stdout.write('\r%s[%s] %s / %s, %2.1f %%' % (bar_prefix, bar, i, mon_file_num, float(i)/float(mon_file_num)*100)),
                    sys.stdout.flush()

            csv_month_file.close()
            sys.stdout.write('\n')
            sys.stdout.flush()
            print '        Converted ' + str(i) + ' files',
            print '(' + str(empty_files) + ' files empty)'
            os.chdir('..')
            # current path : ./bb_data/YEAR/

        csv_year_file.close()
        os.chdir('..')
        # current path : ./bb_data/
    os.chdir('..')
    # current path : ./
    print "JSON to CSV convert Done."
