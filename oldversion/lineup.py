#-*- coding: utf-8 -*-
#lineup.py

class _lineup:
    pos_index = [ 'p', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'dh', 'pr', 'ph' ]
    def __init__( self ):
        self.home = {   # order: {'pos': 포지션(영문), 'code': ID(숫자)}, ...
                        1 : { 'pos': 'c', 'code': -1 },
                        2 : { 'pos': '1b', 'code': -1 },
                        3 : { 'pos': '2b', 'code': -1 },
                        4 : { 'pos': '3b', 'code': -1 },
                        5 : { 'pos': 'ss', 'code': -1 },
                        6 : { 'pos': 'lf', 'code': -1 },
                        7 : { 'pos': 'cf', 'code': -1 },
                        8 : { 'pos': 'rf', 'code': -1 },
                        9 : { 'pos': 'dh', 'code': -1 }
                    }
        self.away = {   # order: {'pos': 포지션(영문), 'code': ID(숫자)}, ...
                        1 : { 'pos': 'c', 'code': -1 },
                        2 : { 'pos': '1b', 'code': -1 },
                        3 : { 'pos': '2b', 'code': -1 },
                        4 : { 'pos': '3b', 'code': -1 },
                        5 : { 'pos': 'ss', 'code': -1 },
                        6 : { 'pos': 'lf', 'code': -1 },
                        7 : { 'pos': 'cf', 'code': -1 },
                        8 : { 'pos': 'rf', 'code': -1 },
                        9 : { 'pos': 'dh', 'code': -1 }
                    }
        self.homepit = -1    # 등판 중인 투수(홈)
        self.awaypit = -1    # 등판 중인 투수(어웨이)
        self.home_curorder = 1  # 현재 타석
        self.away_curorder = 1  # 현재 타석

        # 포지션 별로 유무(1)를 확인한다.
        self.home_pos = {   # '포지션(영문)': count
                            'p': 0,
                            'c': 1,
                            '1b': 1,
                            '2b': 1,
                            '3b': 1,
                            'ss': 1,
                            'lf': 1,
                            'cf': 1,
                            'rf': 1,
                            'dh': 1,
                            'pr': 0,
                            'ph': 0
                        }

        self.away_pos = {   # '포지션(영문)': count
                            'p': 0,
                            'c': 1,
                            '1b': 1,
                            '2b': 1,
                            '3b': 1,
                            'ss': 1,
                            'lf': 1,
                            'cf': 1,
                            'rf': 1,
                            'dh': 1,
                            'pr': 0,
                            'ph': 0
                        }

    def setPlayerInPos( self, homeaway, order, newpos, pCode ):
        if order < 1 :
            print "Unexpected Error Occured in lineup.setPlayerInPos - order < 1: " + pCode
            return -1
        elif order > 9:
            print "Unexpected Error Occured in lineup.setPlayerInPos - order > 9: " + pCode
            return -1
        else:
            if homeaway == 1:
                oldpos = self.home[order]['pos']
                self.home[order]['pos'] = newpos
                self.home[order]['code'] = int(pCode)
                self.home_pos[newpos] += 1
                self.home_pos[oldpos] -= 1
            elif homeaway == 0:
                oldpos = self.away[order]['pos']
                self.away[order]['pos'] = newpos
                self.away[order]['code'] = int(pCode)
                self.away_pos[newpos] += 1
                self.away_pos[oldpos] -= 1
            else:
                print "Unexpected Error Occured in lineup.setPlayerInPos - homeaway not 0 or 1: " + homeaway
                return -1
            return 1

    def setPitcher( self, homeaway, pCode ):
        if homeaway == 1:
            self.homepit = int(pCode)
        elif homeaway == 0:
            self.awaypit = int(pCode)
        else:
            print "Unexpected Error Occured in lineup.setPitcher - homeaway not 0 or 1: " + homeaway
            return -1
        return 1

    def setPosOfOrder( self, homeaway, order, newpos ):
        # away(top) = 0, home(bot) = 1
        # order 순번의 타자의 포지션을 newpos로 변경
        if homeaway == 1:
            oldpos = self.home[order]['pos']
            self.home[order]['pos'] = newpos
            self.home_pos[newpos] += 1
            self.home_pos[oldpos] -= 1
        elif homeaway == 0:
            oldpos = self.away[order]['pos']
            self.away[order]['pos'] = newpos
            self.away_pos[newpos] += 1
            self.away_pos[oldpos] -= 1
        else:
            print "Unexpected Error Occured in lineup.setPosOfOrder - homeaway not 0 or 1: " + homeaway
            return -1
        return 1

    # 타석 단위로 변경될 때마다 체크해준다.
    def checkPos( self, homeaway ):
        # 포지션 개수를 체크한다.
        # 같은 포지션이 1개를 넘거나
        # 투수, 지명타자가 같이 있을 때는 False를 return한다.
        # 포지션 개수의 합이 9를 넘어도 False를 return한다.
        if homeaway == 1:
            if self.home_pos['p'] >= 1:
                if self.home_pos['dh'] >=1:
                    return False

            posSum = 0
            for i in range(len(self.pos_index)):
                posCount = self.home_pos[self.pos_index[i]]

                if posCount > 1 :
                    if self.pos_index[i] == 'ph':
                        posSum += posCount
                    elif self.pos_index[i] == 'pr':
                        posSum += posCount
                    else:
                        return False
                else:
                    posSum += posCount

            if posSum == 9:
                return True
            else:
                return False
        else:
            if self.away_pos['p'] >= 1 and self.away_pos['dh'] >=1:
                return False

            posSum = 0
            for i in range(len(self.pos_index)):
                posCount = self.home_pos[self.pos_index[i]]

                if posCount > 1 :
                    if self.pos_index[i] == 'ph':
                        posSum += posCount
                    elif self.pos_index[i] == 'pr':
                        posSum += posCount
                    else:
                        return False
                else:
                    posSum += posCount

            if posSum == 9:
                return True
            else:
                return False

    # 현재 해당 포지션을 차지하고 있는 선수의 code를 리턴.
    def getPosCode( self, homeaway, Pos ):
        if homeaway == 1:
            for i in range(1, 10):
                if self.home[i]['pos'] == Pos:
                    return self.home[i]['code']
            return 0
        else:
            for i in range(1, 10):
                if self.away[i]['pos'] == Pos:
                    return self.away[i]['code']
            return 0

    # 현재 등판해 있는 투수의 code를 리턴.
    def getPitCode( self, homeaway ):
        if homeaway == 1:
            return self.homepit
        else:
            return self.awaypit

    # 현재 해당 타순에 서는 선수의 code를 리턴.
    def getOrderCode( self, homeaway, Order ):
        if int(Order) > 9 :
            return -1
        elif int(Order) < 1:
            return -1
        if homeaway == 1:
            return self.home[int(Order)]['code']
        else:
            return self.away[int(Order)]['code']

    def findOrderByCode( self, homeaway, pCode ):
        if homeaway == 1:
            for i in range(1, 10):
                if self.home[i]['code'] == int(pCode):
                    return i
            return -1   # don't exist
        else:
            for i in range(1, 10):
                if self.away[i]['code'] == int(pCode):
                    return i
            return -1   # don't exist

    def findPosByOrder( self, homeaway, order ):
        if int(order) > 9 :
            return -1
        elif int(order) < 1:
            return -1
        if homeaway == 1:
            return self.home[order]['pos']
        else:
            return self.away[order]['pos']

    def doPitcherExistInLineup( self, homeaway ):
        if homeaway == 1:
            if self.home_pos['p'] > 0:
                return True
            else:
                return False
        else:
            if self.away_pos['p'] > 0:
                return True
            else:
                return False
