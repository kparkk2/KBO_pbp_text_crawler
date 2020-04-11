import os
import json
from collections import OrderedDict
import regex
import csv

import pandas as pd
import numpy as np
import sys

# custom library
from utils import print_progress

header_row = ['pitch_type', 'pitcher', 'batter', 'pitcher_ID', 'batter_ID',
              'speed', 'pitch_result', 'pa_result', 'balls', 'strikes', 'outs',
              'inning', 'inning_topbot', 'score_away', 'score_home',
              'stands', 'throws', 'on_1b', 'on_2b', 'on_3b',
              'px', 'pz', 'pfx_x', 'pfx_z', 'pfx_x_raw', 'pfx_z_raw',
              'x0', 'z0', 'sz_top', 'sz_bot', 'pos_1', 'pos_2', 'pos_3', 'pos_4', 'pos_5',
              'pos_6', 'pos_7', 'pos_8', 'pos_9', 'game_date', 'home', 'away',
              'stadium', 'referee', 'pa_number', 'pitch_number',
              'y0', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'pitchID']  # raw data 추가

def parse_pitch_result(text):
    res = text.split(' ')[-1]
    if res == '볼':
        return 'b'
    elif res == '스트라이크':
        return 's'
    elif res == '헛스윙':
        return 'm'
    elif res == '파울':
        return 'f'
    elif res == '타격':
        return 'h'
    else:
        return None

    
batter_result = [
    ['삼진', '삼진', '삼진'],
    ['볼넷', '볼넷', '볼넷'],
    ['자동 고의 4구', '고의 4구', '고의 4구'],
    ['자동 고의4구', '고의 4구', '고의 4구'],
    ['고의4구', '고의 4구', '고의 4구'],
    ['몸에', '몸에 맞는 공', '몸에 맞는 공'],
    ['1루타', '안타', '안타'],
    ['내야안타', '내야 안타', '내야 안타'],
    ['번트안타', '번트 안타', '번트 안타'],
    ['안타', '안타', '안타'],
    ['2루타', '2루타', '2루타'],
    ['3루타', '3루타', '3루타'],
    ['홈런', '홈런', '홈런'],
    ['낫아웃 폭투', '낫아웃 출루', '낫아웃 폭투'],
    ['낫아웃 포일', '낫아웃 출루', '낫아웃 포일'],
    ['낫 아웃', '삼진', '낫아웃 삼진'],
    ['낫아웃 다른주자 수비 실책', '낫아웃 출루', '낫아웃 다른 주자 수비 실책'],
    ['낫아웃 다른주자 수비', '낫아웃 출루', '낫아웃 다른 주자 포스 아웃'],
    ['땅볼로 출루', '포스 아웃', '포스 아웃'],
    ['땅볼 아웃', '포스 아웃', '포스 아웃'],
    ['플라이 아웃', '필드 아웃', '필드 아웃'],
    ['인필드', '필드 아웃', '인필드 플라이'],
    ['파울플라이', '필드 아웃', '파울 플라이 아웃'],
    ['라인드라이브 아웃', '필드 아웃', '라인드라이브 아웃'],
    ['번트 아웃', '필드 아웃', '번트 아웃'],
    ['병살타', '병살타', '병살타'],
    ['희생번트 아웃', '희생 번트', '희생 번트'],
    ['희생플라이 아웃', '희생 플라이', '희생 플라이'],
    ['희생플라이아웃', '희생 플라이', '희생 플라이'],
    ['쓰리번트', '삼진', '쓰리번트 삼진'],
    ['타구맞음', '필드 아웃', '타구맞음 아웃'],
    ['희생번트 실책', '실책', '실책'],
    ['희생번트 야수선택', '야수 선택', '야수 선택'],
    ['야수선택', '야수 선택', '야수 선택'],
    ['실책', '실책', '실책'],
    ['타격방해', '타격 방해', '타격 방해'],
    ['삼중살', '삼중살', '삼중살'],
    ['부정타격', '필드 아웃', '부정 타격 아웃'],
    ['번트', '번트 안타', '안타'],
]


def parse_batter_result(text):
    for tup in batter_result:
        if text.find(tup[0]) >= 0:
            return tup[1], tup[2]


def parse_batter_as_runner(text):
    runner = text.split(' ')[0]
    
    result = 'o' if text.find('아웃') > 0 else 'a'
    result = 'h' if text.find('홈런') > 0 else result
    
    before_base = 0
    after_base = None
    if any([s in text for s in ['안타', '1루타', '4구', '볼넷', '출루', '낫아웃 포일', '낫아웃 폭투', '몸에 맞는', '낫아웃 다른주자']]):
        after_base = 1
    elif '2루타' in text:
        after_base = 2
    elif '3루타' in text:
        after_base = 3
    elif '홈런' in text:
        after_base = 4
    elif '아웃' in text:
        after_base = None
    
    return [runner, result, before_base, after_base]


def parse_runner_result(text):
    runner = text.split(' ')[1]
    
    result = 'o' if text.find('아웃') > 0 else 'a' # o : out, a : advance
    result = 'h' if text.find('홈인') > 0 else result # 'h' : home-in
    
    before_base = int(text[0])
    after_base = None if result != 'a' else int(text[text.find('루까지')-1])
    after_base = 4 if result == 'h' else after_base
    
    return [runner, result, before_base, after_base]



class game_status:
    def __init__ (self):
        # game data frame
        self.pitching_df = None
        self.batting_df = None
        self.relay_df = None
        
        # game meta data
        self.game_date = None
        self.away = None
        self.home = None
        self.stadium = None
        self.referee = None
        self.game_id = None
        
        # lineup(order), fielding position
        self.lineups = [[], []] # 초 공격 / 말 공격
        self.fields = [{}, {}] # 초 수비 / 말 수비
        
        # status change at pa, inning
        self.pa_number = 0
        self.is_pitcher_batting = [False, False]
        self.top_bot = 1 # 0 : 초, 1 : 말
        self.cur_order = 1
        self.stands = None
        self.throws = None
        
        # status by pitch, etc.
        self.bases = [None, None, None]
        self.after_bases = [None, None, None]
        self.base_change = [False, False, False]
        self.score = [0, 0] # 초공(어웨이), 말공(홈)
        self.balls, self.outs, self.strikes = 0, 0, 0
        self.pitch_number = 0
    
    def load_game_csv(self, game_id):
        self.game_id = game_id
        year = game_id[:4]
        month = int(game_id[4:6])
        pl = '_pitching.csv'
        bl = '_batting.csv'
        rl = '_relay.csv'
        
        tcol = ['textOrder', 'seqno', 'text', 'type', 'stuff',
                'pitchId', 'speed', 'referee', 'stadium', 'inn',
                'topbot', 'stance']
        pcol = ['pitchId', 'speed', 'crossPlateX',
                'vx0', 'vy0', 'vz0', 'x0', 'z0', 'ax', 'ay', 'az',
                'topSz', 'bottomSz']
        scol = ['outPlayer', 'inPlayer', 'shiftPlayer']

        enc = 'cp949' if sys.platform == 'win32' else 'utf8'
        self.pitching_df = pd.read_csv(f'pbp_data/{year}/{month}/{game_id}{pl}',
                                       encoding=enc)
        self.batting_df = pd.read_csv(f'pbp_data/{year}/{month}/{game_id}{bl}',
                                      encoding=enc)
        self.relay_df = pd.read_csv(f'pbp_data/{year}/{month}/{game_id}{rl}',
                                    encoding=enc)
        self.relay_df.sort_values(['textOrder', 'seqno'], inplace=True)

        self.game_date = game_id[:8]
        self.away = game_id[8:10]
        self.home = game_id[10:12]
        self.stadium = rdf.stadium.unique()[0]
        self.referee = rdf.referee.unique()[0]
        
    def load_players(self):
        bdf = self.batting_df
        pdf = self.pitching_df
        
        bats = [bdf.loc[bdf.homeaway == 'a'],
                bdf.loc[bdf.homeaway == 'h']]
        pits = [pdf.loc[pdf.homeaway == 'a'],
                pdf.loc[pdf.homeaway == 'h']]
        abat_seqno_min = bats[0].groupby('batOrder').seqno.min().tolist()
        hbat_seqno_min = bats[1].groupby('batOrder').seqno.min().tolist()

        for i in range(9):
            aCode = bats[0].loc[(bats[0].batOrder == i+1) &
                                (bats[0].seqno == abat_seqno_min[i])].pCode.values[0]
            aName = bats[0].loc[(bats[0].batOrder == i+1) &
                                (bats[0].seqno == abat_seqno_min[i])].name.values[0]
            hCode = bats[1].loc[(bats[1].batOrder == i+1) &
                                (bats[1].seqno == hbat_seqno_min[i])].pCode.values[0]
            hName = bats[1].loc[(bats[1].batOrder == i+1) &
                                (bats[1].seqno == hbat_seqno_min[i])].name.values[0]
            aPlayer = {'name': aName, 'code': aCode}
            hPlayer = {'name': hName, 'code': hCode}

            aPos = bats[0].loc[bats[0].pCode == aCode].posName.values[0]
            hPos = bats[1].loc[bats[1].pCode == hCode].posName.values[0]
            self.fields[1][aPos] = aPlayer
            self.fields[0][hPos] = hPlayer

            aLineup = {'name': aName, 'code': aCode, 'pos': aPos}
            hLineup = {'name': hName, 'code': hCode, 'pos': hPos}
            self.lineups[0].append(aLineup)
            self.lineups[1].append(hLineup)

        aPitcher = {'name': pits[0].iloc[0]['name'], 'code': pits[0].iloc[0].pCode}
        hPitcher = {'name': pits[1].iloc[0]['name'], 'code': pits[1].iloc[0].pCode}
        self.fields[1]['투수'] = aPitcher
        self.fields[0]['투수'] = hPitcher

    def set_innings(self):
        inn = 0
        topbot = 'b'

        inns = []
        topbots = []

        for ind in self.relay_df.index:
            row = self.relay_df.loc[ind]
            if row.type == 0:
                inns.append(inn+1) if topbot == 'b' else inns.append(inn)
                topbots.append('t') if topbot == 'b' else topbots.append('b')
                inn = inn+1 if topbot == 'b' else inn
                topbot = 't' if topbot == 'b' else 'b'
            else:
                inns.append(inn)
                topbots.append(topbot)

        self.relay_df['inn'] = inns
        self.relay_df['topbot'] = topbots

        # maxSeqnoInPA = self.relay_df.groupby(['inn', 'topbot', 'textOrder']).seqno.transform('max')
        # self.relay_df['maxSeqnoInPA'] = maxSeqnoInPA
        
    