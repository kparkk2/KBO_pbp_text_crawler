#-*- coding: utf-8 -*-
#pbp_data_parser.py

import os
import sys
import csv
import json
import Queue
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

pos_convert =   {
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
            'review'    # 합의판정(이건 없어도 됨)
)

def parseResult( text ):
    # liveText를 종류 별로 나눈다.
    # 가장 기초적인 pitch 결과
    if searchUT( text, '구 볼'.decode('utf-8')):
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

def pbp_data_parser( mon_start, mon_end, year_start, year_end ):
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

        if not os.path.isdir("./" + str(year)):
            print os.getcwd()
            print "DOWNLOAD YEAR " + str(year) + " DATA FIRST"
            continue
        os.chdir( "./" + str(year) )
        # current path : ./pbp_data/YEAR/

        """
        # YEAR CSV 쓰는 건 나중에
        """

        for month in range(mon_start, mon_end+1):
            print "    Month " + str(month) + "... "
            i = 0
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
                if file_name.find( 'pbp' ) > 0:
                    mon_file_num += 1

            # 라인업 파일과 개수 비교. 라인업 텅 빈 파일은 parsing하지 않음.
            os.chdir( '../../../' )
            # current path : ./
            os.chdir( 'lineup_data/' + str(year) + '/' + str(month))
            # current path : ./lineup_data/YEAR/MONTH/
            lufiles = [f for f in os.listdir('.') if os.path.isfile(f)]
            lu_file_num = 0
            for lufile in lufiles:
                if lufile.find( 'lineup' ) > 0:
                    if os.path.getsize( lufile ) > 40:
                        lu_file_num += 1
            os.chdir( './' + str(year) + '/' + str(month) )

            if mon_file_num > lu_file_num:
                mon_file_num = lu_file_num

            if not mon_file_num > 0:
                print os.getcwd()
                print "DOWNLOAD MONTH " + str(month) + " DATA FIRST"
                os.chdir('..')
                # current path : ./pbp_data/YEAR/
                continue

            bar_prefix = '    Converting: '
            sys.stdout.write('\r%s[waiting]' % (bar_prefix)),

            # (4) 'csv' 폴더 생성
            if not os.path.isdir( "./csv" ):
                os.mkdir( "./csv" )

            """
            #MONTH FILE 쓰는 건 나중에
            """
            empty_files = 0

            # (5) 파일 별로 game structure 생성 시작
            for file_name in files:
                # 파일 이름에 'pbp_data'가 들어간 것만 대상으로.
                # 기존에 남아있던 CSV 출력 파일을 input으로 하지 않기 위함
                if file_name.find( 'pbp_data' ) <= 0:
                    continue

                lufile_name =

                # DOWNLOAD한 파일 중 내용이 텅 빈 것이 있음
                # 그런 것은 FILE SIZE로 걸러 냄
                if os.path.getsize( file_name ) > 1024:
                    lineup_filename = '../../../lineup_data/' + str(year) + '/' + str(month) + '/'
                    lineup_filename = lineup_filename + matchInfo + '_lineup.txt'
                    if os.path.getsize( lineup_filename ) < 100:
                        continue

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
                    # csv = open( './csv/' + csv_filename, 'w' )

                    #################################
                    ###### INSERT PLAYERS INFO ######
                    #################################
                    homeLineup = js['homeTeamLineUp']
                    awayLineup = js['awayTeamLineUp']

                    homebat = homeLineup['batter']
                    awaybat = awayLineup['batter']
                    homepit = homeLineup['pitcher']
                    awaypit = awayLineup['pitcher']

                    curOrder = 0
                    for i in range(len(homebat)):
                        bat = homebat[i]
                        name = bat['name'].encode('utf-8')
                        code = bat['pCode']
                        pos = pos_convert.get( bat['posName'].encode('utf-8') )
                        if pos == None:
                            print "pos error: " + bat['posName'].encode('utf-8')
                            print "matchInfo: " + matchInfo + " , home"
                            exit(1)

                        batThrows = bat['hitType']
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
                        '''
                        # 교체 여부
                        subIn = False
                        subOut = False
                        for key in bat.keys():
                            if key == 'cin':
                                subIn = True
                            elif key == 'cout':
                                subOut = True
                        # subOut이 True고 이따 라인업에서 이름 먼저 나오면 선발 출장.
                        '''

                        thisgame.addPlayer( name, code, pos, stands, throws )

                        # 미리 라인업을 설정
                        order = bat['batOrder']

                        if curOrder < order:
                            curOrder = order

                        # relay text에서는 선발로 나온 선수가 나중에 입력됨.
                        # setPlayer, setInOut 나중에 하는 선수가 lineup에 남기 때문에
                        # 선발/교체 상관없이 그냥 쭉쭉 해준다.
                        thisgame.lineup.setPlayer( 1, curOrder, pos, code )
                        thisgame.setInOut( 1, curOrder, code )

                    curOrder = 0
                    for i in range(len(awaybat)):
                        bat = awaybat[i]
                        name = bat['name'].encode('utf-8')
                        code = bat['pCode']
                        pos = pos_convert.get( bat['posName'].encode('utf-8') )
                        if pos == None:
                            print "pos error: " + bat['posName'].encode('utf-8')
                            print "matchInfo: " + matchInfo + " , home"
                            exit(1)

                        batThrows = bat['hitType']
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
                        '''
                        # 교체 여부
                        subInOut = False
                        for key in bat.keys():
                            if key == 'cin':
                                subInOut = True
                            elif key == 'cout':
                                subInOut = False
                        # subOut이 True고 이따 라인업에서 이름 먼저 나오면 선발 출장.
                        '''
                        thisgame.addPlayer( name, code, pos, stands, throws )

                        # 미리 라인업을 설정
                        order = bat['batOrder']

                        if curOrder < order:
                            curOrder = order

                        # relay text에서는 선발로 나온 선수가 나중에 입력됨.
                        # setPlayer, setInOut 나중에 하는 선수가 lineup에 남기 때문에
                        # 선발/교체 상관없이 그냥 쭉쭉 해준다.
                        thisgame.lineup.setPlayer( 0, curOrder, pos, code )
                        thisgame.setInOut( 0, curOrder, code )

                    addedStarter = False
                    for i in range(len(homepit)):
                        pit = homepit[i]
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

                        thisgame.addPlayer( name, code, 'p', stands, throws )
                        # 선발 투수는 라인업에서 이름 먼저 나온다.
                        # 때문에 처음 나온 선수만 setPitcher, setInOut 해준다.
                        if addedStarter == False:
                            thisgame.lineup.setPitcher( 1, code )
                            thisgame.setInOutPit( 1, code )
                            addedStarter = True

                    addedStarter = False
                    for i in range(len(awaypit)):
                        pit = awaypit[i]
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

                        thisgame.addPlayer( name, code, 'p', stands, throws )
                        # 선발 투수는 라인업에서 이름 먼저 나온다.
                        # 때문에 처음 나온 선수만 setPitcher, setInOut 해준다.
                        if addedStarter == False:
                            thisgame.lineup.setPitcher( 0, code )
                            thisgame.setInOutPit( 0, code )
                            addedStarter = True

                    ################################
                    ###### INSERT LINEUP INFO ######
                    ################################

                    # JSON 데이터에는 경기 마지막 포지션만 입력되어 있어서
                    # 경기 시작했을 때 포지션을 알 수 없다.
                    # LINEUP DATA에서 첫 포지션을 알 수 있다.
                    # 포지션 정보만 입력해준다.

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
                            lorder = ldata[0]
                            lpos = ldata[1]
                            if curorder < lorder:
                                curorder += 1
                                # 선발 선수 첫번째 포지션 수정
                                in_pos = lineup_pos_dict[ lpos.decode('utf-8')[0] ]
                                thisgame.lineup.setPos( 0, curorder, in_pos )

                        elif stage == 2:
                            if line.find('away_pit') >= 0:
                                stage = 3
                                continue
                            ldata = line.split(',')
                            lorder = ldata[0]
                            lpos = ldata[1]
                            if curorder < lorder:
                                curorder += 1
                                # 선발 선수 첫번째 포지션 수정
                                in_pos = lineup_pos_dict[ lpos.decode('utf-8')[0] ]
                                thisgame.lineup.setPos( 1, curorder, in_pos )
                        else:
                            break
                    lf.close()
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

                    thisgame.atBat.startGame()

                    ################################
                    ######     START GAME     ######
                    ################################

                    rtexts = js['relayTexts']
                    inn_max = int(js['currentInning'])

                    for inn in range(1, inn_max + 1):
                        rtext = rtexts[ str(inn) ]
                        textCount = len(rtext)

                        nextBat = False # 'n번 타자'가 나오면 True로 바꾼다. 타석 단위를 계산하기 위함.
                        for i in range(  ):
                            text = rtext[ textCount - i - 1 ]['liveText']
                            textLength = len(text)

                            tr = parseResult( text )
                            seqno = rtext[ textCount - i - 1 ]['seqno']

                            if tr == ts.ball:
                                thisgame.ball( seqno )
                            elif tr == ts.strike:
                                thisgame.strike( seqno )
                            elif tr == ts.foul:
                                thisgame.foul( seqno )
                            elif tr == ts.swstr:
                                thisgame.swstr( seqno )
                            elif tr == ts.buntfoul:
                                thisgame.buntfoul( seqno )
                            elif tr == ts.contact:
                                thisgame.contact( seqno )
                                # '타격' 자체로는 아무 결과도 이뤄지지 않는다.
                                # 그러나 타석의 종료를 의미한다.
                                # 다음 라인에 나오는 것으로 결과를 유추한다.
                            elif tr == ts.single:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.hit( 1, bblocation, seqno )
                            elif tr == ts.double:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.hit( 2, bblocation, seqno )
                            elif tr == ts.triple:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.hit( 3, bblocation, seqno )
                            elif tr == ts.homerun:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.homerun( bblocation, seqno )
                            elif tr == ts.hit:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.hit( 1, bblocation, seqno )
                            elif tr == ts.onbase:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')

                                # 타자 주자
                                # 출루 원인을 찾아야 한다.
                                # 출루; 땅볼, 실책, 야수선택, 타격방해, 희생번트(야수선택 or 실책), 희생플라이 실책
                                #       gb, err, fc, intf, bunterr, fberr

                                if searchUT( text, '타격방해'.decode('utf-8') ):
                                    thisgame.onbase( 'intf', bblocation, seqno )
                                elif searchUT( text, '실책'.decode('utf-8')):
                                    if searchUT( text, '번트'.decode('utf-8') ):
                                        thisgame.onbase( 'bunterr', bblocation, seqno )
                                    elif searchUT( text, '플라이'.decode('utf-8') ):
                                        thisgame.onbase( 'fberr', bblocation, seqno )
                                        # 일반 플라이 실책
                                    else:
                                        thisgame.onbase( 'err', bblocation, seqno )
                                        # 이외의 실책에 '좌익수 실책' 같은 게 섞여있다.
                                elif searchUT( text, '야수선택'.decode('utf-8') ):
                                    thisgame.onbase( 'fc', bblocation, seqno )
                                elif searchUT( text, '주루 포기'.decode('utf-8') ):
                                    # 땅볼 말고 주루포기.. ㅅㅂ...
                                    # 이 line 자체로는 아무 의미가 없으므로 넘어간다.
                                    continue
                                else:
                                    # 땅볼
                                    thisgame.onbase( 'gb', bblocation, seqno )
                                # 20160721NCSK 3회초 지석훈 타석: 번트타구 1-5C-6B 더블플레이
                                # 문자중계에서는 '땅볼로 출루(투수 2루 터치아웃)'으로 표기 - 오표기 혹은 함정데이터
                            elif tr == ts.lderror:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.onbase( 'lderror', bblocation, seqno )
                            elif tr == ts.advance:
                                text_splitted = text.split(' ')
                                pName = text_splitted[1].encode('utf-8')
                                # ~~~~~ 'n'루까지 진루
                                runfrom = text_splitted[0][0]
                                runto = -1
                                for i in range( len(text_splitted) ):
                                    if searchUT( text_splitted[i], '루까지'.decode('utf-8') ):
                                        runto = text_splitted[i][0]
                                        break
                                thisgame.advance( 1, runfrom, runto, pName, seqno )
                            elif tr == ts.moreadv:
                                text_splitted = text.split(' ')
                                pName = text_splitted[1].encode('utf-8')
                                # ~~~~~ 'n'루까지 진루
                                runfrom = text_splitted[0][0]
                                runto = -1
                                for i in range( len(text_splitted) ):
                                    if searchUT( text_splitted[i], '루까지'.decode('utf-8') ):
                                        if searchUT( text_splitted[i], 'FD'.decode('utf-8') ):
                                            runto = text_splitted[i][2]
                                        else:
                                            runto = text_splitted[i][0]
                                        break
                                if searchUT( text, '도루로'.decode('utf-8') ):
                                    thisgame.advance( 1, runfrom, runto, pName, seqno )
                                else:
                                    thisgame.advance( 0, runfrom, runto, pName, seqno )
                            elif tr == ts.homein:
                                text_splitted = text.split(' ')
                                runfrom = text_splitted[0][0]
                                pName = text_splitted[1].encode('utf-8')
                                thisgame.homein( runfrom, pName, seqno )
                            elif tr == ts.infield:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'infield', bblocation, seqno )
                            elif tr == ts.gbout:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'gb', bblocation, seqno )
                            elif tr == ts.fbout:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'fb', bblocation, seqno )
                            elif tr == ts.ldout():
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'ld', bblocation, seqno )
                            elif tr == ts.gidpout:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'gidp', bblocation, seqno )
                            elif tr == ts.tplay:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.out( 'tplay', bblocation, seqno )
                            elif tr == ts.sacfly:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.sacfly( bblocation, seqno )
                            elif tr == ts.sacbunt:
                                text_splitted = text.split(' ')
                                bblocation = text_splitted[2].encode('utf-8')
                                thisgame.sacbunt( bblocation, seqno )
                            elif tr == ts.threebunt:
                                thisgame.strikeout( 0, seqno )
                            elif tr == ts.strikeout:
                                thisgame.strikeout( 1, seqno )
                                # 0: 쓰리번트, 1: 삼진
                                # 타석의 종료.
                            elif tr == ts.notout:
                                if searchUT( text, '다른'.decode('utf-8')):
                                    thisgame.notout( 0, seqno )
                                elif searchUT( text, '포일'.decode('utf-8')):
                                    thisgame.notout( 0, seqno )
                                elif searchUT( text, '폭투'.decode('utf-8')):
                                    thisgame.notout( 0, seqno )
                                else:
                                    thisgame.notout( 1, seqno )
                                # 출루한 경우만 기록
                                # 0: 폭투/포일/다른주자 수비로 타자주자 출루 성공
                                # 1: 타자주자 아웃
                                # 타석의 종료.
                            elif tr == ts.walk:
                                thisgame.walk( 0, seqno )
                            elif tr == ts.ibb:
                                thisgame.walk( 1, seqno )
                            elif tr == ts.hbp:
                                thisgame.walk( 2, seqno )
                                # 0: 일반 볼넷, 1: 고의4구, 2: 몸에 맞는 공
                                # 타석의 종료.
                            # 포스아웃, 태그아웃, 터치아웃: 모두 주자의 아웃.
                            elif tr == ts.forceout:
                                text_splitted = text.split(' ')
                                runfrom = text_splitted[0][0]
                                pName = text_splitted[1].encode('utf-8')
                                thisgame.forceout( runfrom, pName, seqno )
                            elif tr == ts.tagout:
                                # (낫아웃)폭투사이 진루실패아웃도 있다.
                                # 진루실패아웃, 도루실패아웃
                                text_splitted = text.split(' ')
                                runfrom = text_splitted[0][0]
                                pName = text_splitted[1].encode('utf-8')
                                thisgame.tagout( runfrom, pName, seqno )
                            elif tr == ts.touchout:
                                text_splitted = text.split(' ')
                                runfrom = text_splitted[0][0]
                                pName = text_splitted[1].encode('utf-8')
                                thisgame.touchout( runfrom, pName, seqno )
                            elif tr == ts.batter:
                                # 교체(대타)인 경우 atBat의 정보와 lineup을 모두 수정
                                homeaway = thisgame.gameInfo.getInnTopbot()
                                if isTextIncludeSub(text):
                                    # n번타자 XXX : 대타 OOO (으)로 교체)
                                    # 0     1   2 3   4   5    6
                                    text_splitted = text.split(' ')
                                    newPlayer = text_splitted[4].encode('utf-8')
                                    newCode = thisgame.findCodeByName( newPlayer )
                                    order = text_splitted[0]
                                    thisgame.lineup.setPlayer( homeaway, order, 'ph', newCode )
                                    thisgame.atBat.changeBat( newCode )

                                # 타석이 종료될 때마다 포지션 개수 체크를 한다.
                                # 현재 경기에 출장 중인 타자 숫자가 9를 넘으면 안됨
                                checkPos = thisgame.lineup.checkPos( homeaway )
                                if checkPos == False:
                                    print 'BATTER > 9'
                                    thisgame.print_error_info()
                                    exit(1)
                                nextBat = True
                            elif tr == ts.sub:
                                # ~~~로 교체
                                text_splitted = text.split(' ')
                                oldName = text_splitted[1].encode('utf-8')
                                newPos = pos_convert.get(text_splitted[3].encode('utf-8'))
                                newName = text_splitted[4].encode('utf-8')

                                thisgame.substitute( oldName, newPos, newName )
                            elif tr == ts.change:
                                # 포지션 변경 ('위치 변경')
                                text_splitted = text.split(' ')
                                token = text_splitted[3]
                                token = newPosToken.split('(')
                                newPos = pos_convert.get(token[0].encode('utf-8'))
                                pName = text_splitted[1]
                                thisgame.change( pName, newPos )
                            elif tr == ts.innMid:
                                thisgame.gameInfo.setInnMid()
                            elif tr == ts.innEnd:
                                thisgame.gameInfo.setInnEnd()
                            else:
                                # 경기 중단, 비디오 판독, 합의판정, 기타 등등
                                print "###################################"
                                print text.encode('utf-8')
                                print "###################################"
                            # 이닝 텍스트 끝

                        # 혹시나 모를 상황 대비해서 이닝 종료
                        if thisgame.gameInfo.getInnTopbot() == 1:
                            thisgame.gameInfo.setInnEnd()

                        if thisgame.gameInfo.getInn() > inn_max:
                            thisgame.endGame()

                    # game over
