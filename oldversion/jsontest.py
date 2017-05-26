#jsontest.py
#-*- coding: utf-8 -*-
import os
import sys
import json
import platform

def searchUT( text, target ):
    # text 안에 target 내용이 있는지 확인
    l = len(text)
    t = len(target)
    pos = 0
    found = False
    # 012345678 / 0123 -> 9 - 4 = 5, 5 넘으면 gg
    for i in range( len(text) ):
        if text[i] == target[pos]:
            pos += 1
            if pos == t:
                found = True
                break
        else:
            pos = 0
    return found

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

textSet = enum(
            'review',   # 합의판정
            'ball',     # 볼
            'strike',   # 스트라이크
            'swstr'     # 헛스윙
            'contact',  # 타격
            'onbase',   # 출루; 땅볼, 실책, 야수선택, 타격방해
            'advance',  # 진루; 타격, 볼넷, 실책, 폭투, 포일, 다른주자수비 등
            'homein',   # 홈인; 타격, 볼넷, 실책, 폭투, 포일 등
            'gbout',    # 땅볼 아웃; 송구아웃, 터치아웃, 태그아웃
            'fbout',    # 플라이 아웃
            'ldout',    # 라인드라이브 아웃
            'strikeout', # 삼진 아웃
            'notout',   # 낫아웃; 진루한 경우만 기록됨. 폭투, 포일, 다른주자 수비
            'walk',     # 볼넷
            'forceout', # 포스아웃; 주자만 기록. 타격시. '터치아웃'으로 기록
            'tagout',   # 태그아웃; 타격시(기록 없음), 도루실패아웃, 폭투사이 진루실패, 견제사아웃
            'touchout' # 터치아웃; 포스아웃 제외. 플라이/라이너 이후 귀루 실패시 그냥 '아웃'으로만 기록
)

def pbp_data_json_to_csv( mon_start, mon_end, year_start, year_end ):
    if not os.path.isdir("./pbp_data"):
        print "DOWNLOAD DATA FIRST"
        exit(1)
    os.chdir("./pbp_data")
    # current path : ./pbp_data/
    isWindows = False # Win: True, Other: False
    # check OS
    if platform.system() == 'Windows':
        isWindows = True

    for year in range(year_start, year_end+1):
        #print "  for Year " + str(year) + "..."
        # (1) move into YEAR dir

        if not os.path.isdir("./" + str(year)):
            #print os.getcwd()
            #print "DOWNLOAD YEAR " + str(year) + " DATA FIRST"
            continue
        os.chdir( "./" + str(year) )
        # current path : ./pbp_data/YEAR/

        for month in range(mon_start, mon_end+1):
            #print "    Month " + str(month) + "... "
            i = 0
            mon_file_num = 0

            # (2) move into MONTH dir
            if not os.path.isdir( "./" + str(month) ):
                #print os.getcwd()
                #print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                continue
            os.chdir( "./" + str(month) )
            # current path : ./pbp_data/YEAR/MONTH/

            # (3) check if file exists
            files = [f for f in os.listdir('.') if os.path.isfile(f)]

            for file_name in files:
                if file_name.find( 'pbp' ) > 0:
                    mon_file_num += 1

            if not mon_file_num > 0:
                #print os.getcwd()
                #print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                os.chdir('..')
                # current path : ./pbp_data/YEAR/
                continue

            # (4) create 'csv' folder
            if not os.path.isdir( "./csv" ):
                os.mkdir( "./csv" )

            empty_files = 0
            for file_name in files:
                if file_name.find( 'pbp' ) <= 0:
                    continue

                if os.path.getsize( file_name ) > 1024:
                    js_in = open( file_name, 'r' )
                    js = json.loads( js_in.read(), 'utf-8' )
                    js_in.close()

                    matchInfo = file_name.split('_pbp')[0]
                    match_date = matchInfo[0:8]
                    match_away = matchInfo[8:10]
                    match_home = matchInfo[10:12]

                    #print 'Date : ' + match_date
                    #print 'home : ' + match_home + ' / away : ' + match_away

                    k = 10
                    if k == 10:
                        # Relay Text
                        rts = js['relayTexts']
                        innmax = 0
                        for key in rts.keys():
                            if key.isdigit():
                                if innmax < int(key):
                                    innmax = int(key)

                        for i in range( 1, innmax+1 ):
                            rt = rts[str(i)]
                            rtlen = len(rt)
                            for j in range(len(rt)):
                                text = rt[rtlen - j - 1]['liveText']

                                asdf = 2
                                if asdf == 1:
                                    print text.encode('utf-8')
                                else:
                                    if searchUT( text, '지명타자'.decode('utf-8') ):
                                        if searchUT( text, '수비위치'.decode('utf-8') ):
                                            print text.encode('utf-8')
                                            print matchInfo
                                            print str(i) + '이닝'

                    jj = 1
                    if jj == 10:
                        hl = js['homeTeamLineUp']
                        al = js['awayTeamLineUp']

                        hb = hl['batter']
                        ab = al['batter']

                        for num in range(len(hb)):
                            bat = hb[num]
                            for key in bat.keys():
                                if key == 'cin':
                                    print bat['name'].encode('utf-8') + ' / cin: ' + bat[key].encode('utf-8')
                                    print matchInfo
                                elif key == 'cout':
                                    print bat['name'].encode('utf-8') + ' / cout: ' + bat[key].encode('utf-8')
                                    print matchInfo

                        for num in range(len(ab)):
                            bat = ab[num]
                            for key in bat.keys():
                                if key == 'cin':
                                    print bat['name'].encode('utf-8') + ' / cin: ' + bat[key].encode('utf-8')
                                    print matchInfo
                                elif key == 'cout':
                                    print bat['name'].encode('utf-8') + ' / cout: ' + bat[key].encode('utf-8')
                                    print matchInfo

            os.chdir('..')
        os.chdir('..')

if __name__ == "__main__":
    pbp_data_json_to_csv(4,4, 2016, 2016)
