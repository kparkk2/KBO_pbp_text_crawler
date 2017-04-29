#-*- coding: utf-8 -*-
#baseball_game.py

import os
import sys
import csv
import json
import Queue
from onBase import _onBase
from lineup import _lineup
from atBat import _atBat
from gameInfo import _gameInfo

pos_dict =  {
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

# 타구 결과물
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

bb_location = [ "투수", "포수", "1루수", "2루수", "3루수", "유격수", "좌익수", "중견수", "우익수", "좌중간", "우중간" ]

res_string = ["안타", "2루타", "3루타", "홈런", "실책", "땅볼", "뜬공", "희생플라이", "희생번트", "야수선택", "삼진", "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타" ]

stadium_string = ['잠실', '고척', '문학', '대전', '대구', '사직', '광주', '마산', '수원', '청주', '울산', '포항', '목동', '시민', '무등']

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

class pbpdata:
    def __init__( self ):
        self.dict = {
                    'inn': 0,
                    'topbot': '초',
                    'homescore': 0,
                    'awayscore': 0,
                    'batName': '',
                    'pitName': '',
                    'ball': 0,
                    'strike': 0,
                    'out': 0,
                    'onbase1': '',
                    'onbase2': '',
                    'onbase3': '',
                    'event': '',       # PA result. actual_result; 타석의 최종 결과(안타, 2루타 등)
                    'description': '',  # pitch by pitch result; 볼, 스트, 파울, 헛스윙, 인플레이
                    'bs': 'X',          # 볼/스트. 각각 B/S로 표기. 인플레이는 X. description에 따라서 설정
                    'bb_type' : '',     # batted ball type; 뜬공, 직선타, 땅볼, 없음('')
                    'field_pos': '',     # 공 잡은 수비수 포지션. 한글 표기
                    'field_name': '',    # 공 잡은 수비수 이름. 한글 표기
                    'result': '',       # 결과를 안타, 아웃, 홈런, 실책, 볼넷, 사구, 야수선택, 없음('')으로만 분류(타구 분포 분석 용도)
                    'stands': 'R',
                    'throws': 'R',
                    'date': '20160101',
                    'batTeam': 'OB',
                    'pitTeam': 'LG',
                    'seqno': 0         # livetext의 시퀀스 넘버. BB DATA와 비교하기 위함. 타석 마무리 시(삼진/볼넷/인플레이)에만 기록
        }

    def getData( self, key ):
        return self.dict.get(key)

    def setData( self, key, value ):
        self.dict[key] = value

    def printBBData( self ):
        text = '"' + str(self.dict.get('inn')) + '회' + self.dict.get('topbot') + '"'
        text += ',"' + self.dict.get('batName') + '"'
        text += ',"' + self.dict.get('pitName') + '"'
        #text += ',"' + self.dict.get('stands') + '"'
        #text += ',"' + self.dict.get('throws') + '"'
        Date = str(self.dict.get('date'))
        yyyy = Date[0:4]
        mm = Date[4:6]
        dd = Date[6:8]
        text += ',"' + str(yyyy) + '-' + str(mm) + '-' + str(dd) + '"'
        text += ',"' + get_team(self.dict.get('batTeam')) + '"'
        text += ',"' + get_team(self.dict.get('pitTeam')) + '"'
        return text

    def printData( self ):
        text = '"' + self.dict.get('inn') + self.dict.get('topbot') + '"'
        text += ',"' + self.dict.get('homescore') + '"'
        text += ',"' + self.dict.get('awayscore') + '"'
        text += ',"' + self.dict.get('batName') + '"'
        text += ',"' + self.dict.get('pitName') + '"'
        text += ',"' + self.dict.get('ball') + '"'
        text += ',"' + self.dict.get('strike') + '"'
        text += ',"' + self.dict.get('out') + '"'
        text += ',"' + self.dict.get('onbase1') + '"'
        text += ',"' + self.dict.get('onbase2') + '"'
        text += ',"' + self.dict.get('onbase3') + '"'
        text += ',"' + self.dict.get('event') + '"'
        text += ',"' + self.dict.get('description') + '"'
        text += ',"' + self.dict.get('bs') + '"'
        text += ',"' + self.dict.get('bb_type') + '"'
        text += ',"' + self.dict.get('result') + '"'
        text += ',"' + self.dict.get('field_pos') + '"'
        text += ',"' + self.dict.get('field_name') + '"'
        text += ',"' + self.dict.get('stands') + '"'
        text += ',"' + self.dict.get('throws') + '"'
        Date = str(self.dict.get('date'))
        yyyy = Date[0:4]
        mm = Date[4:6]
        dd = Date[6:8]
        text += ',"' + str(yyyy) + '-' + str(mm) + '-' + str(dd) + '"'
        text += ',"' + self.dict.get('batTeam') + '"'
        text += ',"' + self.dict.get('pitTeam') + '"'
        text += ',"' + self.dict.get('seqno') + '"\n'
        return text

class gameData:
    # 경기의 모든 데이터를 총괄한다.
    # 1) 주자 상황
    # 2) 타석 상황
    # 3) 라인업 & 포지션 상황
    # 4) 경기 개요

    def __init__( self ):
        self.ErrMsg = ''
        self.onBase = _onBase()
        self.atBat = _atBat()
        self.lineup = _lineup()
        self.gameInfo = _gameInfo()
        self.curRunner = 0

        self.keepOldPos = ''
        self.keepOldName = ''
        self.keepNewPos = ''
        self.keepNewName = ''

        self.players = {}
        # ID: { name: xxx, stand: 012, throw: 012, inout: tf, homeaway: 01 }

        self.playerCode = {} # 선수 ID를 총괄하는 dictionary structure.
                        # ID:이름 순서로 입력
                        # ID는 unique한데 이름은 아니다.
        self.playerStands = {}   # 선수의 타격 손을 dictionary로 저장
                            # ID: 손 순서로 입력(손: right = 0, left = 1, switch = 2)
        self.playerThrows = {}   # 선수의 투구 손을 dictionary로 저장
                            # ID: 손 순서로 입력(손: right = 0, left = 1, switch = 2)
        self.playerInOut = {}    # 선수가 현재 경기에 나가 있는지, 아닌지 나타냄
                            # ID: {'homeaway': 0/1, 'inout': True/False} 순서로 입력
                            # True는 현재 경기에 뛰는 중
                            # False는 교체아웃됐거나 아직 나오지 않음

        self.pbp_list = []       # 이 리스트의 tail에는 항상 '다음 pitch 결과를 반영할' pbp data가 있는 것으로 가정한다.
                            # -> pitch가 들어오면 결과를 tail에 반영한다.
                            # -> PA result가 나오면 tail에 반영한다.
                            # -> 새 pitch 들어올 차례가 됐을 때는 항상 new tail을 만든다.
                            # '새로운 내용을 쓸 칸을 항상 유지한다'라고 생각하자.
                            # 이닝 종료가 될 때는 지금까지 쓴 칸(pbp data 하나)을 다 뜯고 새로 칸을 마련한다.
                            #   ex) 도루자로 이닝 종료 -> 마지막 칸에는 '도루자' 내용을 적는다.
                            #                          이닝 종료 텍스트가 뜰 때만 새 칸을 마련한다.
                            #   ex) 타석 도중 대타 -> 앞 칸들의 타자 ID를 바꿔준다.
                            #                       마지막 칸은 내버려두면 된다.
                            #                       타격이 종료되면 나오는 대타 텍스트에서 다시 타자 ID를 추출한다.
                            #                       타자 ID가 비어있는 칸들에만 새 ID를 넣어준다.
                            #                       내용을 기입한 칸은 뜯어서 출력하고 새 칸을 마련한다.

        self.gameInfo.setDate( '20160101' )
        # 아무거나 넣어 줬다.

    def addPlayer( self, Code, Name, Stands, Throws, Homeaway ):
        if self.players.get(int(Code)) == None:
            self.players[ int(Code) ] = { 'name': Name, 'stands': Stands, 'throws': Throws, 'homeaway': Homeaway, 'inout': True}
            return 1
        else:
            if self.players.get(int(Code))['name'] == Name:
                return 1
            else:
                print
                print "Unexpected Error Occured in gameData.addPlayer - player already exists: " + Name
                return -1

    def setInOut( self, Code, tf ):
        if self.players.get( int(Code) ) != None:
            self.players[ int(Code) ]['inout'] = tf
            return 1
        else:
            if self.players.get(int(Code))['name'] == Name:
                return 1
            else:
                print
                print "Unexpected Error Occured in gameData.setInOut - player doesn't exist: " + Code
                return -1

    def isThereSameName( self, Name ):
        num = 0
        for key in self.players.keys():
            if self.players.get( key )['name'] == Name:
                num += 1
        if num > 1:
            return True
        else:
            return False

    def findCodeByName( self, Name ):
        # 처음 나오는 key만 리턴.
        # isThereSameName이 False일 때만 실행한다.
        for key in self.players.keys():
            if self.players.get( key )['name'] == Name:
                return key

    def findMultiCodeByName( self, Name ):
        # 동명이인이 존재하는 경우, 모든 code를 찾아서 리스트로 리턴.
        # isThereSameName이 True인 경우 실행.
        # 이병규 쉬벌...
        CodeList = []
        for key in self.players.keys():
            if self.players.get( key )['name'] == Name:
                CodeList.append( key )
        return CodeList

    def findNameByCode( self, pCode ):
        # 선수 ID로 이름을 찾는다.
        if self.players.get( pCode ) != None:
            return self.players.get( pCode )['name']
        else:
            return ''

    def print_error_info( self ):
        # 에러 발생 시 경기 정보를 출력한다.
        text = "  DATE : " + str(self.gameInfo.getDate()) + "\n"
        text = text + "  HOME : " + self.gameInfo.getHome() + "\n"
        text = text + "  AWAY : " + self.gameInfo.getAway() + "\n"
        text = text + "  INN : " + str(self.gameInfo.getInn()) + "\n"
        text = text + "  TOPBOT : "
        if self.gameInfo.getInnTopbot() == 1:
            text = text + "BOT\n"
        else:
            text = text + "TOP\n"
        print text

    def print_lineup_msg( self, homeaway ):
        print
        print '======================'
        if homeaway == 1:
            print '홈'
            for i in range(1, 10):
                code = self.lineup.home[i]['code']
                print str(i) + ' ' + str(code) + ' '  + self.players.get(code)['name'] + ' ' + self.lineup.home[i]['pos']
        else:
            print '어웨이'
            for i in range(1, 10):
                code = self.lineup.away[i]['code']
                print str(i) + ' ' + str(code) + ' '  + self.players.get(code)['name'] + ' ' + self.lineup.away[i]['pos']
        print '======================'
        self.print_error_info()

    def try_print( self, result ):
        if result < 0:
            print
            print self.ErrMsg
            self.print_lineup_msg( self.gameInfo.getInnTopbot() )
            self.print_lineup_msg( 1-self.gameInfo.getInnTopbot() )
            exit(1)

    def setpbpOnbase( self, pbp ):
        runners = self.onBase.getBaseList()
        on_1b = runners[0]
        on_2b = runners[1]
        on_3b = runners[2]

        pbp.setData( 'onbase1', on_1b )
        pbp.setData( 'onbase2', on_2b )
        pbp.setData( 'onbase3', on_3b )

    def setpbpAtbat( self, pbp ):
        # 타자 이름은 타석 종료 / 타자 교대됐을 때 기입한다.
        homeaway = self.gameInfo.getInnTopbot()
        if homeaway == 1:
            homeaway = 0
        else:
            homeaway = 1
        codep = self.lineup.getPitCode( homeaway )
        pitName = self.findNameByCode( codep )
        balls = self.atBat.balls
        strikes = self.atBat.strikes
        outs = self.atBat.outs
        if self.atBat.stand == 0:
            stands = 'R'
        elif self.atBat.p_throws == 1:
            stands = 'L'
        else:
            stands = 'S'
        if self.atBat.p_throws == 0:
            throws = 'R'
        elif self.atBat.p_throws == 1:
            throws = 'L'
        else:
            throws = 'S'

        #pbp.setData( 'batName', batName )
        pbp.setData( 'pitName', pitName )
        pbp.setData( 'ball', balls )
        pbp.setData( 'strikes', strikes )
        pbp.setData( 'outs', outs )
        pbp.setData( 'stands', stands )
        pbp.setData( 'throws', throws )

    def setpbpGameInfo( self, pbp ):
        inn = self.gameInfo.getInn()
        topbot = ''
        batTeam = ''
        pitTeam = ''
        if self.gameInfo.getInnTopbot() == 1:
            topbot = '말'
            batTeam = self.gameInfo.getHome()
            pitTeam = self.gameInfo.getAway()
        else:
            topbot = '초'
            batTeam = self.gameInfo.getAway()
            pitTeam = self.gameInfo.getHome()

        homescore = self.gameInfo.getHomeScore()
        awayscore = self.gameInfo.getAwayScore()
        gamedate = self.gameInfo.getDate()

        pbp.setData( 'inn', str(inn) )
        pbp.setData( 'topbot', topbot )
        pbp.setData( 'homescore', homescore )
        pbp.setData( 'awayscore', awayscore )
        pbp.setData( 'date', gamedate )
        pbp.setData( 'batTeam', batTeam )
        pbp.setData( 'pitTeam', pitTeam )

    # 라인업, 선수 데이터가 모두 입력된 상태에서 실행.
    # 경기의 시작.
    # 첫 타자와 첫 투수를 atBat에 세팅한다.
    def startGame( self ):
        batID = self.lineup.getOrderCode( 0, 1 )
        pitID = self.lineup.getPitCode( 1 )
        if batID == -1:
            self.print_error_info()
            print 'startGame Failure - invalid leadoff hitter'
            exit(1)
        if pitID == -1:
            self.print_error_info()
            print 'startGame Failure - invalid starting pitcher'
            exit(1)
        #self.atBat.batterID = 0   # 무조건 처음 batterID는 0이다.
        #self.atBat.stand = 0       # 무조건 처음 batter Stand는 0이다.
        self.atBat.pitcherID = pitID
        self.atBat.p_throws = self.players.get( pitID )['throws']

        pbp = pbpdata()

        #self.setpbpOnbase( pbp )
        self.setpbpAtbat( pbp )
        self.setpbpGameInfo( pbp )

        self.pbp_list.append( pbp )

    def endGame( self ):
        # pseudo function(do nothing)
        self.pbp_list = []

    def setStands( self, pCode, pStands ):
        self.players[int(pCode)]['stands'] = pStands

    def getStandsByCode( self, pCode ):
        return self.players.get( int(pCode) )['stands']

    def setThrows( self, pCode, pStands ):
        self.players[int(pCode)]['throws'] = pStands

    def getThrowsByCode( self, pCode ):
        return self.players.get( int(pCode) )['throws']

    def printBBData( self, seqno ):
        text = ''
        homeaway = self.gameInfo.getInnTopbot()
        if homeaway == 1:
            homeaway = 0
        else:
            homeaway = 1
        for i in range( len(self.pbp_list) ):
            codep = self.lineup.getPitCode( homeaway )
            codec = self.lineup.getPosCode( homeaway, 'c' )
            if not codec:
                self.print_lineup_msg( homeaway )
                self.print_error_info()
                exit(1)
            code1b = self.lineup.getPosCode( homeaway, '1b' )
            code2b = self.lineup.getPosCode( homeaway, '2b' )
            code3b = self.lineup.getPosCode( homeaway, '3b' )
            codess = self.lineup.getPosCode( homeaway, 'ss' )
            codelf = self.lineup.getPosCode( homeaway, 'lf' )
            codecf = self.lineup.getPosCode( homeaway, 'cf' )
            coderf = self.lineup.getPosCode( homeaway, 'rf' )
            text += '"' + str(seqno) +'",'
            text += self.pbp_list[i].printBBData() + ',"'
            text += self.findNameByCode( codep ) + '","'
            text += self.findNameByCode( codec ) + '","'
            text += self.findNameByCode( code1b ) + '","'
            text += self.findNameByCode( code2b ) + '","'
            text += self.findNameByCode( code3b ) + '","'
            text += self.findNameByCode( codess ) + '","'
            text += self.findNameByCode( codelf ) + '","'
            text += self.findNameByCode( codecf ) + '","'
            text += self.findNameByCode( coderf ) + '"\n'
        return text

    def setAtBat( self, order, inName ):
        homeaway = self.gameInfo.getInnTopbot()
        pCode = self.lineup.getOrderCode( homeaway, order )
        self.atBat.batterID = pCode
        self.atBat.batOrder = int(order)
        pName = self.findNameByCode( pCode )
        for i in range( len(self.pbp_list) ):
            if self.pbp_list[i].getData( 'batName' ) == '':
                self.pbp_list[i].setData( 'batName', pName )

    # 타석을 리셋한다. BSO를 리셋.
    # 타석 결과 나올때 한다. -> 'n번 타자'는 도중 교체일 수도 있어서 타석의 끝이 아니다.
    # 타석의 결과는 안타/홈런/아웃/출루/낫아웃 이렇게 구성
    # order도 넘긴다.
    def nextAtBat( self ):
        self.atBat.pitches = 0
        self.atBat.batOrder += 1
        if self.atBat.batOrder > 9:
            self.atBat.batOrder = 1
        self.atBat.batterID = 0 # 타석 종료 혹은 교체 후에 batterID를 모두 채운다.
        # pitcherID 는 1구1구마다 체크 가능하므로 바꾸지 않는다.
        self.atBat.stand = -1
        #self.atBat.p_throws = 0
        self.atBat.balls = 0
        self.atBat.strikes = 0
        self.atBat.outs += 0    # 변경 없음; 아웃 처리되는 곳에서 처리

    def resetPBP( self ):
        self.pbp_list = []
        pbp = pbpdata()
        self.setpbpAtbat( pbp )
        self.setpbpGameInfo( pbp )
        #self.setpbpOnbase( pbp )
        #self.onBase.clear()

        self.pbp_list.append( pbp )

    def setInnMid( self ):
        self.gameInfo.inn_topbot = 1
        awayPit = self.lineup.getPitCode( 0 )
        awayPitThrow = self.getThrowsByCode( awayPit )
        self.atBat.changePit( awayPit, awayPitThrow )

    def setInnEnd( self ):
        self.gameInfo.inn_topbot = 0
        homePit = self.lineup.getPitCode( 1 )
        homePitThrow = self.getThrowsByCode( homePit )
        self.atBat.changePit( homePit, homePitThrow )
        self.gameInfo.inn += 1

    # text에 적히는 종류 별로 EVENT를 작성.

    #'n번타자' 텍스트 볼 때 처리하는 이벤트
    # -> 타석에 선 타자를 확정할 수 있게 된다.
    # -> 타자 관련 정보를 확정짓지 않았던 pbp data list들을 찾아 값을 갱신한다.
    # -> 타자 관련 정보 = batterID, stand
    #
    # 확정된 이후에는 pbp data를 출력할 수 있게 된다.
    # event, result는 'n번 타자' 이전에 나오는 관련 텍스트 parsing할 때 처리.
    # -> list에 적재된 pbp data를 모두 출력한다.
    # -> 다음 타석을 위해 pbp data를 새로 만들어서 추가한다.
    # -> 이 data는 현재 atBat의 내용을 반영해서 한다. 이미 BSO 계산된 상황.
    #
    # 1) list에 적재된 pbp data에서 batterID가 0인 것을 텍스트 기준으로 수정.
    # 2) 1)에서 수정한 pbp data의 stand를 텍스트 기준으로 수정.
    # 3) onbase를 정리한다. runner 중 ID가 -1인 것이 있으면 batterID로 수정.
    # 4) pbp data를 모두 출력.
    # 5) 새 pbp data를 만들어서 추가. 여기에 atBat 내용 반영(setpbpAtbat)


    # 타자 결과 텍스트 볼 때 처리하는 이벤트(XXX: ~~~~)
    # -> 타석의 결과(event, result)를 확정지을 수 있다.
    # -> 안타, 낫아웃 포함 출루(폭투/포일/다른주자 수비)인 경우 타자 주자의 onBase를 처리할 수 있다.
    #       * 타격 이벤트의 종류
    #       1) 출루하는 것
    #       -> 안타, 홈런 - hit, homerun
    #       -> 볼넷, 고의4구, 몸에 맞는(은) 공 - walk( 0/1/2, seqno )
    #       -> 실책, 야수선택, 타격방해, 땅볼로 출루 - onbase
    #       -> 희생번트 실책, 희생번트 야수선택, 희생플라이 실책 (희생타는 따로) - onbase
    #       -> 낫아웃(폭투, 포일, 다른주자 수비) - notout(0)
    #       -> 라인드라이브 실책(아웃과 구분) - onbase
    #
    #       2) 출루 없는 것
    #       -> 땅볼 아웃, 플라이 아웃, 라인드라이브 아웃, 병살타 아웃, 삼중살 - out( 'gb', 'fb', 'ld', 'gidp', 'tplay' )
    #       -> 희생번트 아웃, 희생플라이 아웃 - sacfly, sacbunt
    #       -> 삼진, 낫아웃 - strikeout(1), notout(1)
    #       -> 인필드플라이 아웃 - out( 'infield' )
    #       -> 쓰리번트 아웃 - strikeout(0)
    #
    # -> pitch result는 볼/스트/인플레이로 나뉘므로 여기서 처리하지 않는다.
    # -> bb_type을 여기서 정할 수 있다.
    # -> fielder(bblocation)를 확정지을 수 있다. 포지션, 이름
    # -> 타자주자의 아웃카운트 처리를 확실하게 할 수 있다.
    # -> seqno가 찍히는 pitch는 타격 결과만.
    # -> 주자 상황 결과를 제외하면, atBat 데이터를 모두 확정 리셋할 수 있다.
    #
    # 1) list에 적재된 pbp data의 event, result를 모두 확정지어준다.
    # 2) 타자의 onbase를 처리한다.
    # 3) 마지막 pbp data의 bb_type을 확정 짓는다.
    # 4) 마지막 pbp data에서 field_pos, field_name을 확정 짓는다.
    # 5) seqno를 찍는다.
    # 6) 아웃카운트를 처리한다.
    # 7) atBat을 리셋한다. (nextAtBat)


    # 주자 텍스트 볼 때 처리하는 이벤트(X루주자 ~~~)
    # -> 누상의 결과를 처리할 수 있다.
    # -> 순차적 처리하기 때문에 한 루에 2명 주자 있는 상황 발생 가능.
    #    ex) 만루에서 밀어내기 볼넷이 나와서
    #        타자 -> 1루 주자 -> 2루 주자 -> 3루 주자 순으로 처리할 때.
    #        1루, 2루, 3루에 계속 주자가 2명이 쌓이게 된다.
    # -> 다음 atBat 이전의 onBase 내용을 처리할 수 있다.
    # -> 결과에 따라서 아웃카운트, 스코어가 증감하게 된다.
    #
    # 1) 주자를 하나씩 옮긴다.
    # 2) 순차적으로 처리되기 때문에 한 개 루에 2명의 주자가 있는 상황이 발생할 수 있다.
    # 3) 아웃/득점 처리도 각각 해준다. 마지막 주자 처리하면 아웃카운트/점수 확정된다.
    # 4) 아웃/득점은 해당 타석에 모두 귀속되는 결과이기 때문에 순차적 처리해서 누적한다.
    '''
    # 일반적인 진루는 'n루주자 XXX : n루까지 진루' 이렇게 표시된다.
    # 이 경우는 차례대로, 현재 주자의 base를 cursor로 가리키면서
    # 다음 text가 들어왔을 때 cursor가 가리키는 base와 text의 출발 base를 비교하면
    # 동명이인이라도 같은 주자인지 아닌지 구분할 수 있다.
    # 비정상적인(?) 진루는 전부 실책/(무관심)도루(실패)/폭투/포일/보크/다른주자수비
    # 이런 상황에서발생하며, 이런 각종 설명이 붙는다(예외: FD2루까지 / FD3루까지. 예전 문중에 남은 bug성)
    # 이 경우는 '추가 진루'로 보며 앞 text에서 처리한 주자를 계속 진루시킨다.
    '''


    # 교체/변경 텍스트 볼 때 처리하는 이벤트(XXX : XXX로 교체/수비위치 변경)
    # -> lineup을 변경하게 된다.
    # -> onBase를 수정해야 할 때도 있다(주자의 경우)
    # -> atBat의 내용이 바뀌기도 한다(투수의 경우).
    # -> 하나씩 처리해준다.
    # -> 투수의 경우 바뀌는 즉시 tail의 pbp data에 반영해준다.
    #
    # 1) lineup을 수정해준다.
    # 2) 대주자인 경우, onBase를 같이 수정한다.
    # 3) 투수인 경우, atBat을 같이 수정한다.
    # 4) pbp data에 setpbpAtBat, setpbpOnbase, setpbpGameInfo 해준다.


    # 기타 투구 텍스트 볼 때 처리하는 이벤트( -n구 XXXX )
    # -> pitch count를 추가 가능.
    # -> pitch result를 확정 가능. (description)
    # -> 타석의 볼카운트를 추가 가능.
    # -> pbp data의 BS 분류를 추가 가능.
    # -> 타석 종료(타격/삼진/볼넷)가 아니면 다음 pitch data를 추가.
    # -> bb type은 타격 결과에서 확정 가능.
    #
    # 1) pitches ++
    # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
    # 3) description을 pbp data에 추가.
    # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
    # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X


    ###############################################
    ###############   PITCH EVENTS    ##############
    ###############################################
    # 투구에 따른 4가지 기본 이벤트: 볼, 스트라이크, 헛스윙, 타격
    # n구 XX 형식으로 오는 이벤트
    # 추가로 번트까지 고려한다.
    # -> pitch count를 추가 가능.
    # -> pitch result를 확정 가능. (description)
    # -> 타석의 볼카운트를 추가 가능.
    # -> pbp data의 BS 분류를 추가 가능.
    # -> 타석 종료(타격/삼진/볼넷)가 아니면 다음 pitch data를 추가.
    # -> bb type은 타격 결과에서 확정 가능.
    #
    # 1) pitches ++
    # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
    # 3) description을 pbp data에 추가.
    # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
    # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

    def ball( self, seqno ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        self.atBat.balls += 1
        #self.atBat.strikes += 0
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '볼' )
        pbp.setData( 'bs', 'B' )
        if self.atBat.balls < 4:
            next_pbp = pbpdata()
            self.setpbpAtbat( next_pbp )
            self.setpbpOnbase( next_pbp )
            self.setpbpGameInfo( next_pbp )
            pbp_list.append( next_pbp )

    def strike( self, seqno ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        #self.atBat.balls += 0
        self.atBat.strikes += 1
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '스트라이크' )
        pbp.setData( 'bs', 'S' )
        if self.atBat.strikes < 3:
            next_pbp = pbpdata()
            self.setpbpAtbat( next_pbp )
            self.setpbpOnbase( next_pbp )
            self.setpbpGameInfo( next_pbp )
            pbp_list.append( next_pbp )

    def foul( self, seqno ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        #self.atBat.balls += 0
        if self.atBat.strikes < 2:
            self.atBat.strikes += 1
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '파울' )
        pbp.setData( 'bs', 'S' )
        next_pbp = pbpdata()
        self.setpbpAtbat( next_pbp )
        self.setpbpOnbase( next_pbp )
        self.setpbpGameInfo( next_pbp )
        pbp_list.append( next_pbp )

    def swstr( self, seqno ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        #self.atBat.balls += 0
        self.atBat.strikes += 1
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '헛스윙' )
        pbp.setData( 'bs', 'S' )
        if self.atBat.strikes < 3:
            next_pbp = pbpdata()
            self.setpbpAtbat( next_pbp )
            self.setpbpOnbase( next_pbp )
            self.setpbpGameInfo( next_pbp )
            pbp_list.append( next_pbp )

    # 번트는 기본적으로 '타격'이다. 번트안타, 희생번트 모두 해당
    # 번트헛스윙/번트파울은 '번트'로 표기된다.
    # 번트파울 플라이 아웃은 '타격'으로 표기된다.
    def buntfoul( self ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        #self.atBat.balls += 0
        self.atBat.strikes += 1
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '번트파울' )
        pbp.setData( 'bs', 'S' )
        if self.atBat.strikes < 3:
            next_pbp = pbpdata()
            self.setpbpAtbat( next_pbp )
            self.setpbpOnbase( next_pbp )
            self.setpbpGameInfo( next_pbp )
            pbp_list.append( next_pbp )

    def contact( self, seqno ):
        # 1) pitches ++
        # 2) ball/strike를 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 3) description을 pbp data에 추가.
        # 4) bs를 pbp data에 추가. (필요한 경우 - 볼/스트라이크/헛스윙/파울)
        # 5) 카운트, pitch 결과에 따라서 다음 pitch data 추가 가능. atBat 세팅. 타석 종료(볼넷/삼진/타격)되면 추가 X

        self.atBat.pitches += 1
        #self.atBat.balls += 0
        #self.atBat.strikes += 0
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'description', '인플레이' )
        pbp.setData( 'bs', 'X' )

    # 여기서부터는 CONTACT 결과에 대한 내용

    ###############################################
    ##############   BATTER EVENTS   ##############
    ###############################################
    # 타자 이벤트: 안타, 아웃, 볼넷, 삼진, 진루, 홈인, 교체
    # 타격, 볼넷, 삼진, 낫아웃에 뒤따르는 이벤트
    # line 여러개로 표기되는 경우가 있다. 예를 들면 주자 있을 때 땅볼로 주자만 아웃
    # 이럴 때는 line 하나씩 처리한다.
    #
    # 1) list에 적재된 pbp data의 event, result를 모두 확정지어준다.
    # 2) 타자의 onbase를 처리한다.
    # 3) 마지막 pbp data의 bb_type을 확정 짓는다.
    # 4) 마지막 pbp data에서 field_pos, field_name을 확정 짓는다.
    # 5) seqno를 찍는다.
    # 6) 아웃카운트를 처리한다.
    # 7) atBat을 리셋한다. (nextAtBat)

    #       1) 출루하는 것
    #       -> 안타, 홈런 - hit, homerun
    #       -> 볼넷, 고의4구, 몸에 맞는(은) 공 - walk( 0/1/2, seqno )
    #       -> 실책, 야수선택, 타격방해, 땅볼로 출루 - onbase
    #       -> 희생번트 실책, 희생번트 야수선택, 희생플라이 실책 (희생타는 따로) - onbase
    #       -> 낫아웃(폭투, 포일, 다른주자 수비) - notout(0)
    #       -> 라인드라이브 실책(아웃과 구분) - onbase
    #
    #       2) 출루 없는 것
    #       -> 땅볼 아웃, 플라이 아웃, 라인드라이브 아웃, 병살타 아웃, 삼중살 - out( 'gb', 'fb', 'ld', 'gidp', 'tplay' )
    #       -> 희생번트 아웃, 희생플라이 아웃 - sacfly, sacbunt
    #       -> 삼진, 낫아웃 - strikeout(1), notout(1)
    #       -> 인필드플라이 아웃 - out( 'infield' )
    #       -> 쓰리번트 아웃 - strikeout(0)

# 출루; 땅볼, 실책, 야수선택, 타격방해, 희생번트(야수선택 or 실책), 희생플라이 실책

    def hit( self, base, bblocation, seqno ):
        # 1) list에 적재된 pbp data의 event, result를 모두 확정지어준다.
        # 2) 타자의 onbase를 처리한다.
        # 3) 마지막 pbp data의 bb_type을 확정 짓는다.
        # 4) 마지막 pbp data에서 field_pos, field_name을 확정 짓는다.
        # 5) seqno를 찍는다.
        # 6) 아웃카운트를 처리한다.
        # 7) atBat을 리셋한다. (nextAtBat)

        event = ''
        result = '안타'
        if base == 1:
            event = '안타'
            self.onBase.setRunner( 1, -1 )
            # onbase 처리
            # 현재 타자가 -1로 되어 있으니 -1로 한다. ㅅㅂ
        elif base == 2:
            event == '2루타'
            self.onBase.setRunner( 2, -1 )
        else:
            event == '3루타'
            self.onBase.setRunner( 2, -1 )
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )

        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '' )

        pos = pod_dict.get( bblocation )
        homeaway = self.gameInfo.getInnTopbot
        pCode = self.lineup.getPosCode( homeaway, pos )
        pbp.setData( 'field_pos', bblocation )
        pbp.setData( 'field_name', self.findNameByCode( pCode ) )
        pbp.setData( 'seqno', seqno )

        # 아웃카운트 처리
        #self.atBat.outs += 0
        self.nextAtBat()

    def homerun( self, bblocation, seqno ):
        event = '홈런'
        result = '홈런'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '' )

        pbp.setData( 'field_pos', bblocation )
        pbp.setData( 'field_name', '' )
        pbp.setData( 'seqno', seqno )

        # 아웃카운트 처리
        #self.atBat.outs += 0
        self.nextAtBat()

    def sacfly( self, bblocation, seqno ):
        event = '희생플라이'
        result = '아웃'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '뜬공' )

        pos = pod_dict.get( bblocation )
        homeaway = self.gameInfo.getInnTopbot
        pCode = self.lineup.getPosCode( homeaway, pos )
        pbp.setData( 'field_pos', bblocation )
        pbp.setData( 'field_name', self.findNameByCode( pCode ) )
        pbp.setData( 'seqno', seqno )

        # 아웃카운트 처리
        self.atBat.outs += 1
        self.nextAtBat()

    def sacbunt( self, bblocation, seqno ):
        event = '희생번트'
        result = '아웃'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '땅볼' )

        pos = pod_dict.get( bblocation )
        homeaway = self.gameInfo.getInnTopbot
        pCode = self.lineup.getPosCode( homeaway, pos )
        pbp.setData( 'field_pos', bblocation )
        pbp.setData( 'field_name', self.findNameByCode( pCode ) )
        pbp.setData( 'seqno', seqno )

        # 아웃카운트 처리
        self.atBat.outs += 1
        self.nextAtBat()

    def strikeout( self, nottb, seqno ):
        # nottb: 쓰리번트
        # nottb = 0 -> 쓰리번트 삼진, nottb = 1 -> 일반 삼진
        event = ''
        if nottb == 0:
            event = '쓰리번트'
        else:
            event = '삼진'
        result = '아웃'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )

        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '' )
        pbp.setData( 'field_pos', '' )
        pbp.setData( 'field_name', '' )
        pbp.setData( 'seqno', seqno )

        self.atBat.outs += 1
        self.nextAtBat()

    def walk( self, walktype, seqno ):
        # 0: 일반 볼넷, 1: 고의4구, 2: 몸에 맞는 공
        event = ''
        result = ''
        if walktype == 0:
            event = '볼넷'
            result = '볼넷'
        elif walktype == 1:
            event = '고의4구'
            result = '볼넷'
        else:
            event = '몸에 맞는 공'
            result = '사구'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )

        # 아직 타석의 타자 ID가 세팅되지 않은 상태이므로 -1로 초기 설정
        self.onBase.setRunner( 1, -1 )

        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '' )
        pbp.setData( 'field_pos', '' )
        pbp.setData( 'field_name', '' )
        pbp.setData( 'seqno', seqno )

        self.atBat.outs += 0
        self.nextAtBat()

    def notout( self, adv, seqno ):
        # 일반적으로 '낫아웃 아웃'으로 아웃 처리.
        # 예외적으로 '낫아웃 폭투/포일/다른주자 수비'가 있다. 출루 처리한다.
        # adv = 0이면 출루, adv = 1이면 아웃.
        # 출루, 아웃카운트 처리만 0/1에 따라서 다르게 해준다.
        event = '낫아웃'
        result = '아웃'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )
        ##### Base 세팅
        if adv == 0:
            # 낫아웃 출루
            # 아직 타석의 타자 ID가 세팅되지 않은 상태이므로 -1로 초기 설정
            self.onBase.setRunner( 1, -1 )
        #else:
        # 아무것도 안함

        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        pbp.setData( 'bb_type', '' )
        pbp.setData( 'field_pos', '' )
        pbp.setData( 'field_name', '' )
        pbp.setData( 'seqno', seqno )

        if adv == 1:
            # 낫아웃 아웃
            self.atBat.outs += 1
        self.nextAtBat()

    def out( self, reason, bblocation, seqno ):
        # reason:
        # 'gb', 'fb', 'ld', 'gidp', 'infield'
        event = ''
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        if reason == 'gb':
            event = '땅볼'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'fb':
            event = '뜬공'
            pbp.setData( 'bb_type', '뜬공' )
        elif reason == 'ld':
            event = '직선타'
            pbp.setData( 'bb_type', '직선타' )
        elif reason == 'gidp':
            event = '병살타'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'tplay':
            event = '삼중살'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'infield':
            event = '뜬공'
            pbp.setData( 'bb_type', '뜬공' )
        result = '아웃'
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )

        pos = pod_dict.get( bblocation )
        homeaway = self.gameInfo.getInnTopbot
        pCode = self.lineup.getPosCode( homeaway, pos )
        pbp.setData( 'field_pos', bblocation )
        pbp.setData( 'field_name', self.findNameByCode( pCode ) )
        pbp.setData( 'seqno', seqno )

        # 병살타는 중계가 2줄 나와서 아웃 2번 측정된다. 여기선 하나만 올린다. 삼중살도.
        self.atBat.outs += 1
        self.nextAtBat()

    def onbase( self, reason, bblocation, seqno ):
        # contact 이후에 이어진다.
        # 출루; 땅볼, 실책, 야수선택, 타격방해, 희생번트(야수선택 or 실책), 희생플라이 실책; 일반 플라이 실책
        #       gb, err, fc, intf, bunterr, fberr

        event = ''
        result = ''
        pbp = self.pbp_list[ self.atBat.pitches - 1 ] # 끄트머리 있는 것을 가져온다
        if reason == 'gb':
            event = '땅볼'
            result = '아웃'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'gberr':
            result = '실책'
            if bblocation == '좌익수':
                event = '뜬공'
                pbp.setData( 'bb_type', '뜬공' )
            elif bblocation == '중견수':
                event = '뜬공'
                pbp.setData( 'bb_type', '뜬공' )
            elif bblocation == '우익수':
                event = '뜬공'
                pbp.setData( 'bb_type', '뜬공' )
            else:
                event = '땅볼'
                pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'fc':
            event = '땅볼'
            result = '야수선택'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'intf':
            event = '타격방해'
            result = '실책'
            pbp.setData( 'bb_type', '' )
        elif reason == 'bunterr':
            event = '땅볼'
            result = '실책'
            pbp.setData( 'bb_type', '땅볼' )
        elif reason == 'fberr':
            event = '뜬공'
            result = '실책'
            pbp.setData( 'bb_type', '뜬공' )
        for i in range( len(self.pbp_list) ):
            self.pbp_list[i].setData( 'event', event )
            self.pbp_list[i].setData( 'result', result )

        # 아직 타석의 타자 ID가 세팅되지 않은 상태이므로 -1로 초기 설정
        self.onBase.setRunner( 1, -1 )

        if reason == 'intf':
            pbp.setData( 'field_pos', '' )
            pbp.setData( 'field_name', '' )
        else:
            pos = pod_dict.get( bblocation )
            homeaway = self.gameInfo.getInnTopbot
            pCode = self.lineup.getPosCode( homeaway, pos )
            pbp.setData( 'field_pos', bblocation )
            pbp.setData( 'field_name', self.findNameByCode( pCode ) )
        pbp.setData( 'seqno', seqno )

        #       gb, err, fc, intf, bunterr, fberr
        if reason == 'gb':
            self.atBat.outs += 1
        else:
            # 야선, 실책, 타격방해는 모두 아웃카운트 그대로
            self.atBat.outs += 0
        self.nextAtBat()

    ###############################################
    ###############   RUNNER EVENTS   ##############
    ###############################################
    # 주자 이벤트: 진루, 아웃, 홈인
    # 아웃: 포스아웃(주자), 태그아웃(주자)
    def advance( self, isnormal, runfrom, runto, pName, seqno ):
        # isnormal = 1: 보통 진루, 0: 추가 진루
        # 보통 진루면 '마지막으로 진루시킨 주자'를 저장하기 위해 self.curRunner에 pCode를 저장한다.
        # 추가 진루면 self.curRunner에서 pCode를 빼온다.
        # 혹시나 모르니 추가 진루일 때는 pCode로 이름 찾은 것과 입력 이름을 대조해본다.
        #
        # 1) 주자를 하나씩 옮긴다.
        # 2) 순차적으로 처리되기 때문에 한 개 루에 2명의 주자가 있는 상황이 발생할 수 있다.
        # 3) 아웃/득점 처리도 각각 해준다. 마지막 주자 처리하면 아웃카운트/점수 확정된다.
        # 4) 아웃/득점은 해당 타석에 모두 귀속되는 결과이기 때문에 순차적 처리해서 누적한다.

        if isnormal == 1:
            pCodes = self.findMultiCodeByName( pName )
            pCode = 0

            runners = self.onBase.getBaseList()[ runfrom - 1 ]
            for i in range( len(runners) ):
                for pCode in pCodes:
                    if pCode == runners[i]:
                        pCode = runners[i]
                        break
                if not pCode == 0:
                    break

            if pCode == 0:
                print
                print "ERROR: NO RUNNER FOUND ON BASE " + str(runfrom) + ": " + pName
                self.print_error_info()
                exit(1)
            self.curRunner = pCode
            self.onBase.advance( runfrom, runto, pCode )

        else:
            pCode = self.curRunner
            if pCode == 0:
                print
                print "ERROR: NO RUNNER FOUND ON BASE " + str(runfrom) + ": " + pName
                self.print_error_info()
                exit(1)
            if findNameByCode( pCode ) != pName:
                print
                print "ERROR: MORE ADV ERROR - curRunner: " + findNameByCode( pCode ) + ", pName: " + pName
                self.print_error_info()
                exit(1)
            self.onBase.advance( runfrom, runto, pCode )

    def homein( self, runfrom, pName, seqno ):
        # 점수를 등록하고 주자를 onBase structure에서 말소한다.
        # 1) 주자를 하나씩 옮긴다.
        # 2) 순차적으로 처리되기 때문에 한 개 루에 2명의 주자가 있는 상황이 발생할 수 있다.
        # 3) 아웃/득점 처리도 각각 해준다. 마지막 주자 처리하면 아웃카운트/점수 확정된다.
        # 4) 아웃/득점은 해당 타석에 모두 귀속되는 결과이기 때문에 순차적 처리해서 누적한다.
        # TODO 홈인 - 이전 주자, 추가 진루 구분이 안된다. '실책으로 홈인' 이 경우 참조
        pCodes = self.findMultiCodeByName( pName )
        pCode = 0

        runners = self.onBase.getBaseList()[ runfrom - 1 ]
        for i in range( len(runners) ):
            for pCode in pCodes:
                if pCode == runners[i]:
                    pCode = runners[i]
                    break
            if not pCode == 0:
                break

        if pCode == 0:
            print "ERROR: NO RUNNER FOUND ON BASE " + str(runfrom) + ": " + pName
            self.print_error_info()
            exit(1)
        self.onBase.homein( runfrom, pCode )

    # def tagout( self, runfrom, pName, seqno ):

    # def forceout( self, runfrom, pName, seqno ):

    # def touchout( self, runfrom, pName, seqno ):

    ###############################################
    ###############   ANOTHER EVENTS   ##############
    ###############################################
    # 타석 중간/이전 이벤트: 실책, 폭투, 포일, 견제사, 합의판정, 교체, 변경
    # 1구에 앞서 교체/변경은 정상적인 포지션 교체/변경. 투수 or 야수
    # 투구 도중에 교체되는 경우도 있음(-_-) 이것도 고려해줘야.
    # 투구 도중 교체시,
    #   - 볼카운트에서 볼 > 스트라이크 라면
    #       - 볼넷은 전임 투수의 책임
    #       - 안타/실책/야선/포스아웃/사구 출루는 구원투수의 책임
    #   - 볼카운트에서 볼 =< 스트라이크 라면
    #       - 모든 결과는 구원투수의 책임

    def change( self, pName, oldPos, newPos ):
        # 수비 위치 변경
        # ~회말 (bot) -> 어웨이 변경(top)
        # ~회초 (top) -> 홈 변경(bot)
        homeaway = 1 - self.gameInfo.getInnTopbot()

        pCodes = self.findMultiCodeByName( pName )
        pCode = -1
        order = -1
        # 수비위치 변경하는 포지션 order 찾기
        # condition:
        # 1) 출장중('inout' = true)
        # 2) 홈/어웨이 현재 설정과 일치('homeaway' = homeaway)
        # 3) 타순은 정해진 범위(order > 0)
        # 4) 타순으로 찾아낸 포지션은 텍스트 내용과 일치해야 함(findPosByOrder(pos) = oldPos)
        for i in range( len(pCodes) ):
            candidate = self.players[ pCodes[i] ]
            if ( candidate['inout'] == True ):
                if candidate['homeaway'] == homeaway:
                    order =  self.lineup.findOrderByCode( homeaway, pCodes[i] )
                    if order > 0:
                        if self.lineup.findPosByOrder( homeaway, order ) == oldPos:
                            pCode = pCodes[i]

        if pCode == -1:
            self.ErrMsg = 'ERROR: in change(); can\'t find player to change position\n'
            self.ErrMsg += "  Player Name : " + pName + "\n"
            self.ErrMsg += "  old Position : " + oldPos + "\n"
            self.ErrMsg += "  new Position : " + newPos + "\n"
            print
            print self.ErrMsg
            self.print_lineup_msg( homeaway )
            self.print_lineup_msg( 1-homeaway )
            return -1

        self.try_print( self.lineup.setPlayerInPos(homeaway, order, newPos, pCode) )
        return 1

    def subs( self, oldPos, oldName, newPos, newName ):
        homeaway = self.gameInfo.getInnTopbot()
        if newPos.find( 'ph' ) >= 0:
            homeaway = homeaway
        elif newPos.find( 'pr' ) >= 0:
            homeaway = homeaway
        else:
            homeaway = 1 - homeaway # reverse

        keep = False
        if self.keepNewPos != '':
            keep = True

        self.try_print( self.substitute( homeaway, oldPos, oldName, newPos, newName ) )
        if self.keepNewPos != '':
            if keep == False:
                return 1
            else:
                if newPos.find('ph') >= 0:
                    # 대타로 교체하는 경우에는 keep했던 교체를 여기서 수행
                    if self.keepOldName == newName:
                        self.try_print( self.substitute( homeaway, self.keepOldPos, self.keepOldName, self.keepNewPos, self.keepNewName ) )
        self.setpbpAtbat( self.pbp_list[ len(self.pbp_list) - 1 ] )
        return 1

    def substitute( self, homeaway, oldPos, oldName, newPos, newName ):
        oldCodes = self.findMultiCodeByName( oldName )
        newCodes = self.findMultiCodeByName( newName )

        self.ErrMsg = ''
        if oldCodes == None:
            self.ErrMsg = "ERROR : player to substitute(OUT) DO NOT EXIST IN RAW DATA;\n"
            self.ErrMsg += "  OUT : " + oldName + "\n"
            if newCodes == None:
                self.ErrMsg += "ERROR : player to substitute(IN) DO NOT EXIST IN RAW DATA;\n"
                self.ErrMsg += "  IN : " + newPos + "/" + newName +"\n"
            else:
                self.ErrMsg += "  IN : " + newPos + "/" + newName + "/" + str(newCode) + "\n"
            return -1
        elif newCodes == None:
            self.ErrMsg = "ERROR : player to substitute(IN) DO NOT EXIST IN RAW DATA;" + "\n"
            self.ErrMsg += "  OUT : " + oldName + "/" + str(oldCode) + "\n"
            self.ErrMsg += "  IN : " + newPos + "/" + newName + "\n"
            return -1

        # find newCode
        # condition
        # 1) 'inout' = False -> 투수인 경우 True도 가능(지명타자 삭제)
        # 2) 'homeaway' = homeaway
        newCode = -1
        for i in range(len(newCodes)):
            candidate = self.players[ newCodes[i] ]
            if newPos == 'p':
                if newCodes[i] == self.lineup.getPitCode(homeaway):
                    if candidate['homeaway'] == homeaway:
                        if candidate['inout'] == True:
                            newCode = newCodes[i]
            if candidate['inout'] == False:
                if candidate['homeaway'] == homeaway:
                    newCode = newCodes[i]
                    break;

        if newCode == -1:
            self.ErrMsg = "ERROR : player to substitute(IN) DO NOT EXIST IN RAW DATA;\n"
            self.ErrMsg += "  Couldn\'t find player in name list\n"
            self.ErrMsg += "  OUT : " + oldName + "\n"
            self.ErrMsg += "  IN : " + newPos + " / " + newName +"\n"
            print
            print 'homeaway = ' + str(homeaway)
            for i in range(len(newCodes)):
                candidate = self.players[ newCodes[i] ]
                print candidate['name'] + ' / ' + str(newCodes[i]) + ' / ',
                print str(candidate['homeaway']) + ' / ' + str(candidate['inout'])
            return -1

        if oldPos != 'p':
            # 교체하는 포지션 order 찾기
            # condition:
            # 1) 출장중('inout' = true)
            # 2) 홈/어웨이 현재 공격과 일치('homeaway' = homeaway)
            # 3) 타순은 정해진 범위(order > 0)
            # 4) 타순으로 찾아낸 포지션은 텍스트 내용과 일치해야 함(findPosByOrder(pos) = oldPos)
            oldCode = -1
            order = -1
            targetPos = ''
            cankeep = False
            for i in range(len(oldCodes)):
                candidate = self.players[ oldCodes[i] ]
                if candidate['homeaway'] == homeaway:
                    cankeep = True
                    if candidate['inout'] == True:
                        order = self.lineup.findOrderByCode( homeaway, oldCodes[i] )
                        if order > 0:
                            targetPos = self.lineup.findPosByOrder( homeaway, order )
                            if targetPos == oldPos:
                                oldCode = oldCodes[i]
                                break
                            else:
                                if oldPos.find('주자') >= 0:
                                    oldCode = oldCodes[i]
                                    break
                                elif oldPos.isdigit():
                                    oldCode = oldCodes[i]
                                    break

            if oldCode == -1:
                # order만 없는 경우 - keep해놓고 나중에 한다.
                if cankeep == True:
                    self.keepOldPos = oldPos
                    self.keepOldName = oldName
                    self.keepNewPos = newPos
                    self.keepNewName = newName
                    return 1
                else:
                    self.ErrMsg = "ERROR : player to substitute(OUT) DO NOT EXIST IN RAW DATA;" + "\n"
                    self.ErrMsg += "CHECK POSITION, IN/OUT, ORDER, HOME/AWAY CONDITION\n"
                    self.ErrMsg += "  OUT : " + oldName + "/" + str(oldCode) + "\n"
                    self.ErrMsg += "  IN : " + newPos + "/" + newName + "\n"
                    return -1

                    return -1

            self.lineup.setPlayerInPos( homeaway, order, newPos, newCode )
            self.setInOut( oldCode, False )
            self.setInOut( newCode, True )
            if newPos == 'p':
                self.lineup.setPitcher( homeaway, newCode )
            elif newPos == 'pr':
                # 대주자 교체 - onBase 설정은 나중에
                self.onBase.clear() # 임시 코드
        else:
            # 투수교대하는 경우 - 투수가 타순에 속해있는지 확인해야함
            if self.lineup.doPitcherExistInLineup( homeaway ):
                oldCode = -1
                order = -1
                targetPos = ''
                cankeep = False
                for i in range(len(oldCodes)):
                    candidate = self.players[ oldCodes[i] ]
                    if candidate['homeaway'] == homeaway:
                        cankeep = True
                        if candidate['inout'] == True:
                            order = self.lineup.findOrderByCode( homeaway, oldCodes[i] )
                            if order > 0:
                                targetPos = self.lineup.findPosByOrder( homeaway, order )
                                if targetPos == oldPos:
                                    oldCode = oldCodes[i]
                                    break
                if oldCode == -1:
                    self.ErrMsg = "ERROR : player to substitute(OUT) DO NOT EXIST IN RAW DATA;" + "\n"
                    self.ErrMsg += "CHECK POSITION, IN/OUT, ORDER, HOME/AWAY CONDITION\n"
                    self.ErrMsg += "  OUT : " + oldName + "/" + str(oldCode) + "\n"
                    self.ErrMsg += "  IN : " + newPos + "/" + newName + "\n"
                self.lineup.setPlayerInPos( homeaway, order, newPos, newCode )
                self.lineup.setPitcher( homeaway, newCode )
                #TODO 일단 throw 전부 0(right)로 기록함.
                self.atBat.changePit( newCode, 0 )
                self.setInOut( oldCode, False )
                self.setInOut( newCode, True )
            else:
                oldCode = self.lineup.getPitCode( homeaway )
                self.lineup.setPitcher( homeaway, newCode )
                self.setInOut( oldCode, False )
                self.setInOut( newCode, True )
        return 1
