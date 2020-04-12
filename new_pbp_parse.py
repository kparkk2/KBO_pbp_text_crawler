import os
import json
from collections import OrderedDict
import regex
import csv

import pandas as pd
import numpy as np
import sys
import pathlib

# custom library
from utils import print_progress

header_row = ['pitch_type', 'pitcher', 'batter', 'pitcher_ID', 'batter_ID',
              'speed', 'pitch_result', 'pa_result', 'pa_result_detail',
              'description', 'balls', 'strikes', 'outs',
              'inning', 'inning_topbot', 'score_away', 'score_home',
              'stands', 'throws', 'on_1b', 'on_2b', 'on_3b',
              'pos_1', 'pos_2', 'pos_3', 'pos_4', 'pos_5',
              'pos_6', 'pos_7', 'pos_8', 'pos_9',
              'px', 'pz', 'pfx_x', 'pfx_z', 'pfx_x_raw', 'pfx_z_raw',
              'x0', 'z0', 'sz_top', 'sz_bot',
              'y0', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az',
              'game_date', 'home', 'away', 'home_alias', 'away_alias',
              'stadium', 'referee', 'pa_number', 'pitch_number', 'pitchID']

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


def get_pitch_location_break(row):
    if 'x0' not in row.index:
        return [None]*6
    else:
        ax = row.ax
        ay = row.ay
        az = row.ax
        vx0 = row.vx0
        vy0 = row.vy0
        vz0 = row.vz0
        x0 = row.x0
        y0 = 50
        z0 = row.z0
        cpy = 1.4167

        # do math
        t = (-vy0 - (vy0 * vy0 - 2 * ay * (y0 - cpy)) ** 0.5) / ay

        t40 = (-vy0 - (vy0 * vy0 - 2 * ay * (y0 - 40)) ** 0.5) / ay
        x40 = x0 + vx0 * t40 + 0.5 * ax * t40 * t40
        vx40 = vx0 + ax * t40
        z40 = z0 + vz0 * t40 + 0.5 * az * t40 * t40
        vz40 = vz0 + az * t40
        th = t - t40
        x_no_air = x40 + vx40 * th
        z_no_air = z40 + vz40 * th - 0.5 * 32.174 * th * th
        z_no_induced = z0 + vz0 * t

        px = x0 + vx0 * t + ax * t * t * 0.5
        pz = z0 + vz0 * t + az * t * t * 0.5

        pfx_x = (px - x_no_air) * 12
        pfx_z = (pz - z_no_air) * 12
        pfx_x_raw = px * 12
        pfx_z_raw = (pz - z_no_induced) * 12

        return px, pz, pfx_x, pfx_z, pfx_x_raw, pfx_z_raw


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
        self.away_alias = None
        self.home_alias = None
        self.stadium = None
        self.referee = None
        self.game_id = None
        
        # current game numbers, names, codes, etc.
        self.score = [0, 0]
        self.batter_name = None
        self.batter_code = -1
        self.pitcher_name = None
        self.pitcher_code = -1
        self.stands = None
        self.throws = None
        self.DH_exist = [True, True]
        self.DH_exist_after = [True, True]
        
        # lineup(order), fielding position, base
        self.lineups = [[], []] # 초 공격 / 말 공격
        self.fields = [{}, {}] # 초 수비 / 말 수비
        self.bases = [None, None, None]
        self.after_bases = [None, None, None]
        self.base_change = [False, False, False]
        
        # status change at pa, inning
        self.pa_number = 0
        self.inn = 0
        self.top_bot = 1 # 0 : 초, 1 : 말
        self.cur_order = 1
        
        # status by pitch, etc.
        self.pitch_number = 0
        self.bases = [None, None, None]
        self.score = [0, 0] # 초공(어웨이), 말공(홈)
        self.balls, self.outs, self.strikes = 0, 0, 0
        self.last_pitch = None
        
        # pitch result, pa result
        self.pitch_result = None
        self.pa_result = None
        self.pa_result_detail = None
        self.description = ''        
        
        # print rows
        self.print_rows = []
        
        # debug mode
        self.DEBUG_MODE = False
    

    def toggle_debug(self, mode):
        if type(mode) == bool:
            self.DEBUG_MODE = mode
        
    def load(self, game_id, pdf, bdf, rdf):
        self.pitching_df = pdf
        self.batting_df = bdf
        self.relay_df = rdf.sort_values('seqno')
        self.game_id = game_id
        
        self.game_date = game_id[:8]
        self.away = game_id[8:10]
        self.home = game_id[10:12]
        self.stadium = rdf.stadium.unique()[0]
        self.referee = rdf.referee.unique()[0]
        self.away_alias = pdf.loc[pdf.homeaway == 'a'].team_name.unique()[0]
        self.home_alias = pdf.loc[pdf.homeaway == 'h'].team_name.unique()[0]
        
        bats = [bdf.loc[bdf.homeaway == 'a'],
                bdf.loc[bdf.homeaway == 'h']]
        pits = [pdf.loc[pdf.homeaway == 'a'],
                pdf.loc[pdf.homeaway == 'h']]
        abat_seqno_min = bats[0].groupby('batOrder').seqno.min().tolist()
        hbat_seqno_min = bats[1].groupby('batOrder').seqno.min().tolist()

        for i in range(9):
            away_code = bats[0].loc[(bats[0].batOrder == i+1) &
                                    (bats[0].seqno == abat_seqno_min[i])].pCode.values[0]
            away_name = bats[0].loc[(bats[0].batOrder == i+1) &
                                    (bats[0].seqno == abat_seqno_min[i])].name.values[0]
            home_code = bats[1].loc[(bats[1].batOrder == i+1) &
                                    (bats[1].seqno == hbat_seqno_min[i])].pCode.values[0]
            home_name = bats[1].loc[(bats[1].batOrder == i+1) &
                                    (bats[1].seqno == hbat_seqno_min[i])].name.values[0]
            away_player = {'name': away_name, 'code': away_code}
            home_player = {'name': home_name, 'code': home_code}

            away_pos = bats[0].loc[bats[0].pCode == away_code].posName.values[0]
            home_pos = bats[1].loc[bats[1].pCode == home_code].posName.values[0]
            self.fields[1][away_pos] = away_player
            self.fields[0][home_pos] = home_player

            away_lineup = {'name': away_name, 'code': int(away_code), 'pos': away_pos}
            home_lineup = {'name': home_name, 'code': int(home_code), 'pos': home_pos}
            self.lineups[0].append(away_lineup)
            self.lineups[1].append(home_lineup)

        away_pitcher = {'name': pits[0].iloc[0]['name'], 'code': int(pits[0].iloc[0].pCode)}
        home_pitcher = {'name': pits[1].iloc[0]['name'], 'code': int(pits[1].iloc[0].pCode)}
        self.fields[1]['투수'] = away_pitcher
        self.fields[0]['투수'] = home_pitcher

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
        
        
    def convert_row_to_save_format(self, row,
                                   pa_result_details=None):
        # row: pandas Series
        bdf = self.batting_df
        pdf = self.pitching_df
        save_row = {k: None for k in header_row}
        save_row['pitcher'] = self.pitcher_name
        save_row['batter'] = self.batter_name
        save_row['pitcher_ID'] = self.pitcher_code
        save_row['batter_ID'] = self.batter_code
        save_row['balls'] = self.balls
        save_row['strikes'] = self.strikes
        save_row['outs'] = self.outs
        save_row['inning'] = self.inn
        save_row['inning_topbot'] = '초' if self.top_bot == 0 else '말'
        save_row['score_away'] = self.score[0]
        save_row['score_home'] = self.score[1]
        save_row['stands'] = bdf.loc[bdf.pCode == self.batter_code].hitType.values[0][2]
        save_row['throws'] = pdf.loc[pdf.pCode == self.pitcher_code].hitType.values[0][0]
        save_row['pa_number'] = self.pa_number

        save_row['game_date'] = self.game_date
        save_row['home'] = self.home
        save_row['away'] = self.away
        save_row['home_alias'] = self.home_alias
        save_row['away_alias'] = self.away_alias
        save_row['stadium'] = self.stadium
        save_row['referee'] = self.referee

        if self.bases[0] is not None:
            save_row['on_1b'] = bdf.loc[bdf.pCode == self.bases[0]].name.values[0]
        if self.bases[1] is not None:
            save_row['on_2b'] = bdf.loc[bdf.pCode == self.bases[1]].name.values[0]
        if self.bases[2] is not None:
            save_row['on_3b'] = bdf.loc[bdf.pCode == self.bases[2]].name.values[0]

        save_row['pos_1'] = self.fields[self.top_bot]['투수'].get('name')
        save_row['pos_2'] = self.fields[self.top_bot]['포수'].get('name')
        save_row['pos_3'] = self.fields[self.top_bot]['1루수'].get('name')
        save_row['pos_4'] = self.fields[self.top_bot]['2루수'].get('name')
        save_row['pos_5'] = self.fields[self.top_bot]['유격수'].get('name')
        save_row['pos_6'] = self.fields[self.top_bot]['3루수'].get('name')
        save_row['pos_7'] = self.fields[self.top_bot]['좌익수'].get('name')
        save_row['pos_8'] = self.fields[self.top_bot]['중견수'].get('name')
        save_row['pos_9'] = self.fields[self.top_bot]['우익수'].get('name')

        if row is not None:
            save_row['pitch_type'] = row.stuff
            save_row['speed'] = row.speed
            save_row['pitch_result'] = row.text.split(' ')[-1]
            save_row['pitch_number'] = self.pitch_number
            save_row['pitchID'] = row.pitchId
            if 'x0' in row.index:
                save_row['x0'] = row.x0
                save_row['z0'] = row.z0
                save_row['sz_top'] = row.topSz
                save_row['sz_bot'] = row.bottomSz
                px, pz, pfx_x, pfx_z, pfx_x_raw, pfx_z_raw = get_pitch_location_break(row)

                save_row['px'] = px
                save_row['pz'] = pz
                save_row['pfx_x'] = pfx_x
                save_row['pfx_z'] = pfx_z
                save_row['pfx_x_raw'] = pfx_x_raw
                save_row['pfx_z_raw'] = pfx_z_raw

                save_row['y0'] = 50
                save_row['vx0'] = row.vx0
                save_row['vy0'] = row.vy0
                save_row['vz0'] = row.vz0
                save_row['ax'] = row.ax
                save_row['ay'] = row.ay
                save_row['az'] = row.az

        if pa_result_details is not None:
            save_row['description'] = pa_result_details[0]
            save_row['pa_result'] = pa_result_details[1]
            save_row['pa_result_detail'] = pa_result_details[2]

        return save_row
 
    def handle_runner_stack(self, runner_stack):
        for i in range(len(runner_stack)):
            rrow = runner_stack[i]
            if (rrow.type == 13) | (rrow.type == 23):
                res = parse_batter_as_runner(rrow.text) # runner, result, before_base, after_base
                if res[1] == 'h':
                    self.score[self.top_bot] += 1
                elif res[1] == 'o':
                    self.outs += 1
                else:
                    self.after_bases[res[3]-1] = self.batter_code
                    self.base_change[res[3]-1] = True
                if self.DEBUG_MODE: print(f'\t\t{rrow.text}')
            else:
                res = parse_runner_result(rrow.text) # runner, result, before_base, after_base
                runner_code = self.bases[res[2]-1] if self.base_change[res[2]-1] is False else self.after_bases[res[2]-1]
                if ((self.base_change[res[2]-1] is True) & (self.after_bases[res[2]-1] == self.batter_code)) &\
                   ((self.bases[res[2]-1] is not None) & (self.bases[res[2]-1] != self.batter_code)):
                    runner_code = self.bases[res[2]-1]

                if res[1] == 'h':
                    self.score[self.top_bot] += 1
                elif res[1] == 'o':
                    self.outs += 1
                else:
                    self.after_bases[res[3]-1] = runner_code
                    self.base_change[res[3]-1] = True

                if self.base_change[res[2]-1] is False:
                    self.after_bases[res[2]-1] = None
                    self.base_change[res[2]-1] = True
                else:
                    if self.after_bases[res[2]-1] == runner_code:
                        self.after_bases[res[2]-1] = None

                if self.DEBUG_MODE: print(f'\t\t{rrow.text}')

        self.bases = self.after_bases
        self.after_bases = [None, None, None]
        self.base_change = [False, False, False]

 
    def handle_change(self, text_stack):
        change_stack = []
        bdf = self.batting_df
        pdf = self.pitching_df
        for i in range(len(text_stack)):
            text = text_stack[i]
            if self.DEBUG_MODE: print(f'\t{text}')
            order = None
            before_pos = text.split(' ')[0]

            if text.find('변경') > 0:
                after_pos = text.split('(')[0].strip().split(' ')[-1]
                shift_name = text.split(' ')[1].strip()

                for i in range(9):
                    if (self.lineups[1 - self.top_bot][i].get('name') == shift_name) &\
                       (self.lineups[1 - self.top_bot][i].get('pos') == before_pos):
                        shift_code = self.lineups[1 - self.top_bot][i].get('code')
                        order = i + 1
                        break
                if before_pos == '지명타자':
                    self.DH_exist_after[self.top_bot] = False
                if after_pos == '투수':
                    self.DH_exist_after[self.top_bot] = False
                change = [before_pos, after_pos, order, shift_name, shift_code]
                change_stack.append(change)
            else:
                after_pos = text.split('(')[0].strip().split(' ')[3]
                after_name = text.split('(')[0].strip().split(' ')[-1]
                before_name = text.split(' ')[1].strip()
                before_code = None
                homeaway = 'a' if self.top_bot == 0 else 'h'
                order = None

                if (before_pos == '지명타자') & (after_pos !='지명타자') & (after_pos !='대타'):
                    self.DH_exist_after[self.top_bot] = False
                elif (before_pos == '투수') & (after_pos != '투수'):
                    self.DH_exist_after[self.top_bot] = False
                elif (before_pos != '투수') & (after_pos == '투수'):
                    self.DH_exist_after[self.top_bot] = False

                if before_pos.find('번타자') > 0:
                    order = int(before_pos[0])
                    before_code = self.lineups[self.top_bot][order - 1].get('code')
                    seqno = int(bdf.loc[bdf.pCode == before_code].seqno)
                    after_code = int(bdf.loc[(bdf.homeaway == homeaway) &
                                             (bdf.batOrder == order) &
                                             (bdf.seqno > seqno)].head(1).pCode)
                elif after_pos == '투수':
                    homeaway = 'h' if self.top_bot == 0 else 'a'

                    # 예외처리
                    if (after_name == self.pitcher_name) & (before_pos != '투수'):
                        after_code = self.pitcher_code
                    elif (after_name != self.pitcher_name) & (before_pos != '투수'):
                        seqno = int(pdf.loc[pdf.pCode == self.pitcher_code].seqno)
                        after_code = int(pdf.loc[(pdf.homeaway == homeaway) &
                                                 (pdf.seqno > seqno)].head(1).pCode)
                    else:
                        before_code = self.fields[self.top_bot][before_pos].get('code')
                        seqno = int(pdf.loc[pdf.pCode == before_code].seqno)
                        after_code = int(pdf.loc[(pdf.homeaway == homeaway) &
                                                 (pdf.seqno > seqno)].head(1).pCode)
                    if (self.DH_exist[self.top_bot] is False) or (self.DH_exist_after[self.top_bot] != self.DH_exist[self.top_bot]):
                        for i in range(9):
                            if (self.lineups[1 - self.top_bot][i].get('name') == before_name) &\
                               (self.lineups[1 - self.top_bot][i].get('pos') == before_pos):
                                order = i + 1
                                break
                elif before_pos.find('루주자') > 0:
                    before_base = int(before_pos[0])
                    before_code = self.bases[before_base - 1]
                    order = int(bdf.loc[bdf.pCode == before_code].batOrder)
                    seqno = int(bdf.loc[bdf.pCode == before_code].seqno)
                    after_code = int(bdf.loc[(bdf.homeaway == homeaway) &
                                             (bdf.batOrder == order) &
                                             (bdf.seqno > seqno)].head(1).pCode)
                else:
                    for i in range(9):
                        if (self.lineups[1 - self.top_bot][i].get('name') == before_name) &\
                           (self.lineups[1 - self.top_bot][i].get('pos') == before_pos):
                            before_code = self.lineups[1 - self.top_bot][i].get('code')
                            order = i + 1
                            break
                    try:
                        seqno = int(bdf.loc[bdf.pCode == before_code].seqno.values[0])
                    except IndexError:
                        print(before_code)
                        print(text)
                        print(bdf.loc[bdf.pCode == before_code].seqno)
                        return False
                    homeaway = 'h' if self.top_bot == 0 else 'a'
                    after_code = int(bdf.loc[(bdf.homeaway == homeaway) &
                                             (bdf.batOrder == order) &
                                             (bdf.seqno > seqno)].head(1).pCode)
                change = [before_pos, after_pos, order, after_name, after_code]
                change_stack.append(change)

        for i in range(len(change_stack)):
            change = change_stack[i]
            before_pos, after_pos, order, after_name, after_code = change
            if (after_pos != '대타') & (after_pos != '대주자'):
                self.fields[self.top_bot][after_pos]['code'] = after_code
                self.fields[self.top_bot][after_pos]['name'] = after_name

            if order is not None:
                if (after_pos != '대타') & (after_pos != '대주자'):
                    tb = 1 - self.top_bot
                else:
                    tb = self.top_bot

                self.lineups[tb][order - 1]['code'] = after_code
                self.lineups[tb][order - 1]['name'] = after_name
                self.lineups[tb][order - 1]['pos'] = after_pos

            if after_pos == '투수':
                self.pitcher_code = after_code
                self.pitcher_name = after_name
            elif after_pos == '대주자':
                after_base = int(before_pos[0])
                self.bases[after_base - 1] = after_code
        self.DH_exist[self.top_bot] = self.DH_exist_after[self.top_bot]
   

    def parse_game(self):
        rdf = self.relay_df
        inns = range(1, rdf.inn.max()+1)
        for inn in inns:
            self.inn = inn
            for tb in ['t', 'b']:
                Inn = rdf.loc[(rdf.inn == inn) & (rdf.topbot == tb)]
                if Inn.size == 0:
                    break
                self.bases = [None, None, None]
                self.after_bases = [None, None, None]
                self.base_change = [False, False, False]
                self.balls, self.outs, self.strikes = 0, 0, 0
                self.DH_exist_after = self.DH_exist
                self.last_pitch = None

                tos = list(Inn.textOrder.unique())

                for to in tos:
                    PA = rdf.loc[rdf.textOrder == to]
                    if self.DEBUG_MODE: print(f'TO {to}')
                    lenPA = PA.shape[0]

                    ind = 0

                    while ind < lenPA:
                        row = PA.iloc[ind]

                        ##############################
                        ###### type에 따라 파싱 ######
                        ##############################

                        if (row.type == 1):
                            self.last_pitch = row
                            self.pitch_number += 1
                            res = row.text.split(' ')[-1]
                            self.pitch_result = res
                            # 인플레이/삼진/볼넷 이외에는 여기서 row print
                            # 몸에맞는공은 타석 결과에서 수정
                            if res != '타격':
                                save_row = self.convert_row_to_save_format(row)
                                self.print_rows.append(save_row)

                            if res == '볼':
                                self.balls += 1
                            elif res == '스트라이크':
                                self.strikes += 1
                            elif res == '헛스윙':
                                self.strikes += 1
                            elif res == '파울':
                                self.strikes = self.strikes+1 if self.strikes < 2 else 2
                            if self.DEBUG_MODE: print(f'\t{row.text}')
                            ind = ind + 1

                        elif (row.type == 8):
                            # 타석 시작(x번타자 / 대타)
                            position = row.text.split(' ')[0]
                            self.last_pitch = None
                            self.pa_result = None
                            self.pitch_result = None
                            self.pa_result_detail = None
                            self.description = ''
                            if len(position) > 2:
                                self.cur_order = int(position[0])
                                self.batter_name, self.batter_code, _pos = self.lineups[self.top_bot][self.cur_order - 1].values()
                                self.pitch_number = 0
                                self.pa_number += 1
                                self.balls, self.strikes = 0, 0
                            else:
                                self.batter_name, self.batter_code, _pos = self.lineups[self.top_bot][self.cur_order - 1].values()
                            if self.DEBUG_MODE: print(f'\t{row.text}')
                            ind = ind + 1
                        elif ((row.type == 13) | (row.type == 23)):
                            # 타자주자(비득점/득점)
                            runner_stack = []
                            cur_ind = ind
                            cur_row = PA.iloc[cur_ind]
                            self.description = ''
                            while ((cur_row.type == 13) | (cur_row.type == 23) | (cur_row.type == 14) | (cur_row.type == 24)):
                                runner_stack.append(cur_row)
                                self.description += cur_row.text.strip() + '; '
                                cur_ind = cur_ind + 1
                                if cur_ind >= lenPA:
                                    break
                                cur_row = PA.iloc[cur_ind]
                            self.description = self.description.strip()

                            result = parse_batter_result(row.text)
                            self.pa_result = result[0]
                            self.pa_result_detail = result[1]
                            if self.pitch_result != '타격':
                                self.print_rows[-1]['description'] = self.description
                                self.print_rows[-1]['pa_result'] = self.pa_result
                                self.print_rows[-1]['pa_result_detail'] = self.pa_result_detail
                            else:
                                save_row = self.convert_row_to_save_format(self.last_pitch,
                                                                           [self.description, self.pa_result, self.pa_result_detail])
                                self.print_rows.append(save_row)

                            ind = cur_ind
                            self.handle_runner_stack(runner_stack)
                        elif ((row.type == 14) | (row.type == 24)):
                            # 주자(비득점/득점)
                            runner_stack = []
                            cur_runner = None
                            cur_ind = ind
                            cur_row = PA.iloc[cur_ind]
                            self.description = ''
                            while ((cur_row.type == 14) | (cur_row.type == 24)):
                                runner_stack.append(cur_row)
                                self.description += cur_row.text.strip() + '; '
                                cur_ind = cur_ind + 1
                                if cur_ind >= lenPA:
                                    break
                                cur_row = PA.iloc[cur_ind]
                            self.description = self.description.strip()
                            save_row = self.convert_row_to_save_format(None,
                                                                       [self.description, None, None])
                            self.print_rows.append(save_row)
                            ind = cur_ind
                            self.handle_runner_stack(runner_stack)
                        elif (row.type == 0):
                            # 이닝 시작
                            if self.DEBUG_MODE: print(f'\t{row.text}')
                            ind = ind + 1
                            self.top_bot = (1 - self.top_bot)
                            self.pitcher_name, self.pitcher_code = self.fields[self.top_bot].get('투수').values()
                            self.pitch_number = 0
                        elif (row.type == 2):
                             # 교체/변경
                            text_stack = []
                            cur_ind = ind
                            cur_row = PA.iloc[cur_ind]
                            self.description = ''
                            while cur_row.type == 2:
                                text_stack.append(cur_row.text)
                                self.description += cur_row.text.strip() + '; '
                                cur_ind = cur_ind + 1
                                if cur_ind >= lenPA:
                                    break
                                cur_row = PA.iloc[cur_ind]
                            self.description = self.description.strip()
                            ind = cur_ind

                            save_row = self.convert_row_to_save_format(None,
                                                                       [self.description, None, None])
                            self.print_rows.append(save_row)

                            self.handle_change(text_stack)
                        elif (row.type == 7):
                            if self.DEBUG_MODE: print(f'\t{row.text}')
                            ind = ind + 1
                        else:
                            ind = ind + 1


    def save_game(self, path=None):
        row_df = pd.DataFrame(self.print_rows)
        enc = 'cp949' if sys.platform == 'win32' else 'utf-8'

        if path is None:
            year = int(self.game_date[:4])
            month = int(self.game_date[4:6])
            path = f'pbp_data/{year}/{month}'
        save_path = str(pathlib.Path(path) / f'{self.game_id}.csv')

        row_df.to_csv(save_path,
                      encoding=enc,
                      index=False)

