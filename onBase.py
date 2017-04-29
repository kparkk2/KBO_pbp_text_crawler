#-*- coding: utf-8 -*-
#onBase.py

class _onBase:
    # 베이스 상황만 기록
    def __init__( self ):
        self.on_1b = []                 # pCode; player ID list
        self.on_2b = []                 # pCode; player ID list
        self.on_3b = []                 # pCode; player ID list

    def advance( self, src, dest, code ):
        if src == 1:
            for i in range( len(self.on_1b) ):
                if self.on_1b[i] == int(code):
                    self.on_1b[i:i+1] = []
                    break
            if dest == 2:
                self.on_2b.append( int(code) )
            else:
                self.on_3b.append( int(code) )
        else:
            for i in range( len(self.on_2b) ):
                if self.on_2b[i] == int(code):
                    self.on_2b[i:i+1] = []
                    break
            self.on_3b.append( int(code) )

    def homein( self, src, code ):
        if src == 1:
            for i in range( len(self.on_1b) ):
                if self.on_1b[i] == int(code):
                    self.on_1b[i:i+1] = []
                    break
        elif src == 2:
            for i in range( len(self.on_2b) ):
                if self.on_2b[i] == int(code):
                    self.on_2b[i:i+1] = []
                    break
        else:
            for i in range( len(self.on_3b) ):
                if self.on_3b[i] == int(code):
                    self.on_3b[i:i+1] = []
                    break

    def setRunner( self, base, pCode ):
        # 대주자 교체 시에 사용
        # 특정 베이스의 주자를 바꾼다
        if base == 1:
            self.on_1b.append( int(pCode) )
        elif base == 2:
            self.on_2b.append( int(pCode) )
        elif base == 3:
            self.on_3b.append( int(pCode) )
        else:
            print "ERROR : On setRunner Function - INVALID BASE NUMBER( > 3)"
            print "  BASE1 : " + self.on_1b
            print "  BASE2 : " + self.on_2b
            print "  BASE3 : " + self.on_3b
            exit(1)

    def clear( self ):
        self.on_1b = []
        self.on_2b = []
        self.on_3b = []

    def getBaseList( self ):
        # 주자 진루가 모두 처리된 상황에서만 쓴다.
        # 베이스 하나에 한 명의 주자만 있을 수 있다.
        if len(self.on_1b) > 1:
            print "ERROR : On getBaseList Function - too many runners on one base 1( > 1)"
            print "  BASE1 : " + self.on_1b
            print "  BASE2 : " + self.on_2b
            print "  BASE3 : " + self.on_3b
            exit(1)
        elif len(self.on_2b) > 1:
            print "ERROR : On getBaseList Function - too many runners on one base 2( > 1)"
            print "  BASE1 : " + self.on_1b
            print "  BASE2 : " + self.on_2b
            print "  BASE3 : " + self.on_3b
            exit(1)
        elif len(self.on_3b) > 1:
            print "ERROR : On getBaseList Function - too many runners on one base 3( > 1)"
            print "  BASE1 : " + self.on_1b
            print "  BASE2 : " + self.on_2b
            print "  BASE3 : " + self.on_3b
            exit(1)
        else:
            run1b = self.on_1b[0]
            run2b = self.on_2b[0]
            run3b = self.on_3b[0]
            return [run1b, run2b, run3b]
