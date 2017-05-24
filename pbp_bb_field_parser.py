#-*- coding: utf-8 -*-
#pbp_bb_field_parser.py

import os
import sys
import csv
import json
import platform
from baseball_game import gameData

####################
#### relay text 한 line 단위로 event 계산
#### 1구 1구에 따른 pitch data만 계산
#### AB result는 결과 나온 line에서 계산
#### 타격/볼넷 결과는 바로 계산
#### 단, 타격/볼넷 결과 이후 추가 상황 발생할 때는
#### 진루 결과를 'n번 타자' line 전까지 queue에 몰아 넣고
#### line 위에서 아래 순서로 계산
####################
lineup_pos_dict =   {
                    u'\ud22c': 'p',     #'투'
                    u'\ud3ec' : 'c',    #'포'
                    u'\u4E00' : '1b',   #'一'
                    u'\u4E8C' : '2b',   #'二'
                    u'\u4E09' : '3b',   #'三'
                    u'\uc720' : 'ss',   #'유'
                    u'\uc88c' : 'lf',   #'좌'
                    u'\uc911' : 'cf',   #'중'
                    u'\uc6b0' : 'rf',   #'우'
                    u'\uC9C0' : 'dh',   #'지'
                    u'\uD0C0' : 'ph',   #'타'
                    u'\uC8FC' : 'pr'    #'주'
                }
    
pos_dict =   {
                    '투수': 'p',
                    '포수': 'c',
                    '1루수' : '1b',
                    '2루수' : '2b',
                    '3루수' : '3b',
                    '유격수' : 'ss',
                    '좌익수' : 'lf',
                    '중견수' : 'cf',
                    '우익수' : 'rf',
                    '지명타자' : 'dh',
                    '대타' : 'ph',
                    '대주자' : 'pr'
                }

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

def write_in_csv( filename, data, isComma ):
    filename.write( '"' + data + '"' )
    if isComma == True:
        filename.write( ',' )

def searchUT( text, target ):
    # searchUT = searchUnicodeText
    # text 안에 target 내용이 있는지 확인
    # text, target 모두 unicode 형식으로 들어와야함
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

ts = enum(  # ts: 'textSet'
            'ball',     # 볼
            'strike',   # 스트라이크
            'foul',     # 파울
            'swstr',    # 헛스윙; 번트헛스윙도 포함.
            'contact',  # 타격
            'single',   # 1루타
            'double',   # 2루타
            'triple',   # 3루타
            'homerun',  # 홈런
            'hit',      # 내야안타 & 번트안타
            'forceout', # 포스아웃; 주자만 기록. 타격시. '터치아웃'으로 기록
            'tagout',   # 태그아웃; 타격시(기록 없음), 도루실패아웃, 폭투사이 진루실패, 견제사아웃
            'touchout', # 터치아웃; 포스아웃 제외. 플라이/라이너 이후 귀루 실패시 그냥 '아웃'으로만 기록
            'onbase',   # 출루; 땅볼, 실책, 야수선택, 타격방해, 희생번트(야수선택 or 실책), 희생플라이 실책; 일반 '플라이 실책'('으로 출루'가 안 붙는다...)
            'advance',  # 진루; 일반적인 진루. 'n루주자 XXX : n루까지 진루' 형식을 지킨다.
            'moreadv',  # 추가 진루; 상황 설명이 붙는다. 폭투, 포일, 보크, 실책, (무관심)도루, 다른주자 수비 등
            'homein',   # 홈인; 타격, 볼넷, 실책, 폭투, 포일 등
            'lderror',  # 라인드라이브 실책; 보기 드물지만 존재한다...
            'infield',   # 인필드플라이 아웃; '플라이 아웃' 이전에 걸러내야 함
            'gbout',    # 땅볼 아웃; 송구아웃, 터치아웃, 태그아웃
            'fbout',    # 플라이 아웃; '플라이 아웃 (번트파울)' 이것도 있음
            'buntfoul', # 번트파울
            'ldout',    # 라인드라이브 아웃
            'gidpout',  # 병살타 아웃
            'tplay',    # 삼중살 아웃
            'sacfly',    # 희생플라이 아웃 + 희생플라이아웃 (띄어쓰기); 실책 출루와 구분되므로 그냥 '희생플라이'로 검색.
            'sacbunt',  # 희생번트 아웃
            'threebunt', # 쓰리번트 아웃
            'strikeout', # 삼진 아웃
            'notout',   # 낫아웃, 낫 아웃; 그냥 아웃(별 기록 없음), 폭투, 포일, 다른주자 수비
            'walk',     # 볼넷
            'ibb',      # 고의4구
            'hbp',      # 몸에 맞는 공
            'batter',   # n번타자
            'sub',      # 교체
            'change',   # 포변
            'innMid',   # n회초; 초공 종료
            'innEnd',   # n회말; 말공 종료
            'review',   # 합의판정(이건 없어도 됨)
            'others'    # 예외 상황
)

def parseResult( text ):
    # liveText를 종류 별로 나눈다.
    # 가장 기초적인 pitch 결과
    if searchUT( text, '경기 지연'.decode('utf-8')):
        return ts.others
    elif searchUT( text, '퇴장'.decode('utf-8')):
        return ts.others
    elif searchUT( text, '구 볼'.decode('utf-8')):
        return ts.ball
    elif searchUT( text, '구 스트라이크'.decode('utf-8')):
        return ts.strike
    elif searchUT( text, '구 파울'.decode('utf-8')):
        return ts.foul
    elif searchUT( text, '헛스윙'.decode('utf-8')):
        return ts.swstr
    elif searchUT( text, '타격'.decode('utf-8')):
        return ts.contact
    # 타자 결과
    elif searchUT( text, '1루타'.decode('utf-8')):
        return ts.single
    elif searchUT( text, '2루타'.decode('utf-8')):
        return ts.double
    elif searchUT( text, '3루타'.decode('utf-8')):
        return ts.triple
    elif searchUT( text, '홈런'.decode('utf-8')):
        return ts.homerun
    elif searchUT( text, '내야안타'.decode('utf-8')):
        return ts.hit
    elif searchUT( text, '번트안타'.decode('utf-8')):
        return ts.hit
    elif searchUT( text, '출루'.decode('utf-8')):
        return ts.onbase
    elif searchUT( text, '라인드라이브 실책'.decode('utf-8')):
        return ts.lderror
    elif searchUT( text, '인필드'.decode('utf-8')):
        return ts.infield
    elif searchUT( text, '땅볼 아웃'.decode('utf-8')):
        return ts.gbout
    elif searchUT( text, '플라이 아웃'.decode('utf-8')):
        return ts.fbout
    elif searchUT( text, '플라이 실책'.decode('utf-8')):
        return ts.onbase
    # 번트파울 플라이 아웃과 구분을 위해. 플라이 아웃이 아닌 번트파울만 따로 분류.
    elif searchUT( text, '번트파울'.decode('utf-8')):
        return ts.buntfoul
    elif searchUT( text, '병살타 아웃'.decode('utf-8')):
        return ts.gidpout
    elif searchUT( text, '삼중살'.decode('utf-8')):
        return ts.tplay
    elif searchUT( text, '희생플라이'.decode('utf-8')):
        return ts.sacfly
    elif searchUT( text, '희생번트 아웃'.decode('utf-8')):
        return ts.sacbunt
    elif searchUT( text, '라인드라이브 아웃'.decode('utf-8')):
        return ts.ldout
    elif searchUT( text, '쓰리번트'.decode('utf-8') ):
        return ts.threebunt
    elif searchUT( text, '삼진 아웃'.decode('utf-8')):
        return ts.strikeout
    elif searchUT( text, '볼넷'.decode('utf-8')):
        return ts.walk
    elif searchUT( text, '고의4구'.decode('utf-8')):
        return ts.ibb
    elif searchUT( text, '몸에'.decode('utf-8')):
        return ts.hbp
    elif searchUT( text, '낫아웃'.decode('utf-8')):
        return ts.notout
    elif searchUT( text, '낫 아웃'.decode('utf-8')):
        return ts.notout
    # 주자 결과
    elif searchUT( text, '포스아웃'.decode('utf-8')):
        return ts.forceout
    elif searchUT( text, '태그아웃'.decode('utf-8')):
        return ts.tagout
    elif searchUT( text, '터치아웃'.decode('utf-8')):
        return ts.touchout
    elif searchUT( text, '진루'.decode('utf-8')):
        text_splitted = text.split(' ')
        if len( text_splitted ) < 3:
            return -1
        elif searchUT( text_splitted[3], '루까지'.decode('utf-8')):
            if not searchUT( text_splitted[3], 'FD'.decode('utf-8') ):
                return ts.advance
            else:
                return ts.moreadv
        else:
            return ts.moreadv
    elif searchUT( text, '홈인'.decode('utf-8')):
        return ts.homein
    # 기타
    elif searchUT( text, '번타자'.decode('utf-8')):
        return ts.batter
    elif searchUT( text, '로 교체'.decode('utf-8')):
        return ts.sub
    elif searchUT( text, '위치 변경'.decode('utf-8')):
        return ts.change
    elif searchUT( text, '회초 '.decode('utf-8')):
        return ts.innMid
    elif searchUT( text, '회말'.decode('utf-8')):
        return ts.innEnd
    elif searchUT( text, '합의판정'.decode('utf-8')):
        return ts.review
    # 에러
    else:
        return -1

def isTextIncludeSub( text ):
    return searchUT( text, '로 교체'.decode('utf-8') )

def isTextShowOrder( text ):
    return searchUT( text, '번타자'.decode('utf-8') )

def try_print( result, matchInfo ):
    if result < 0:
        print
        print "matchInfo : " + matchInfo
        exit(1)

def pbp_bb_field_parser( mon_start, mon_end, year_start, year_end ):
    if not os.path.isdir("./pbp_data"):
        print "DOWNLOAD DATA FIRST"
        exit(1)
    os.chdir("./pbp_data")
    # current path : ./pbp_data/
    print "##################################################"
    print "###### CONVERT PBP DATA(JSON) TO CSV FORMAT ######"
    print "##################################################"

    isWindows = False # Win: True, Other: False
    # check OS
    if platform.system() == 'Windows':
        isWindows = True

    for year in range(year_start, year_end+1):
        print "  for Year " + str(year) + "..."
        # (1) YEAR 단위 경로로 이동

        csv_yearfilename = str(year) + '_pbp.csv'
        csv_yearfile = open( csv_yearfilename, 'w' )
        if isWindows:
            csv_yearfile.write( '\xEF\xBB\xBF' )
        csv_yearfile.write( '"seqno","inn","batterName","pitcherName",' )
        #csv_file.write( '"stands","throws",' )
        csv_yearfile.write( '"date","batterTeam","pitcherTeam",' )
        csv_yearfile.write( '"투수","포수",' )
        csv_yearfile.write( '"1루수","2루수",' )
        csv_yearfile.write( '"3루수","유격수",' )
        csv_yearfile.write( '"좌익수","중견수",' )
        csv_yearfile.write( '"우익수"\n' )

        if not os.path.isdir("./" + str(year)):
            print os.getcwd()
            print "DOWNLOAD YEAR " + str(year) + " DATA FIRST"
            continue
        os.chdir( "./" + str(year) )
        # current path : ./pbp_data/YEAR/

        for month in range(mon_start, mon_end+1):
            print "    Month " + str(month) + "... "
            done = 0
            mon_file_num = 0

            # (2) MONTH 단위 경로로 이동
            if not os.path.isdir( "./" + str(month) ):
                print os.getcwd()
                print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                continue
            os.chdir( "./" + str(month) )
            # current path : ./pbp_data/YEAR/MONTH/

            # (3) 파일 존재 여부 확인
            files = [f for f in os.listdir('.') if os.path.isfile(f)]

            for file_name in files:
                if file_name.find( 'pbp.json' ) > 0:
                    if os.path.getsize( file_name ) > 1024:
                        mon_file_num += 1

            if not mon_file_num > 0:
                print os.getcwd()
                print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                os.chdir('..')
                # current path : ./pbp_data/YEAR/
                continue

            bar_prefix = '    Converting: '
            sys.stdout.write('\r%s[waiting]' % (bar_prefix)),
            sys.stdout.flush()

            # (4) 'csv' 폴더 생성
            if not os.path.isdir( "./csv" ):
                os.mkdir( "./csv" )

            csv_monfilename = str(year) + '_' + str(month) + '_pbp.csv'
            csv_monfile = open( csv_monfilename, 'w' )
            if isWindows:
                csv_monfile.write( '\xEF\xBB\xBF' )
            csv_monfile.write( '"seqno","inn","batterName","pitcherName",' )
            #csv_file.write( '"stands","throws",' )
            csv_monfile.write( '"date","batterTeam","pitcherTeam",' )
            csv_monfile.write( '"투수","포수",' )
            csv_monfile.write( '"1루수","2루수",' )
            csv_monfile.write( '"3루수","유격수",' )
            csv_monfile.write( '"좌익수","중견수",' )
            csv_monfile.write( '"우익수"\n' )

            empty_files = 0

            # (5) 파일 별로 game structure 생성 시작
            for file_name in files:
                # 파일 이름에 'pbp_data'가 들어간 것만 대상으로.
                # 기존에 남아있던 CSV 출력 파일을 input으로 하지 않기 위함
                if file_name.find( 'pbp.json' ) <= 0:
                    continue

                # DOWNLOAD한 파일 중 내용이 텅 빈 것이 있음
                # 그런 것은 FILE SIZE로 걸러 냄
                if not os.path.getsize( file_name ) > 1024:
                    continue
                else:
                    # 파일 내용으로 JSON 객체 생성
                    js_in = open( file_name, 'r' )
                    js = json.loads( js_in.read(), 'utf-8' )
                    js_in.close()

                    # 경기에 해당하는 structure 생성
                    thisgame = gameData()

                    # 경기 일시/팀 이름
                    matchInfo = file_name.split('_pbp')[0]
                    match_date = matchInfo[0:8]
                    match_away = matchInfo[8:10]
                    match_home = matchInfo[10:12]

                    csv_filename = matchInfo + '_pbp.csv'
                    csv_file = open( './csv/' + csv_filename, 'w' )
                    if isWindows:
                        csv_file.write( '\xEF\xBB\xBF' )
                    csv_file.write( '"seqno","inn","batterName","pitcherName",' )
                    #csv_file.write( '"stands","throws",' )
                    csv_file.write( '"date","batterTeam","pitcherTeam",' )
                    csv_file.write( '"투수","포수",' )
                    csv_file.write( '"1루수","2루수",' )
                    csv_file.write( '"3루수","유격수",' )
                    csv_file.write( '"좌익수","중견수",' )
                    csv_file.write( '"우익수"\n' )

                    #################################
                    ###### INSERT PLAYERS INFO ######
                    #################################
                    homeLineup = js['homeTeamLineUp']
                    awayLineup = js['awayTeamLineUp']

                    homebat = homeLineup['batter']
                    awaybat = awayLineup['batter']
                    homepit = homeLineup['pitcher']
                    awaypit = awayLineup['pitcher']

                    for j in range(2):
                        batarray = []
                        if j == 0:
                            batarray = awaybat
                        else:
                            batarray = homebat

                        for i in range(len(batarray)):
                            bat = batarray[i]
                            name = bat['name'].encode('utf-8')
                            code = bat['pCode']

                            batThrows = bat['hitType']
                            stands = 0
                            throws = 0
                            # '투' 설정
                            if searchUT( batThrows, '좌투'.decode('utf-8') ):
                                throws = 1
                            elif searchUT( batThrows, '양투'.decode('utf-8') ):
                                throws = 2
                            else:
                                throws = 0

                            # '타' 설정
                            if searchUT( batThrows, '좌타'.decode('utf-8') ):
                                stands = 1
                            elif searchUT( batThrows, '양타'.decode('utf-8') ):
                                stands = 2
                            else:
                                stands = 0

                            try_print( thisgame.addPlayer( code, name, stands, throws, j ), matchInfo )

                            # relay text에서는 선발로 나온 선수가 나중에 입력됨.
                            # 입력이 들어오는 순서대로 lineup에 넣으면 자동적으로 선발 세팅됨.
                            # 단 포지션은 경기 마지막에 변경된 것만 입력에 남아있기 때문에
                            # 이 부분은 KBO 홈페이지에서 읽은 라인업 정보를 참조해서 변경해야.

                            pos = pos_dict.get( bat['posName'].encode('utf-8') )
                            if pos == None:
                                print "pos error: " + bat['posName'].encode('utf-8')
                                print "matchInfo: " + matchInfo + " , home"
                                exit(1)

                            order = bat['batOrder']
                            oldCode = thisgame.lineup.getOrderCode( j, order )
                            if oldCode > 0:
                                try_print( thisgame.setInOut( oldCode, False ), matchInfo )
                            try_print( thisgame.lineup.setPlayerInPos( j, order, pos, code ), matchInfo )

                    for j in range(2):
                        pitarray = []
                        if j == 0:
                            pitarray = awaypit
                        else:
                            pitarray = homepit

                        addedStarter = False
                        for i in range(len(pitarray)):
                            pit = pitarray[i]
                            name = pit['name'].encode('utf-8')
                            code = pit['pCode']
                            stands = 0
                            throws = 0
                            # '투' 설정
                            if searchUT( batThrows, '좌투'.decode('utf-8') ):
                                throws = 1
                            if searchUT( batThrows, '양투'.decode('utf-8') ):
                                throws = 2
                            else:
                                throws = 0

                            # '타' 설정
                            if searchUT( batThrows, '좌타'.decode('utf-8') ):
                                stands = 1
                            if searchUT( batThrows, '양타'.decode('utf-8') ):
                                stands = 2
                            else:
                                stands = 0

                            try_print( thisgame.addPlayer( code, name, stands, throws, j ), matchInfo )
                            # 선발 투수는 라인업에서 이름 먼저 나온다.
                            # 때문에 처음 나온 선수만 setPitcher, setInOut 해준다.
                            if addedStarter == False:
                                try_print( thisgame.lineup.setPitcher( j, code ), matchInfo )
                                addedStarter = True
                            else:
                                try_print( thisgame.setInOut( code, False ), matchInfo )

                    ################################
                    ###### INSERT LINEUP INFO ######
                    ################################
                    # JSON 데이터에는 경기 마지막 포지션만 입력되어 있어서
                    # 경기 시작했을 때 포지션을 알 수 없다.
                    # LINEUP DATA에서 첫 포지션을 알 수 있다.
                    # 포지션 정보만 입력해준다.

                    os.chdir( '../../../' )
                    # current path : ./
                    os.chdir( 'lineup_data/' + str(year) + '/' + str(month))
                    # current path : ./lineup_data/YEAR/MONTH/
                    lineup_filename = matchInfo + '_lineup.txt'
                    lf = open(lineup_filename, 'r')
                    lines = lf.readlines()
                    stage = 0   # 1: away bat, 2: home bat, >3: pitcher
                    curorder = 0

                    for line in lines:
                        if stage == 0:
                            if line.find('away_bat') >= 0:
                                stage = 1
                                continue
                        elif stage == 1:
                            if line.find('home_bat') >= 0:
                                stage = 2
                                curorder = 0
                                continue
                            ldata = line.split(',')
                            lorder = int(ldata[0])
                            lpos = ldata[1]
                            if curorder < lorder:
                                curorder += 1
                                # 선발 선수 첫번째 포지션 수정
                                in_pos = lineup_pos_dict[ lpos.decode('utf-8')[0] ]
                                try_print( thisgame.lineup.setPosOfOrder( 0, curorder, in_pos ), matchInfo )

                        elif stage == 2:
                            if line.find('away_pit') >= 0:
                                stage = 3
                                continue
                            ldata = line.split(',')
                            lorder = int(ldata[0])
                            lpos = ldata[1]
                            if curorder < lorder:
                                curorder += 1
                                # 선발 선수 첫번째 포지션 수정
                                in_pos = lineup_pos_dict[ lpos.decode('utf-8')[0] ]
                                try_print( thisgame.lineup.setPosOfOrder( 1, curorder, in_pos ), matchInfo )
                        else:
                            break
                    lf.close()

                    # get lineup done
                    os.chdir( '../../../' )
                    os.chdir( 'pbp_data/' + str(year) + '/' + str(month) )
                    # current path : ./pbp_data/YEAR/MONTH/

                    #################################
                    ######    SET GAME INFO    ######
                    #################################

                    inputGameInfo = js['gameInfo']
                    thisgame.gameInfo.setStadium( inputGameInfo['stadium'].encode('utf-8') )
                    thisgame.gameInfo.setHome( inputGameInfo['hCode'] )
                    thisgame.gameInfo.setAway( inputGameInfo['aCode'] )
                    thisgame.gameInfo.setDate( inputGameInfo['gdate'] )

                    #################################
                    ######   INIT ATBAT INFO   ######
                    #################################

                    thisgame.startGame()

                    ################################
                    ######     START GAME     ######
                    ################################
                    innmax = 0
                    rtexts = js['relayTexts']
                    for key in rtexts.keys():
                        if key.isdigit():
                            if innmax < int(key):
                                innmax = int(key)

                    for inn in range( 1, innmax+1 ):
                        rtext = rtexts[ str(inn) ]
                        textCount = len(rtext)

                        for i in range( textCount ):
                            text = rtext[ textCount - i - 1 ]['liveText']
                            textLength = len(text)

                            tr = parseResult( text )
                            if tr == ts.sub:
                                # ~~~로 교체
                                text_splitted = text.split(' ')
                                oldPos = pos_dict.get(text_splitted[0].encode('utf-8'))
                                oldName = text_splitted[1].encode('utf-8')
                                newPos = pos_dict.get(text_splitted[3].encode('utf-8'))
                                newName = text_splitted[4].encode('utf-8')
                                if newName.find('(') >= 0:
                                    newName = newName.split('(')[0]

                                if searchUT( text, '주자'.decode('utf-8') ):
                                    oldPos = text_splitted[0].encode('utf-8')
                                try_print( thisgame.subs( oldPos, oldName, newPos, newName ), matchInfo )
                            elif tr == ts.change:
                                # 포지션 변경 ('위치 변경')
                                text_splitted = text.split(' ')
                                pName = text_splitted[1].encode('utf-8')
                                oldPos = pos_dict.get(text_splitted[0].encode('utf-8'))
                                token = text_splitted[3].split('(')
                                newPos = pos_dict.get(token[0].encode('utf-8'))
                                try_print( thisgame.change( pName, oldPos, newPos ), matchInfo )
                            elif tr == ts.batter:
                                # n번타자
                                text_splitted = text.split(' ')
                                order = int(text_splitted[0][0])
                                oldName = text_splitted[1].encode('utf-8')
                                if searchUT( text, '대타'.decode('utf-8') ):
                                    newPos = 'ph'
                                    newName = text_splitted[4].encode( 'utf-8' )
                                    if newName.find('(') >= 0:
                                        newName = newName.split('(')[0]
                                    oldPos = str(order)
                                    try_print( thisgame.subs( oldPos, oldName, newPos, newName ), matchInfo )
                                    thisgame.setAtBat( order, newName )
                                else:
                                    thisgame.setAtBat( order, oldName )
                                seqno = rtext[ textCount - i - 1 ]['seqno']
                                csv_file.write( thisgame.printBBData( seqno ) )
                                csv_monfile.write( thisgame.printBBData( seqno ) )
                                csv_yearfile.write( thisgame.printBBData( seqno ) )
                                thisgame.nextAtBat()
                                thisgame.resetPBP()
                            elif tr == ts.innEnd:
                                # n회말 XX 공격 종료
                                thisgame.setInnEnd()
                                thisgame.nextAtBat()
                                thisgame.resetPBP()
                            elif tr == ts.innMid:
                                # n회초 XX 공격 종료
                                thisgame.setInnMid()
                                thisgame.nextAtBat()
                                thisgame.resetPBP()
                            # 이닝 텍스트 끝

                        # 혹시나 모를 상황 대비해서 이닝 종료
                        if thisgame.gameInfo.getInnTopbot() == 1:
                            thisgame.setInnEnd()
                            thisgame.nextAtBat()
                            thisgame.resetPBP()

                        if thisgame.gameInfo.getInn() > innmax:
                            thisgame.endGame()

                done = done + 1

                if mon_file_num > 30 :
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, progress_pct*100)),
                    sys.stdout.flush()
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * done + '-' * (mon_file_num - done)
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, float(done)/float(mon_file_num)*100)),
                    sys.stdout.flush()

                    # game over
                    csv_file.close()
            csv_monfile.close()
            print

            os.chdir('..')
            # current path : ./pbp_data/YEAR/

        csv_yearfile.close()
        os.chdir('..')
        # current path : ./pbp_data/
