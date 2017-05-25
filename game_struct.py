# game_struct.py

# 현재 라인업
# 전체 출전 라인업
# 투수
# 타자

import errorManager as em


# wrapper
class GameStruct:
    def __init__(self, year, month, gameID):
        self.home_lineup = Lineup(homeaway=True, current_lineup=[], players=[])
        self.away_lineup = Lineup(homeaway=True, current_lineup=[], players=[])
        self.logger = logging.getLogger('gameLog')

        assert isinstance(year, int)
        assert isinstance(month, int)

        # set log config
        if month < 10:
            mon = '0{}'.format(str(month))
        else:
            mon = str(month)
        log_path = '{}/{}'.format(year, mon)
        log_file_name = gameID
        logManager.setLogFilePath(self.logger, log_path, log_file_name)


class Player:
    def __init__(self, name=None, seq_no=0, position=0):
        self.name = name
        self.seqNo = seq_no
        self.inOut = False
        self.position = position  # 1~9

    def get_name(self):
        return self.name

    def get_no(self):
        return self.seqNo

    def get_position(self):
        return self.position

    def in_player(self):
        self.inOut = True

    def out_player(self):
        self.inOut = False

    def is_pitcher(self):
        return self.position == 1


class Lineup:
    def __init__(self, homeaway=True, current_lineup=None, players=None):
        if players is None:
            players = []
        if current_lineup is None:
            current_lineup = []
        self.homeAway = homeaway
        self.currentLineup = current_lineup
        self.players = players

    def get_player(self, num):
        try:
            p = self.players[num]
        except IndexError:
            em.error_msg = 'index out of bound, idx {} / bound {}'.format(num, len(self.players))
            print(em.getTracebackStr())
            exit(1)
        else:
            return p

    def get_current_lineup(self):
        return self.currentLineup

    def get_players(self):
        return self.players

    def swap_player(self, name1, name2):
        self.currentLineup


class PlayerPool:
    def __init__(self, players=None):
        if players is None:
            self.Players = []
        else:
            self.Players = players

    def addPlayer(self, player):
        try:
            self.Players.append(player)
