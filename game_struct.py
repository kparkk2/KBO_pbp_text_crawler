# game_struct.py

# 현재 라인업
# 전체 출전 라인업
# 투수
# 타자

from errorManager import print_error
import inspect

class Player:
    def __init__(self, name=None, seq_no=0, position=0):
        self.Name = name
        self.Seq_no = seq_no
        self.in_out = False
        self.Position = position  # 1~9

    def get_name(self):
        return self.Name

    def get_no(self):
        return self.Seq_no

    def get_position(self):
        return self.Position

    def in_player(self):
        self.in_out = True

    def out_player(self):
        self.in_out = False

    def is_pitcher(self):
        return self.Position == 1


class Lineup:
    def __init__(self, homeaway=True, current_lineup=None, players=None):
        if players is None:
            players = []
        if current_lineup is None:
            current_lineup = []
        self.HomeAway = homeaway
        self.CurrentLineup = current_lineup
        self.Players = players

    def get_player(self, num):
        try:
            return self.Players[num]
        except IndexError as ie:
            filename, linenum, funcname = inspect.getframeinfo(inspect.currentframe())[:3]
            error_msg = "index : {0} / bound is {1}".format(num, len(self.Players))
            print_error(filename, linenum, funcname, error_msg)
