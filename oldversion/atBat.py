#-*- coding: utf-8 -*-
#atBat.py

class _atBat:
    def __init__( self ):
        self.batOrder = 1           # batting order
        self.pitches = 0

        # Player info
        self.batterID = 0           # pCode; player ID
        self.pitcherID = 0          # pCode; player ID
        self.stand = 0              # batter handness; right = 0, left = 1, switch = 2
        self.p_throws = 0           # pitcher handness; right = 0, left = 1, switch = 2

        # Pitch, ball count DATA
        self.balls = 0              # ball count before pitch
        self.strikes = 0            # strike count before pitch
        self.outs = 0               # outs before pitch

    def changeBat( self, pCode, Stand ):
        self.batterID = int(pCode)
        self.stand = Stand

    def changePit( self, pCode, Throws ):
        self.pitcherID = int(pCode)
        self.p_throws = Throws
