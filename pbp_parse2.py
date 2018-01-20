# pbp_parse2.py

import os
import json
from collections import OrderedDict
import regex

pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수",
              "지명타자", "대타", "대주자"]

bb_dir_string = ["투수", "포수", "1루수", "2루수", "3루수",
                 "유격수", "좌익수", "중견수", "우익수",
                 "우중간", "좌중간"]

res_string = ["1루타", "안타" "2루타", "3루타", "홈런", "실책", "땅볼",
              "뜬공", "희생플라이", "희생번트", "야수선택", "삼진",
              "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타"]

hit_results = ['안타', '1루타', '2루타', '3루타', '홈런']

out_results = ['땅볼', '플라이', '병살타', '라인드라이브',
               ' 번트', '희생번트', '삼중살']

nobb_outs = ['삼진', '낫 아웃', '타구맞음', '쓰리번트', '부정타격']

runner_outs = ['견제사', '  포스아웃', '  태그아웃',
               '도루실패', '진루실패', '터치아웃', '공과']

pass_games = ['20130609HHSK', '20130611LGHH', '20170509KTHT', '20130619LGNC',
              '20130912HTLG', '20140829LGSK', '20141017LGLT', '20150426LGNC',
              '20150505LGOB', '20150612LGHH', '20120513LTHH', '20120601HHLG',
              '20120603HHLG', '20120607LGWO', '20120613SKLG', '20120621LGHH',
              '20120630LGSK', '20120719SKLG', '20120725LGOB']

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
              # 희생번트로 기록
              '희생번트 실책',
              # 희생번트로 기록
              '희생번트 야수선택',
              '야수선택',
              # 플라이 실책, 번트 실책, 라인드라이브 실책, 병살실책, 실책
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

pa = regex.compile('^\p{Hangul}+ : [\p{Hangul}|0-9|\ ]+')
pitch = regex.compile('^[0-9]+구 \p{Hangul}+')
runner = regex.compile('^[0-9]루주자 \p{Hangul}+ : [\p{Hangul}|0-9|\ ()->]+')
change = regex.compile('교체$')


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

        # base
        'runner_1b': None,
        'runner_2b': None,
        'runner_3b': None,

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
        'away_dh': None
    }

    # True 일 때 다음 타석/투구 전환->스코어, 아웃카운트, 이닝 초/말 등 변경.
    made_runs = False
    runs_how_many = 0
    made_outs = False
    outs_how_many = 0
    topbot_change = False
    runner_change = False
    next_1b = None
    next_2b = None
    next_3b = None

    def __init__(self, game_date=None):
        # do nothing
        # print()
        if game_date is not None:
            self.game_status['game_date'] = game_date

    def print_row(self):
        print('\r')

    def set_home_away(self, home, away):
        self.game_status['home'] = home
        self.game_status['away'] = away

    def set_referee(self, referee):
        self.game_status['referee'] = referee

    def set_stadium(self, stadium):
        self.game_status['stadium'] = stadium

    # 타석 리셋
    def go_to_next_pa(self):
        self.print_row()
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
                print('false out count')
                return False

        if self.topbot_change is True:
            self.game_status['inning_topbot'] = (1 - self.game_status['inning_topbot'])
            self.game_status['outs'] = 0

        self.game_status['runner_3b'] = self.next_3b
        self.game_status['runner_2b'] = self.next_2b
        self.game_status['runner_1b'] = self.next_1b

        self.runs_how_many = 0
        self.outs_how_many = 0
        self.made_runs = False
        self.made_outs = False
        self.topbot_change = False

    # 득점
    def score(self, runs):
        self.made_runs = True
        self.runs_how_many += runs

    # 아웃
    def out(self, outs):
        self.made_outs = True
        self.outs_how_many += outs

    def get_ball_four(self):
        self.game_status['pa_result'] = '볼넷'

        runner_1b = self.game_status['runner_1b']
        runner_2b = self.game_status['runner_2b']
        # runner_3b = self.game_status['runner_3b']

        self.next_1b = self.game_status['batter']
        self.next_2b = runner_1b
        self.next_3b = runner_2b
        self.score(1)

    # --------------------------------
    # pitch result
    # --------------------------------

    def get_ball(self):
        self.game_status['pitch_result'] = '볼'
        cur_balls = self.game_status['balls']
        if cur_balls == 4:
            self.game_status['pa_result'] = '볼넷'
        self.print_row()
        self.game_status['balls'] += 1
        '''
        cur_balls = self.game_status['balls']
        if cur_balls == 4:
            self.get_ball_four()
            self.go_to_next_pa()
        else:
            self.print_row()
        '''

    def get_strike(self):
        self.game_status['pitch_result'] = '스트라이크'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 3:
            self.game_status['pa_result'] = '삼진'
        self.print_row()
        self.game_status['strikes'] += 1

    def get_swing_miss(self):
        self.game_status['pitch_result'] = '헛스윙'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 3:
            self.game_status['pa_result'] = '삼진'
        self.print_row()
        self.game_status['strikes'] += 1

    def get_bunt_swing_miss(self):
        self.game_status['pitch_result'] = '번트헛스윙'
        cur_strikes = self.game_status['strikes']
        if cur_strikes == 3:
            self.game_status['pa_result'] = '삼진'
        self.print_row()
        self.game_status['strikes'] += 1

    def get_foul(self):
        self.game_status['pitch_result'] = '파울'
        self.print_row()
        if self.game_status['strikes'] < 2:
            self.game_status['strikes'] += 1

    def get_bunt_foul(self):
        self.game_status['pitch_result'] = '번트파울'
        self.print_row()
        if self.game_status['strikes'] < 2:
            self.game_status['strikes'] += 1

    def get_in_play(self):
        self.game_status['pitch_result'] = '타격'
        self.print_row()

    # --------------------------------
    # pa result
    # --------------------------------

    def single(self):
        self.game_status['pa_result'] = '1루타'
        self.next_1b = self.game_status['batter']

    def double(self):
        self.game_status['pa_result'] = '2루타'
        self.next_2b = self.game_status['batter']

    def triple(self):
        self.game_status['pa_result'] = '3루타'
        self.next_3b = self.game_status['batter']

    def homerun(self):
        self.game_status['pa_result'] = '홈런'
        self.next_1b = None
        self.next_2b = None
        self.next_3b = None
        # runner score -> @runner
        self.score(1)

    def infield_hit(self):
        self.game_status['pa_result'] = '내야안타'
        self.next_1b = self.game_status['batter']

    # 기타 안타
    def other_hit(self):
        self.game_status['pa_result'] = '안타'
        self.next_1b = self.game_status['batter']

    def strike_out(self):
        self.game_status['pa_result'] = '삼진'
        self.out(1)

    def four_ball(self):
        self.game_status['pa_result'] = '볼넷'
        self.next_1b = self.game_status['batter']

    def ibb(self):
        self.game_status['pa_result'] = '고의4구'
        self.next_1b = self.game_status['batter']

    def hbp(self):
        self.game_status['pa_result'] = '몸에 맞는 볼'
        self.next_1b = self.game_status['batter']

    # 낫아웃 삼진
    def not_out(self):
        self.game_status['pa_result'] = '삼진'
        self.out(1)

    # 낫아웃 폭투
    def not_out_wp(self):
        self.game_status['pa_result'] = '낫아웃 폭투'
        self.next_1b = self.game_status['batter']

    # 낫아웃 포일
    def not_out_pb(self):
        self.game_status['pa_result'] = '낫아웃 포일'
        self.next_1b = self.game_status['batter']

    # 주자 포스 아웃, 타자 주자 출루
    # 땅볼로 출루
    def force_out(self):
        self.game_status['pa_result'] = '포스 아웃'
        self.next_1b = self.game_status['batter']
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
    # 희생번트 실책, 플라이 실책, 번트 실책
    # 라인드라이브 실책, 병살실책, 실책
    def roe(self):
        self.game_status['pa_result'] = '실책'
        self.next_1b = self.game_status['batter']

    def interference(self):
        self.game_status['pa_result'] = '타격방해'
        self.next_1b = self.game_status['batter']

    def triple_play(self):
        self.game_status['pa_result'] = '삼중살'
        self.out(1)

    # --------------------------------
    # runner result
    # --------------------------------

    # 도루, 폭투, 포일, 보크 포함
    # 진루 후 투구시 parse_pitch에서 next runner 업데이트
    def runner_advance(self, src, dst):
        runner = ''
        if src == '1루':
            runner = self.game_status['runner_1b']
        elif src == '2루':
            runner = self.game_status['runner_2b']
        else:
            runner = self.game_status['runner_3b']

        if dst == '1루':
            self.next_1b = runner
        elif dst == '2루':
            self.next_2b = runner
        else:
            self.next_3b = runner
        self.runner_change = True

    def runner_home_in(self, src):
        self.score(1)
        if src == '1루':
            self.next_1b = None
        elif src == '2루':
            self.next_2b = None
        else:
            self.next_3b = None
        self.runner_change = True

    # 도루실패, 견제사, 진루실패 포함
    def runner_out(self, src):
        self.out(1)
        if src == '1루':
            self.next_1b = None
        elif src == '2루':
            self.next_2b = None
        else:
            self.next_3b = None
        self.runner_change = True


##########

def parse_pa_result(text, ball_game):
    # do something
    print(pa.search(text).group().split(':')[-1].strip())
    result = pa.search(text).group().split(':')[-1].strip()

    if result == '삼진':
        ball_game.strike_out()

    return True


def parse_pitch(text, ball_game):
    # do something
    if ball_game.runner_change is True:
        ball_game.game_status['runner_1b'] = ball_game.next_1b
        ball_game.game_status['runner_2b'] = ball_game.next_2b
        ball_game.game_status['runner_3b'] = ball_game.next_3b
        ball_game.next_1b = None
        ball_game.next_2b = None
        ball_game.next_3b = None

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

    print(pitch.search(text).group().split(' ')[1])
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
    elif result == 'C':
        ball_game.get_ball()
    elif result == '12초':
        ball_game.get_ball()
    return True


def parse_runner(text, ball_game):
    # do something
    if not change.findall(text):
        print(runner.search(text).group().split(':')[-1].strip())
    return True


def parse_change(text, ball_game):
    src_pattern = regex.compile('[\p{Hangul}|0-9]+ \p{Hangul}+ : ')
    dst_pattern = regex.compile('[\p{Hangul}|0-9|\ ]+ \(으\)로 교체')

    src = src_pattern.search(text).group()
    if src:
        src_pos = src.strip().split(' ')[0]
        src_name = src.strip().split(' ')[1]
    else:
        return False

    dst = dst_pattern.search(text).group()
    if dst:
        dst_pos = dst.strip().split(' ')[0]
        dst_name = dst.strip().split(' ')[1]
    else:
        return False

    # do something
    print('{} {} -> {} {}'.format(src_pos, src_name, dst_pos, dst_name))
    return True


def parse_text(text, text_type, ball_game, game_over):
    if text_type == 2:
        return parse_change(text, ball_game)
    elif text_type == 1:
        return parse_pitch(text, ball_game)
    elif text_type == 13:
        return parse_pa_result(text, ball_game)
    elif text_type == 14:
        return parse_runner(text, ball_game)
    elif text_type == 7:
        # system text
        return True
    elif text_type == 8:
        # batter name
        return True
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
        if not game_over[0]:
            ball_game.go_to_next_pa()
        else:
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
