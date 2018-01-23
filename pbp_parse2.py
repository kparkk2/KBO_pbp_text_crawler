# pbp_parse2.py

import os
import json
from collections import OrderedDict
import regex

# OOO : XXX
# exception : '타석이탈위반'(이름), 'BH'
# caution : mind searching priority!
# 다음 text 받기 전, 타자주자 설정 함

pa_results = ['1루타',
              '2루타',
              '3루타',
              '홈런',
              '볼넷',
              '삼진',
              '몸에 맞는 볼',
              '내야안타',
              # 번트안타
              '안타',
              '고의4구',
              # 낫아웃 -> 폭투 or 포일 or K
              '낫아웃 폭투',
              '낫아웃 포일',
              '낫아웃',
              '낫 아웃',
              '타구맞음',
              # 플라이 -> 아웃, 인필드, 희플, 파플, 실책(뒤에서 다룸)
              ' 플라이 아웃',
              '인필드플라이',
              '희생플라이 아웃',
              '희생플라이아웃',
              '파울플라이 아웃',
              # 땅볼 -> 아웃 or 출루
              '땅볼 아웃',
              '땅볼로 출루',
              # 라인드라이브 -> 아웃 or 실책(뒤에서 다룸)
              '라인드라이브 아웃',
              # 병살타 + 번트병살타
              '병살타',
              '희생번트 아웃',
              '쓰리번트',
              ' 번트 아웃',
              # 희생번트 기록됨
              '희생번트 실책',
              # 희생번트 기록됨
              '희생번트 야수선택',
              '야수선택',
              # (희생포함)플라이 실책, 번트 실책, 라인드라이브 실책, 병살실책, 실책
              '실책',
              # 포수 실책으로 기록
              '타격방해',
              # 기타
              '부정타격',
              '삼중살']

# [0-9]+구 OO
ball_results = ['스트라이크',
                '볼',
                '타격',
                '번트파울',
                '번트헛스윙',
                '파울',
                '헛스윙',
                '파울실책',
                # 12초 룰 경고 입력 - 볼
                'C',
                '12초',
                # pass
                '판독']

runner_results = [
    # 사유 기록 : 케바케로 추가기록(도루실패, 보크, 폭투, 실책)
    # Next play : 아웃, 진루, 홈인
    # 도루실패아웃, 도루실패 기록하며~, 이중도루/삼중도루도 있음
    '도루실패',
    '도루 실패',
    # 보크로 진루/홈인
    '보크',
    # 폭투로 진루/홈인, 폭투사이 진루실패아웃
    '폭투',
    # 포일로 진루/홈인, 포일사이 진루실패아웃
    '포일',
    # 주루방해, 실책으로~(단순 실책) 진루/홈인
    '실책',
    # 도루로 진루/홈인, 이중도루/삼중도루도 있음
    '도루',
    # 견제사 아웃
    '견제사',
    # 기타 사유 - 기록 x
    '재치로',
    '다른주자',
    '타구맞음',
    '공과',
    # 기타
    '진루',
    '홈인',
    '태그아웃',
    '포스아웃',
    # 나머지
    '아웃'
]

other_text = ['포수송구방해로 아웃',
              '수비방해로 인하여',
              '낫아웃 다른주자 수비',
              '합의판정',
              '합의 판정',
              ' 최초 ',
              '어필아웃',
              '스포츠맨쉽',
              '퇴장',
              '추월',
              '경고',
              '판독',
              '비디오',
              '부상으로 중단',
              '주루방해로 득점',
              '말벌',
              'LG 2루주자',
              '4심합의',
              '넘어지면서']

results = ['내야안타',
           '1루타',
           '2루타',
           '3루타',
           '홈런',
           '번트안타',
           '땅볼 아웃',
           '플라이 아웃',
           '병살타 아웃',
           '번트병살타 아웃',
           '라인드라이브 아웃',
           '희생번트 아웃',
           '쓰리번트 아웃',
           ' 번트 아웃',
           '삼중살 아웃',
           '부정타격 아웃',
           '삼진 아웃',
           '스트라이크 낫 아웃',
           '타구맞음 아웃',
           '땅볼로 출루',
           '야수선택으로 출루',
           '실책으로 출루',
           '타격방해로 출루']

position = {
    '지명타자': 0,
    '투수': 1,
    '포수': 2,
    '1루수': 3,
    '2루수': 4,
    '3루수': 5,
    '유격수': 6,
    '좌익수': 7,
    '중견수': 8,
    '우익수': 9,
    '대타': 10,
    '대주자': 11
}

field_home = {
    0: 'home_dh',
    1: 'home_p',
    2: 'home_c',
    3: 'home_1b',
    4: 'home_2b',
    5: 'home_3b',
    6: 'home_ss',
    7: 'home_lf',
    8: 'home_cf',
    9: 'home_rf'
}

field_away = {
    0: 'away_dh',
    1: 'away_p',
    2: 'away_c',
    3: 'away_1b',
    4: 'away_2b',
    5: 'away_3b',
    6: 'away_ss',
    7: 'away_lf',
    8: 'away_cf',
    9: 'away_rf'
}


class BallGame:
    # game status dict
    game_status = {
        'game_date': '00000000',

        # batter & pitcher
        'pitcher': None,
        'batter': None,

        # bats/throws; 0 for Left, 1 for Right
        'stand': 0,
        'throws': 0,

        # ball count & inning & score
        'inning': 1,
        # 0 for top, 1 for bot
        'inning_topbot': 0,
        'balls': 0,
        'strikes': 0,
        'outs': 0,
        'score_home': 0,
        'score_away': 0,

        # pitch & pa result
        # ?결과 나왔을 때만 기록?
        'pa_result': None,
        'pitch_result': None,

        # base
        'runner_1b': None,
        'runner_2b': None,
        'runner_3b': None,

        # pfx data
        'pitch_type': None,
        'speed': None,
        'px': None,
        'pz': None,
        'pfx_x': None,
        'pfx_z': None,
        'release_x': None,
        'release_z': None,
        'sz_bot': None,
        'sz_top': None,

        # home & away
        'home': None,
        'away': None,
        'stadium': None,
        'referee': None,

        # home field
        'home_p': None,
        'home_c': None,
        'home_1b': None,
        'home_2b': None,
        'home_3b': None,
        'home_ss': None,
        'home_lf': None,
        'home_cf': None,
        'home_rf': None,
        'home_dh': None,

        # away field
        'away_p': None,
        'away_c': None,
        'away_1b': None,
        'away_2b': None,
        'away_3b': None,
        'away_ss': None,
        'away_lf': None,
        'away_cf': None,
        'away_rf': None,
        'away_dh': None,

        # home lineup
        'home_lineup': [
            # dummy 1~9
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0}
        ],

        # away lineup
        'away_lineup': [
            # dummy 1~9
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0}
        ]
    }

    # True 일 때 다음 타석/투구 전환->스코어, 아웃카운트, 이닝 초/말 등 변경.
    made_runs = False
    runs_how_many = 0
    made_outs = False
    outs_how_many = 0
    made_in_play = False
    runner_change = False
    change_1b = False
    change_2b = False
    change_3b = False
    next_1b = None
    next_2b = None
    next_3b = None
    ball_and_not_hbp = False
    set_hitter_to_base = False

    def __init__(self, game_date=None):
        # do nothing
        # print()
        if game_date is not None:
            self.game_status['game_date'] = game_date
        self.game_status['inning_topbot'] = 1
        self.game_status['inning'] = 0
        self.game_status['balls'] = 0
        self.game_status['strikes'] = 0
        self.game_status['outs'] = 0
        self.game_status['score_home'] = 0
        self.game_status['score_away'] = 0

        self.game_status['pa_result'] = None
        self.game_status['pitch_result'] = None

        self.game_status['runner_1b'] = None
        self.game_status['runner_2b'] = None
        self.game_status['runner_3b'] = None

        for i in range(10):
            self.game_status[field_away[i]] = None
            self.game_status[field_home[i]] = None

        self.game_status['home_lineup'] = [
            # dummy 1~9
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0}
        ]
        self.game_status['away_lineup'] = [
            # dummy 1~9
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0},
            {'pos': '', 'name': '', 'seqno': 0}
        ]

    def print_row(self):
        # dummy function
        print('\r')
        print(self.made_runs)

    def print_row_debug(self):
        # for debug
        row = str(self.game_status['pitch_result']) + ', '
        row += str(self.game_status['pitcher']) + ', '
        row += str(self.game_status['batter']) + ', '
        row += str(self.game_status['balls']) + '/'
        row += str(self.game_status['strikes']) + '/'
        row += str(self.game_status['outs']) + ', '
        row += str(self.game_status['inning'])
        if self.game_status['inning_topbot'] == 0:
            row += '초, '
        else:
            row += '말, '
        row += str(self.game_status['score_away']) + ':'
        row += str(self.game_status['score_home']) + ', '
        row += str(self.game_status['runner_1b']) + '/'
        row += str(self.game_status['runner_2b']) + '/'
        row += str(self.game_status['runner_3b']) + ', '
        row += str(self.game_status['pa_result']) + '\n'

        if self.game_status['inning_topbot'] == 0:
            row += str(self.game_status['home_p']) + '/'
            row += str(self.game_status['home_c']) + '/'
            row += str(self.game_status['home_1b']) + '/'
            row += str(self.game_status['home_2b']) + '/'
            row += str(self.game_status['home_3b']) + '/'
            row += str(self.game_status['home_ss']) + '/'
            row += str(self.game_status['home_lf']) + '/'
            row += str(self.game_status['home_cf']) + '/'
            row += str(self.game_status['home_rf'])
        else:
            row += str(self.game_status['away_p']) + '/'
            row += str(self.game_status['away_c']) + '/'
            row += str(self.game_status['away_1b']) + '/'
            row += str(self.game_status['away_2b']) + '/'
            row += str(self.game_status['away_3b']) + '/'
            row += str(self.game_status['away_ss']) + '/'
            row += str(self.game_status['away_lf']) + '/'
            row += str(self.game_status['away_cf']) + '/'
            row += str(self.game_status['away_rf'])
        print(row)

    def set_home_away(self, home, away):
        self.game_status['home'] = home
        self.game_status['away'] = away

    def set_referee(self, referee):
        self.game_status['referee'] = referee

    def set_stadium(self, stadium):
        self.game_status['stadium'] = stadium

    def set_lineup(self, js):
        away_lineup = js['awayTeamLineUp']
        home_lineup = js['homeTeamLineUp']
        for away_bat in away_lineup['batter']:
            order = away_bat['batOrder'] - 1
            if self.game_status['away_lineup'][order]['seqno'] == 0:
                self.game_status['away_lineup'][order]['pos'] = away_bat['posName']
                self.game_status['away_lineup'][order]['name'] = away_bat['name']
                self.game_status['away_lineup'][order]['seqno'] = away_bat['seqno']
                pos_num = position[away_bat['posName']]
                if pos_num < 10:
                    pos_name = field_away[pos_num]
                    self.game_status[pos_name] = away_bat['name']
            else:
                cur_seqno = self.game_status['away_lineup'][order]['seqno']
                if away_bat['seqno'] < cur_seqno:
                    self.game_status['away_lineup'][order]['pos'] = away_bat['posName']
                    self.game_status['away_lineup'][order]['name'] = away_bat['name']
                    self.game_status['away_lineup'][order]['seqno'] = away_bat['seqno']
                    pos_num = position[away_bat['posName']]
                    if pos_num < 10:
                        pos_name = field_away[pos_num]
                        self.game_status[pos_name] = away_bat['name']

        for home_bat in home_lineup['batter']:
            order = home_bat['batOrder'] - 1
            if self.game_status['home_lineup'][order]['seqno'] == 0:
                self.game_status['home_lineup'][order]['pos'] = home_bat['posName']
                self.game_status['home_lineup'][order]['name'] = home_bat['name']
                self.game_status['home_lineup'][order]['seqno'] = home_bat['seqno']
                pos_num = position[home_bat['posName']]
                if pos_num < 10:
                    pos_name = field_home[pos_num]
                    self.game_status[pos_name] = home_bat['name']
            else:
                cur_seqno = self.game_status['home_lineup'][order]['seqno']
                if home_bat['seqno'] < cur_seqno:
                    self.game_status['home_lineup'][order]['pos'] = home_bat['posName']
                    self.game_status['home_lineup'][order]['name'] = home_bat['name']
                    self.game_status['home_lineup'][order]['seqno'] = home_bat['seqno']
                    pos_num = position[home_bat['posName']]
                    if pos_num < 10:
                        pos_name = field_home[pos_num]
                        self.game_status[pos_name] = home_bat['name']

        for away_pit in away_lineup['pitcher']:
            if not (away_pit['seqno'] == 1):
                continue
            else:
                self.game_status['away_p'] = away_pit['name']

        for home_pit in home_lineup['pitcher']:
            if not (home_pit['seqno'] == 1):
                continue
            else:
                self.game_status['home_p'] = home_pit['name']

    # 이닝 변경
    def go_to_next_inning(self):
        if self.game_status['strikes'] == 3:
            self.game_status['strikes'] = 2
            # self.print_row()
            self.print_row_debug()
        if self.made_in_play is True:
            self.print_row_debug()
        if self.made_runs is True:
            if self.game_status['inning_topbot'] == 0:
                self.game_status['score_away'] += self.runs_how_many
            else:
                self.game_status['score_home'] += self.runs_how_many

        if self.made_outs is True:
            if self.game_status['outs'] + self.outs_how_many > 3:
                # write log
                # print('false out count')
                return False
        
        if self.game_status['inning_topbot'] == 1:
            self.game_status['inning'] += 1
        
        self.game_status['inning_topbot'] = (1-self.game_status['inning_topbot'])

        if self.game_status['inning_topbot'] == 0:
            self.game_status['pitcher'] = self.game_status['home_p']
        else:
            self.game_status['pitcher'] = self.game_status['away_p']

        self.game_status['pa_result'] = None
        self.game_status['pitch_result'] = None

        self.game_status['outs'] = 0
        self.game_status['runner_1b'] = None
        self.game_status['runner_2b'] = None
        self.game_status['runner_3b'] = None

        self.made_runs = False
        self.runs_how_many = 0
        self.made_outs = False
        self.outs_how_many = 0
        self.made_in_play = False
        self.runner_change = False
        self.change_1b = False
        self.change_2b = False
        self.change_3b = False
        self.next_1b = None
        self.next_2b = None
        self.next_3b = None
        self.ball_and_not_hbp = False
        self.set_hitter_to_base = False

    # 타석 리셋
    def go_to_next_pa(self):
        if self.made_in_play is True:
            # self.print_row()
            self.print_row_debug()
        elif self.game_status['strikes'] == 3:
            self.game_status['strikes'] = 2
            self.print_row_debug()
        elif self.game_status['balls'] == 4:
            self.game_status['balls'] = 3
            self.print_row_debug()
        elif self.game_status['pa_result'] is not None:
            if self.game_status['pa_result'].find('몸에') > -1:
                self.game_status['balls'] -= 1
                self.print_row_debug()

        self.game_status['balls'] = 0
        self.game_status['strikes'] = 0
        if self.made_runs is True:
            if self.game_status['inning_topbot'] == 0:
                self.game_status['score_away'] += self.runs_how_many
            else:
                self.game_status['score_home'] += self.runs_how_many

        if self.made_outs is True:
            self.game_status['outs'] += self.outs_how_many
            if self.game_status['outs'] > 3:
                # write log
                # print('false out count')
                return False

        if self.runner_change is True:
            if self.change_3b is True:
                self.game_status['runner_3b'] = self.next_3b

            if self.change_2b is True:
                self.game_status['runner_2b'] = self.next_2b

            if self.change_1b is True:
                self.game_status['runner_1b'] = self.next_1b

        self.game_status['pa_result'] = None
        self.game_status['pitch_result'] = None

        self.made_runs = False
        self.runs_how_many = 0
        self.made_outs = False
        self.outs_how_many = 0
        self.made_in_play = False
        self.runner_change = False
        self.next_1b = None
        self.next_2b = None
        self.next_3b = None
        self.change_1b = False
        self.change_2b = False
        self.change_3b = False
        self.ball_and_not_hbp = False
        self.set_hitter_to_base = False

    # 득점
    def score(self, runs):
        self.made_runs = True
        self.runs_how_many += runs

    # 아웃
    def out(self, outs):
        self.made_outs = True
        self.outs_how_many += outs

    # --------------------------------
    # pitch result
    # --------------------------------

    def get_ball(self):
        # 몸에맞는공의 경우 아무 카운트에서나 나온다
        # 다음 parse_pitch에서 결과를 확인하고 프린트
        self.game_status['pitch_result'] = '볼'
        cur_balls = self.game_status['balls']
        if cur_balls == 3:
            self.game_status['pa_result'] = '볼넷'
        else:
            # self.print_row()
            # self.print_row_debug()
            self.ball_and_not_hbp = True
        self.game_status['balls'] += 1

    def get_strike(self):
        self.game_status['pitch_result'] = '스트라이크'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 2:
            self.game_status['pa_result'] = '삼진'
        else:
            # self.print_row()
            self.print_row_debug()
        self.game_status['strikes'] += 1

    def get_swing_miss(self):
        self.game_status['pitch_result'] = '헛스윙'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 2:
            self.game_status['pa_result'] = '삼진'
        else:
            # self.print_row()
            self.print_row_debug()
        self.game_status['strikes'] += 1

    def get_bunt_swing_miss(self):
        self.game_status['pitch_result'] = '번트헛스윙'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 2:
            self.game_status['pa_result'] = '삼진'
        else:
            # self.print_row()
            self.print_row_debug()
        self.game_status['strikes'] += 1

    def get_foul(self):
        self.game_status['pitch_result'] = '파울'
        # self.print_row()
        self.print_row_debug()
        if self.game_status['strikes'] < 2:
            self.game_status['strikes'] += 1

    def get_bunt_foul(self):
        self.game_status['pitch_result'] = '번트파울'
        # self.print_row()
        self.print_row_debug()
        if self.game_status['strikes'] < 2:
            self.game_status['strikes'] += 1

    def get_in_play(self):
        self.game_status['pitch_result'] = '타격'
        self.made_in_play = True
        # print row -> @go_to_next_pa

    # --------------------------------
    # pa result
    # --------------------------------

    def single(self):
        self.game_status['pa_result'] = '1루타'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def double(self):
        self.game_status['pa_result'] = '2루타'
        self.runner_change = True
        self.change_2b = True
        self.next_2b = self.game_status['batter']
        self.set_hitter_to_base = True

    def triple(self):
        self.game_status['pa_result'] = '3루타'
        self.runner_change = True
        self.change_3b = True
        self.next_3b = self.game_status['batter']
        self.set_hitter_to_base = True

    def homerun(self):
        self.game_status['pa_result'] = '홈런'
        self.runner_change = True
        self.change_1b = True
        self.change_2b = True
        self.change_3b = True
        self.next_1b = None
        self.next_2b = None
        self.next_3b = None
        # runner score -> @runner
        self.score(1)

    def infield_hit(self):
        self.game_status['pa_result'] = '내야안타'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 기타 안타
    def other_hit(self):
        self.game_status['pa_result'] = '안타'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def strike_out(self):
        self.game_status['pa_result'] = '삼진'
        self.out(1)

    def four_ball(self):
        self.game_status['pa_result'] = '볼넷'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def ibb(self):
        self.game_status['pa_result'] = '고의4구'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def hbp(self):
        self.game_status['pa_result'] = '몸에 맞는 볼'
        self.runner_change = True
        self.change_1b = True
        self.ball_and_not_hbp = False
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 낫아웃 삼진
    def not_out(self):
        self.game_status['pa_result'] = '삼진'
        self.out(1)

    # 낫아웃 폭투
    def not_out_wp(self):
        self.game_status['pa_result'] = '낫아웃 폭투'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 낫아웃 포일
    def not_out_pb(self):
        self.game_status['pa_result'] = '낫아웃 포일'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 주자 포스 아웃, 타자 주자 출루
    # 땅볼로 출루
    def force_out(self):
        self.game_status['pa_result'] = '포스 아웃'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True
        # out -> @runner

    # 타자 주자 아웃
    # 땅볼 아웃, 플라이 아웃, 인필드 플라이, 파울 플라이
    # 라인드라이브 아웃, 번트 아웃
    # 현재 수비방해(송구방해)는 땅볼 아웃으로 기록 중
    def field_out(self):
        self.game_status['pa_result'] = '필드 아웃'
        self.out(1)

    def double_play(self):
        self.game_status['pa_result'] = '병살타'
        self.out(1)

    def sac_hit(self):
        self.game_status['pa_result'] = '희생번트'
        self.out(1)

    def sac_fly(self):
        self.game_status['pa_result'] = '희생플라이'
        self.out(1)

    def three_bunt(self):
        self.game_status['pa_result'] = '쓰리번트 삼진'
        self.out(1)

    def hit_by_ball_out(self):
        self.game_status['pa_result'] = '타구맞음 아웃'
        self.out(1)

    # 실책 출루
    # 플라이 실책, 번트 실책
    # 라인드라이브 실책, 병살실책, 실책
    def roe(self):
        self.game_status['pa_result'] = '실책'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def fc(self):
        self.game_status['pa_result'] = '야수선택'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 희생번트 실책
    def sac_hit_error(self):
        self.game_status['pa_result'] = '희생번트 실책'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    # 희생번트 야수선택
    def sac_hit_fc(self):
        self.game_status['pa_result'] = '희생번트 야수선택'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def interference(self):
        self.game_status['pa_result'] = '타격방해'
        self.runner_change = True
        self.change_1b = True
        self.next_1b = self.game_status['batter']
        self.set_hitter_to_base = True

    def triple_play(self):
        self.game_status['pa_result'] = '삼중살'
        self.out(1)

    # --------------------------------
    # runner result
    # --------------------------------

    # 도루, 폭투, 포일, 보크 포함
    # 진루 후 투구시 parse_pitch에서 next runner 업데이트
    def runner_advance(self, src_base, src_name, dst):
        # 2루주자 허경민 : 3루까지 진루
        # 3루주자 박건우 : 홈인

        # 1루주자 허경민 : 2루까지 진루
        # 2루주자 박건우 : 3루까지 진루
        if dst == 1:
            self.next_1b = src_name
            self.change_1b = True
        elif dst == 2:
            if src_base == 1:
                if self.change_1b is True:
                    # 이미 1루 주자 변경 있었음
                    if src_name == self.next_1b:
                        # 새 1루 주자가 진루한 경우
                        if self.set_hitter_to_base is True:
                            # 타자 주자 이름이 바로 나오는 경우
                            # (타자 이병규, 1루주자 이병규)
                            # -> 같은 주자로 보지 않는다
                            # 기존(새로 들어온) 1루 주자는 내버려둔다.
                            self.set_hitter_to_base = False
                        else:
                            # 1루를 비운다
                            self.next_1b = None
                else:
                    # 기존 1루 주자 진루.
                    self.next_1b = None
                    self.change_1b = True
            self.next_2b = src_name
            self.change_2b = True
        else:
            if src_base == 1:
                if self.change_1b is True:
                    # 이미 1루주자 변경 있었음
                    if src_name == self.next_1b:
                        # 새 1루 주자가 진루한 경우
                        if self.set_hitter_to_base is True:
                            # 타자 주자 이름이 바로 나오는 경우
                            # (타자 이병규, 1루주자 이병규)
                            # -> 같은 주자로 보지 않는다
                            # 기존(새로 들어온) 1루 주자는 내버려둔다.
                            self.set_hitter_to_base = False
                        else:
                            # 1루를 비운다
                            self.next_1b = None
                    # else:
                    # 기존 1루 주자가 진루
                    # self.next_1b는 그대로 보존
                else:
                    # 기존 1루 주자 진루.
                    self.next_1b = None
                    self.change_1b = True
            elif src_base == 2:
                if self.change_2b is True:
                    # 이미 2루주자 변경 있었음
                    if src_name == self.next_2b:
                        # 새 2루 주자가 진루한 경우
                        if self.set_hitter_to_base is True:
                            # 타자 주자 이름이 바로 나오는 경우
                            # (타자 이병규, 2루주자 이병규)
                            # -> 같은 주자로 보지 않는다
                            # 기존(새로 들어온) 2루 주자는 내버려둔다.
                            self.set_hitter_to_base = False
                        else:
                            # 2루를 비운다
                            self.next_2b = None
                    # else:
                    # 기존 2루 주자가 진루
                    # self.next_2b는 그대로 보존
                else:
                    # 기존 2루 주자 진루.
                    self.next_2b = None
                    self.change_2b = True
            self.next_3b = src_name
            self.change_3b = True

        self.runner_change = True

    def runner_home_in(self, src_base, src_name):
        self.score(1)
        if src_base == 1:
            if self.change_1b is True:
                # 이미 1루 주자 변경 있었음 -> 타자가 1루 진루
                if src_name == self.next_1b:
                    # 타자가 다시 진루, 홈인하는 경우
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 1루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 1루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 1루 주자를 홈인시킨다.
                        self.next_1b = None
                # else:
                # 기존 1루 주자가 홈인하는 경우(타자가 1루 진루)
                # self.next_1b는 그대로 보존
            else:
                # 기존 1루 주자가 홈인
                self.next_1b = None
                self.change_1b = True
        elif src_base == 2:
            if self.change_2b is True:
                # 이미 2루 주자 변경 있었음 -> 타자 혹은 1루 주자가 2루 진루
                if src_name == self.next_2b:
                    # 2루 들어온 새 주자가 진루, 홈인하는 경우
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 2루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 2루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 2루 주자를 홈인시킨다.
                        self.next_2b = None
                # else:
                # 기존 2루 주자가 홈인
                # self.next_2b는 그대로 보존
            else:
                # 기존 2루 주자가 홈인
                self.next_2b = None
                self.change_2b = True
        else:
            if self.change_3b is True:
                # 이미 2루 주자 변경 있었음 -> 타자 혹은 1/2루 주자가 3루 진루
                if src_name == self.next_3b:
                    # 3루 들어온 새 주자가 진루, 홈인하는 경우
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 3루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 3루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 3루 주자를 홈인시킨다.
                        self.next_3b = None
                # else:
                # 기존 3루 주자가 홈인
                # self.next_3b는 그대로 보존
            else:
                # 기존 3루 주자가 홈인
                self.next_3b = None
                self.change_3b = True
        self.runner_change = True

    # 도루실패, 견제사, 진루실패 포함
    def runner_out(self, src_base, src_name):
        self.out(1)
        if src_base == 1:
            if self.change_1b is True:
                # 1루 주자에 변경 있음
                if src_name == self.next_1b:
                    # 새로 들어온 1루 주자가 아웃
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 1루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 1루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 1루 주자가 아웃.
                        self.next_1b = None
                # else:
                # 기존 1루 주자가 아웃
                # self.next_1b는 그대로 보존; 새로 1루에 간 주자 이름이 들어감
            else:
                # 기존 1루 주자가 아웃
                self.next_1b = None
                self.change_1b = True
        elif src_base == 2:
            if self.change_2b is True:
                # 2루 주자에 변경 있음
                if src_name == self.next_2b:
                    # 새로 들어온 2루 주자가 아웃
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 2루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 2루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 2루 주자가 아웃.
                        self.next_2b = None
                # else:
                # 기존 2루 주자가 아웃
                # self.next_2b는 그대로 보존; 새로 2루에 간 주자 이름이 들어감
            else:
                # 기존 2루 주자가 아웃
                self.next_2b = None
                self.change_2b = True
        else:
            if self.change_3b is True:
                # 3루 주자에 변경 있음
                if src_name == self.next_3b:
                    # 새로 들어온 3루 주자가 아웃
                    if self.set_hitter_to_base is True:
                        # 타자 주자 이름이 바로 나오는 경우
                        # (타자 이병규, 3루주자 이병규)
                        # -> 같은 주자로 보지 않는다
                        # 기존(새로 들어온) 3루 주자는 내버려둔다.
                        self.set_hitter_to_base = False
                    else:
                        # 기존(새로 들어온) 3루 주자가 아웃.
                        self.next_3b = None
                # else:
                # 기존 3루 주자가 아웃
                # self.next_3b는 그대로 보존; 새로 3루에 간 주자 이름이 들어감
            else:
                # 기존 3루 주자가 아웃
                self.next_3b = None
                self.change_3b = True
        self.runner_change = True


##########

pa = regex.compile('^\p{Hangul}+ : [\p{Hangul}|0-9|\ ]+')
pitch = regex.compile('^[0-9]+구 \p{Hangul}+')
runner = regex.compile('^[0-9]루주자 \p{Hangul}+ : [\p{Hangul}|0-9|\ ()->]+')
change = regex.compile('교체$')
batter = regex.compile('^(([1-9]번타자)|(대타)) \p{Hangul}+')
src_pattern = regex.compile('[\p{Hangul}|0-9]+ \p{Hangul}+ : ')
dst_pattern = regex.compile('[\p{Hangul}|0-9|\ ]+ \(으\)로 교체')
dst_pattern2 = regex.compile('[\p{Hangul}|0-9|\ ]+\(으\)로 수비위치 변경')


def parse_result(text):
    if text.find('1루타') >= 0:
        return '1루타'
    elif text.find('2루타') >= 0:
        return

    return True


def parse_pa_result(text, ball_game):
    # do something
    # print(pa.search(text).group().split(':')[-1].strip())
    result = pa.search(text).group().split(':')[-1].strip()

    if result.find('삼진') >= 0:
        ball_game.strike_out()
    elif result.find('볼넷') >= 0:
        ball_game.four_ball()
    elif result.find('고의4구') >= 0:
        ball_game.ibb()
    elif result.find('몸에') >= 0:
        ball_game.hbp()
    elif result.find('1루타') >= 0:
        ball_game.single()
    elif result.find('내야안타') >= 0:
        ball_game.infield_hit()
    elif result.find('안타') >= 0:
        ball_game.other_hit()
    elif result.find('2루타') >= 0:
        ball_game.double()
    elif result.find('3루타') >= 0:
        ball_game.triple()
    elif result.find('홈런') >= 0:
        ball_game.homerun()
    elif result.find('낫아웃 폭투') >= 0:
        ball_game.not_out_wp()
    elif result.find('낫아웃 포일') >= 0:
        ball_game.not_out_pb()
    elif result.find('낫 아웃') >= 0:
        ball_game.not_out()
    elif result.find('낫아웃') >= 0:
        ball_game.not_out()
    elif result.find('땅볼로 출루') >= 0:
        ball_game.force_out()
    elif result.find('땅볼 아웃') >= 0:
        ball_game.field_out()
    elif result.find(' 플라이 아웃') >= 0:
        ball_game.field_out()
    elif result.find('인필드') >= 0:
        ball_game.field_out()
    elif result.find('파울플라이') >= 0:
        ball_game.field_out()
    elif result.find('라인드라이브 아웃') >= 0:
        ball_game.field_out()
    elif result.find(' 번트 아웃') >= 0:
        ball_game.field_out()
    elif result.find('병살타') >= 0:
        ball_game.double_play()
    elif result.find('희생번트 아웃') >= 0:
        ball_game.sac_hit()
    elif result.find('희생플라이 아웃') >= 0:
        ball_game.sac_fly()
    elif result.find('희생플라이아웃') >= 0:
        ball_game.sac_fly()
    elif result.find('쓰리번트') >= 0:
        ball_game.three_bunt()
    elif result.find('타구맞음') >= 0:
        ball_game.hit_by_ball_out()
    elif result.find('희생번트 실책') >= 0:
        ball_game.sac_hit_error()
    elif result.find('희생번트 야수선택') >= 0:
        ball_game.sac_hit_fc()
    elif result.find('야수선택') >= 0:
        ball_game.fc()
    elif result.find('실책') >= 0:
        ball_game.roe()
    elif result.find('타격방해') >= 0:
        ball_game.interference()
    elif result.find('삼중살') >= 0:
        ball_game.triple_play()
    elif result.find('부정타격') >= 0:
        ball_game.field_out()
    else:
        return False

    return True


def parse_pitch(text, ball_game):
    if ball_game.ball_and_not_hbp is True:
        ball_game.game_status['balls'] -= 1
        # ball_game.print_row()
        ball_game.print_row_debug()
        ball_game.game_status['balls'] += 1

    ball_game.ball_and_not_hbp = False
    ball_game.set_hitter_to_base = False

    if ball_game.runner_change is True:
        if ball_game.change_3b is True:
            ball_game.game_status['runner_3b'] = ball_game.next_3b

        if ball_game.change_2b is True:
            ball_game.game_status['runner_2b'] = ball_game.next_2b

        if ball_game.change_1b is True:
            ball_game.game_status['runner_1b'] = ball_game.next_1b

        ball_game.next_1b = None
        ball_game.next_2b = None
        ball_game.next_3b = None
        ball_game.change_1b = False
        ball_game.change_2b = False
        ball_game.change_3b = False
        ball_game.runner_change = False

    if ball_game.made_outs is True:
        ball_game.game_status['outs'] += ball_game.outs_how_many
        ball_game.made_outs = False
        ball_game.outs_how_many = 0

    if ball_game.made_runs is True:
        if ball_game.game_status['inning_topbot'] is 0:
            ball_game.game_status['score_away'] += ball_game.runs_how_many
        else:
            ball_game.game_status['score_home'] += ball_game.runs_how_many
        ball_game.made_runs = False
        ball_game.runs_how_many = 0

    # print(pitch.search(text).group().split(' ')[1])
    result = pitch.search(text).group().split(' ')[1]

    if result == '볼':
        ball_game.get_ball()
    elif result == '스트라이크':
        ball_game.get_strike()
    elif result == '번트파울':
        ball_game.get_bunt_foul()
    elif result == '파울':
        ball_game.get_foul()
    elif result == '번트헛스윙':
        ball_game.get_bunt_swing_miss()
    elif result == '헛스윙':
        ball_game.get_swing_miss()
    elif result == '타격':
        ball_game.get_in_play()
    elif result == 'C':
        ball_game.get_ball()
    elif result == '12초':
        ball_game.get_ball()
    return True


def parse_runner(text, ball_game):
    if ball_game.ball_and_not_hbp is True:
        ball_game.game_status['balls'] -= 1
        # ball_game.print_row()
        ball_game.print_row_debug()
        ball_game.game_status['balls'] += 1
    ball_game.ball_and_not_hbp = False
    result = runner.search(text).group()
    src_base = int(result.split(' ')[0][0])
    src_name = result.split(' ')[1]

    if result.find('진루') > 0:
        tokens = result.split(' ')
        for i in range(len(tokens)):
            if tokens[i].find('까지') >= 0:
                dst = int(tokens[i][0])
                break
        ball_game.runner_advance(src_base, src_name, dst)
    elif result.find('아웃') > 0:
        ball_game.runner_out(src_base, src_name)
    elif result.find('홈인') > 0:
        ball_game.runner_home_in(src_base, src_name)
    else:
        return False

    return True


def parse_change(text, ball_game):
    # 수비위치 변경, 교체
    change = False
    move = False
    src = src_pattern.search(text)
    if src:
        src_pos = src.group().strip().split(' ')[0]
        src_name = src.group().strip().split(' ')[1]
    else:
        return False

    dst = dst_pattern.search(text)
    if dst:
        dst_pos = dst.group().strip().split(' ')[0]
        dst_name = dst.group().strip().split(' ')[1]
        change = True
    else:
        dst2 = dst_pattern2.search(text)
        if dst2:
            dst_pos = dst2.group().strip().split('(')[0]
            move = True
        else:
            return False

    # do something
    if change:
        if (dst_pos == '대타') or (dst_pos == '대주자'):
            # print('대타')
            lineup_no = int(src_pos[0])
            if ball_game.game_status['inning_topbot'] == 0:
                # away
                if (ball_game.game_status['away_lineup'][lineup_no]['pos'] == src_pos) and\
                   (ball_game.game_status['away_lineup'][lineup_no]['name'] == src_name):
                    ball_game.game_status['away_lineup'][lineup_no]['pos'] = dst_pos
                    ball_game.game_status['away_lineup'][lineup_no]['name'] = dst_name
            else:
                # home
                if (ball_game.game_status['home_lineup'][lineup_no]['pos'] == src_pos) and\
                   (ball_game.game_status['home_lineup'][lineup_no]['name'] == src_name):
                    ball_game.game_status['home_lineup'][lineup_no]['pos'] = dst_pos
                    ball_game.game_status['home_lineup'][lineup_no]['name'] = dst_name

            if dst_pos == '대주자':
                src_base = int(src_pos[0])
                if src_base == 1:
                    ball_game.game_status['runner_1b'] = dst_name
                elif src_base == 2:
                    ball_game.game_status['runner_2b'] = dst_name
                else:
                    ball_game.game_status['runner_3b'] = dst_name
        else:
            # print('수비 교체')
            pos_num = position[dst_pos]
            if pos_num == 1:
                ball_game.game_status['pitcher'] = dst_name
            if ball_game.game_status['inning_topbot'] == 0:
                # away
                for i in range(9):
                    if (ball_game.game_status['home_lineup'][i]['pos'] == src_pos) and\
                       (ball_game.game_status['home_lineup'][i]['name'] == src_name):
                        ball_game.game_status['home_lineup'][i]['pos'] = dst_pos
                        ball_game.game_status['home_lineup'][i]['name'] = dst_name
                        break
                ball_game.game_status[field_home[pos_num]] = dst_name
            else:
                # home
                for i in range(9):
                    if (ball_game.game_status['away_lineup'][i]['pos'] == src_pos) and\
                       (ball_game.game_status['away_lineup'][i]['name'] == src_name):
                        ball_game.game_status['away_lineup'][i]['pos'] = dst_pos
                        ball_game.game_status['away_lineup'][i]['name'] = dst_name
                        break
                ball_game.game_status[field_away[pos_num]] = dst_name
        print('(C) {} {} -> {} {}'.format(src_pos, src_name, dst_pos, dst_name))
    elif move:
        # print('수비 위치 변경')
        pos_num = position[dst_pos]
        if pos_num == 1:
            ball_game.game_status['pitcher'] = dst_name
        if ball_game.game_status['inning_topbot'] == 0:
            # top; change home lineup
            ball_game.game_status[field_home[pos_num]] = src_name
            for i in range(9):
                if (ball_game.game_status['home_lineup'][i]['pos'] == src_pos) and\
                   (ball_game.game_status['home_lineup'][i]['name'] == src_name):
                    ball_game.game_status['home_lineup'][i]['pos'] = dst_pos
                    break
        else:
            # bot; change away lineup
            ball_game.game_status[field_away[pos_num]] = src_name
            for i in range(9):
                if (ball_game.game_status['away_lineup'][i]['pos'] == src_pos) and\
                   (ball_game.game_status['away_lineup'][i]['name'] == src_name):
                    ball_game.game_status['away_lineup'][i]['pos'] = dst_pos
                    break
        print('(M) {} {} -> {}'.format(src_pos, src_name, dst_pos))
    else:
        return False

    return True


def parse_batter(text, ball_game):
    result = batter.search(text).group().split(' ')[-1]

    # substitution - > @parse_change
    ball_game.go_to_next_pa()
    ball_game.game_status['batter'] = result

    return True


def parse_text(text, text_type, ball_game, game_over):
    if text_type == 0:
        return ball_game.go_to_next_inning()
    elif text_type == 1:
        return parse_pitch(text, ball_game)
    elif text_type == 2:
        return parse_change(text, ball_game)
    elif text_type == 7:
        # system text
        return True
    elif text_type == 8:
        # batter name
        # return True
        return parse_batter(text, ball_game)
    elif text_type == 13:
        return parse_pa_result(text, ball_game)
    elif text_type == 14:
        return parse_runner(text, ball_game)
    elif text_type == 23:
        # with home-in
        return parse_pa_result(text, ball_game)
    elif text_type == 24:
        # with home-in
        return parse_runner(text, ball_game)
    elif text_type == 44:
        # foul error; pass
        return True
    elif text_type == 99:
        # game end
        game_over[0] = True
        return True
    else:
        return True


# main function
def parse_game(game):
    fp = open(game, 'r', encoding='utf-8')
    js = json.loads(fp.read(), encoding='utf-8', object_pairs_hook=OrderedDict)
    fp.close()

    ball_game = BallGame(game_date=game[:8])

    ball_game.set_home_away(game[10:12], game[8:10])

    ball_game.set_referee(js['referee'])
    ball_game.set_stadium(js['stadium'])

    ball_game.set_lineup(js)

    rl = js['relayList']

    game_over = [False]
    for k in range(len(rl.keys())):
        text_set = rl[str(k)]['textOptionList']
        for i in range(len(text_set)):
            text = text_set[i]['text']
            text_type = text_set[i]['type']

            if parse_text(text, text_type, ball_game, game_over) is False:
                # game over
                break

        if game_over[0]:
            break

    return True


def parse_main(args, lm=None):
    # parse arguments
    # test
    mon_start = args[0]
    mon_end = args[1]
    year_start = args[2]
    year_end = args[3]

    if lm is not None:
        lm.resetLogHandler()
        lm.setLogPath(os.getcwd())
        lm.setLogFileName('parse_pitch_log.txt')
        lm.cleanLog()
        lm.createLogHandler()
        lm.log('---- Relay Text Parse Log ----')

    if not os.path.isdir('pbp_data'):
        print('no data folder')
        return False

    os.chdir('pbp_data')

    for year in range(year_start, year_end + 1):
        if not os.path.isdir(str(year)):
            print('no year dir')
            os.chdir('..')
            return False

        os.chdir(str(year))

        for month in range(mon_start, mon_end + 1):
            if not os.path.isdir(str(month)):
                print('no month dir')
                os.chdir('../../')
                return False

            os.chdir(str(month))

            games = [f for f in os.listdir('.') if (os.path.isfile(f)) and
                                                   (f.lower().find('relay.json') > 0) and
                                                   (os.path.getsize(f) > 512)]
            if not len(games) > 0:
                print('no games')
                os.chdir('..')
                continue

            games.sort()

            for game in games:
                rc = parse_game(game)
                if rc is False:
                    print('parse game failure')
                    os.chdir('../../../')
                    return False

            # end
            os.chdir('..')

        # end
        os.chdir('..')

    # end
    os.chdir('..')
