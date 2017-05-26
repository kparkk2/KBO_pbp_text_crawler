#-*- coding: utf-8 -*-
#gameInfo.py

class _gameInfo:
    def __init__( self ):
        # GAME INFO
        self.date = '20161231'
        self.home = 'KT'
        self.away = 'HH'
        self.stadium = '잠실'        # stadium name
        self.inn = 1
        self.inn_topbot = 0         # 1 = home(bot), 0 = away(top)

        self.home_score = 0         # home score
        self.away_score = 0         # away score

    def setStadium( self, Stadium ):
        self.stadium = Stadium

    def setHome( self, Home ):
        self.home = Home

    def setAway( self, Away ):
        self.away = Away

    def setDate( self, Date ):
        self.date = Date

    def addHomeScore( self, n ):
        self.home_score += n

    def addAwayScore( self, n ):
        self.away_score += n

    def getStadium( self ):
        return self.stadium

    def getHome( self ):
        return self.home

    def getAway( self ):
        return self.away

    def getDate( self ):
        return self.date

    def getInn( self ):
        return self.inn

    def getInnTopbot( self ):
        return self.inn_topbot

    def getHomeScore( self ):
        return self.home_score

    def getAwayScore( self ):
        return self.away_score
