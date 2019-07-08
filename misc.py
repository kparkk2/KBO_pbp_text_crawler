# coding: utf-8

import numpy as np
import pandas as pd
import scipy as sp
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
from IPython.display import display, Audio
from pfx_plot import clean_data

import importlib
if importlib.util.find_spec('pygam') is not None:
    from pygam import LogisticGAM

def get_re24(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'outs', 'score_home', 'score_away', 'pitch_result', 'pa_result',
                      'on_1b', 'on_2b', 'on_3b']
    t = df.loc[df.outs<3][columns_needed]
    t = t.assign(play_run_home = t.score_home.shift(-1) - t.score_home,
                 play_run_away = t.score_away.shift(-1) - t.score_away)
    t.play_run_away = t.play_run_away.fillna(0)
    t.play_run_home = t.play_run_home.fillna(0)
    t = t.assign(play_run = np.where((t.inning_topbot == '말') &
                                     (t
                                      .pa_result != 'None'),
                                     t.play_run_home,
                                     np.where((t.inning_topbot == '초') & (t.pa_result != 'None'),
                                              t.play_run_away, 0)))
    t = t.assign(play_run = np.where(t.pa_result == '삼진', 0, t.play_run))
    t = t.assign(play_run = np.where(t.pa_result.isin(['볼넷', '자동 고의4구']),
                                     np.where((t.on_1b != 'None') &
                                              (t.on_2b != 'None') &
                                              (t.on_3b != 'None'), 1, 0),
                                     t.play_run))
    t.play_run = t.play_run.fillna(0)
    
    # RE24 계산을 위해 PA result 있는 데이터만 필터
    # 자동 고의4구도 포함 - 이때는 pitch result가 'None'임
    # PA result가 '투구 외 득점'일 때도 pitch result가 'None'인데 이것도 포함
    pa_res = t.loc[(t.pa_result != 'None')]
    
    # base 할당
    pa_res = pa_res.assign(base1 = np.where(pa_res.on_1b != 'None', '1', '_'),
                           base2 = np.where(pa_res.on_2b != 'None', '2', '_'),
                           base3 = np.where(pa_res.on_3b != 'None', '3', '_'))

    pa_res = pa_res.assign(base = pa_res.base1 + pa_res.base2 + pa_res.base3)
    
    ###############################
    # BASE-OUT 조합에 따른 타석의 숫자  #
    ###############################
    base_out_counts = pa_res.pivot_table('away',
                                         'base', 'outs', 'count', 0).sort_index(ascending=False)
    
    # 이닝 최대 점수
    rg = pa_res.groupby(['game_date', 'home', 'away',
                         'inning', 'inning_topbot'])['score_away', 'score_home']
    pa_res = pa_res.assign(max_score_in_inning = np.where(pa_res.inning_topbot == '초',
                                                          rg.transform(max).score_away,
                                                          rg.transform(max).score_home))

    # 해당 플레이 이후 그 이닝에서 발생하는 점수
    pa_res = pa_res.assign(runs_scored_after_play = np.where(pa_res.inning_topbot == '초',
                                                             pa_res.max_score_in_inning - pa_res.score_away,
                                                             pa_res.max_score_in_inning - pa_res.score_home))
    #####################################################
    # BASE-OUT 조합에 따른, 플레이 이후 그 이닝에 발생한 점수의 합  #
    #####################################################
    base_out_run_sum = pa_res.pivot_table('runs_scored_after_play',
                                          'base', 'outs', 'sum', 0).sort_index(ascending=False)
    
    # RE24 table
    re24 = base_out_run_sum / base_out_counts
    
    return re24.sort_values(0)


def get_rv_event(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'outs', 'score_home', 'score_away', 'pitch_result', 'pa_result',
                      'on_1b', 'on_2b', 'on_3b']
    t = df.loc[df.outs<3][columns_needed]
    t = t.assign(play_run_home = t.score_home.shift(-1) - t.score_home,
                 play_run_away = t.score_away.shift(-1) - t.score_away)
    t.play_run_away = t.play_run_away.fillna(0)
    t.play_run_home = t.play_run_home.fillna(0)
    t = t.assign(play_run = np.where((t.inning_topbot == '말') &
                                     (t.pa_result != 'None'),
                                     t.play_run_home,
                                     np.where((t.inning_topbot == '초') & (t.pa_result != 'None'),
                                              t.play_run_away, 0)))
    t = t.assign(play_run = np.where(t.pa_result == '삼진', 0, t.play_run))
    t = t.assign(play_run = np.where(t.pa_result.isin(['볼넷', '자동 고의4구']),
                                     np.where((t.on_1b != 'None') &
                                              (t.on_2b != 'None') &
                                              (t.on_3b != 'None'), 1, 0),
                                     t.play_run))
    t.play_run = t.play_run.fillna(0)
    
    # RE24 계산을 위해 PA result 있는 데이터만 필터
    # 자동 고의4구도 포함 - 이때는 pitch result가 'None'임
    # PA result가 '투구 외 득점'일 때도 pitch result가 'None'인데 이것도 포함
    pa_res = t.loc[(t.pa_result != 'None')]
    
    # base 할당
    pa_res = pa_res.assign(base1 = np.where(pa_res.on_1b != 'None', '1', '_'),
                           base2 = np.where(pa_res.on_2b != 'None', '2', '_'),
                           base3 = np.where(pa_res.on_3b != 'None', '3', '_'))

    pa_res = pa_res.assign(base = pa_res.base1 + pa_res.base2 + pa_res.base3)
    
    ###############################
    # BASE-OUT 조합에 따른 타석의 숫자  #
    ###############################
    base_out_counts = pa_res.pivot_table('away',
                                         'base', 'outs', 'count', 0).sort_index(ascending=False)
    
    # 이닝 최대 점수
    rg = pa_res.groupby(['game_date', 'home', 'away',
                         'inning', 'inning_topbot'])['score_away', 'score_home']
    pa_res = pa_res.assign(max_score_in_inning = np.where(pa_res.inning_topbot == '초',
                                                          rg.transform(max).score_away,
                                                          rg.transform(max).score_home))

    # 해당 플레이 이후 그 이닝에서 발생하는 점수
    pa_res = pa_res.assign(runs_scored_after_play = np.where(pa_res.inning_topbot == '초',
                                                             pa_res.max_score_in_inning - pa_res.score_away,
                                                             pa_res.max_score_in_inning - pa_res.score_home))
    #####################################################
    # BASE-OUT 조합에 따른, 플레이 이후 그 이닝에 발생한 점수의 합  #
    #####################################################
    base_out_run_sum = pa_res.pivot_table('runs_scored_after_play',
                                          'base', 'outs', 'sum', 0).sort_index(ascending=False)
    
    # RE24 table
    re24 = base_out_run_sum / base_out_counts
    
    base_out_re = re24.sort_index(axis=1, ascending=False).get_values().reshape(-1,1)
    
    ######################################
    # BASE-OUT 조합에 따른 각 타격 이벤트의 개수 #
    ######################################
    event_count_by_base_out = pa_res.pivot_table('runs_scored_after_play', ['base', 'outs'],
                                                 'pa_result', 'count', 0).sort_index(ascending=False)

    #########################################
    # BASE-OUT 조합에 따른 각 타석 이벤트의 RE sum #
    #########################################
    event_re_sum_by_base_out = event_count_by_base_out * np.repeat(base_out_re,
                                                                   event_count_by_base_out.shape[1],
                                                                   axis=1)

    #########################################
    # BASE-OUT 조합에 따른 각 타석 이벤트의 RE AVG #
    #########################################
    event_re_avg_by_base_out = event_re_sum_by_base_out.sum(axis=0) / event_count_by_base_out.sum(axis=0)
    
    ##############################################
    # 플레이(타석 이벤트) 이후 해당 이닝에 발생한 점수의 평균 #
    ##############################################
    runs_after_play_sum_by_event = pa_res.pivot_table('runs_scored_after_play',
                                                      'pa_result',
                                                      aggfunc='sum', fill_value=0)
    event_count = pa_res.pivot_table('runs_scored_after_play', 'pa_result', aggfunc='count', fill_value=0)
    runs_after_play_avg_by_event = (runs_after_play_sum_by_event / event_count).fillna(0)

    rv = runs_after_play_avg_by_event.runs_scored_after_play - event_re_avg_by_base_out
    
    rvdf = pd.DataFrame(rv)
    rvdf = rvdf.rename_axis('event')
    rvdf = rvdf.rename(index=str, columns={0:'Run Value'})

    return rvdf


def get_rv_event_simple(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'outs', 'score_home', 'score_away', 'pitch_result', 'pa_result',
                      'on_1b', 'on_2b', 'on_3b']
    single = ['내야안타', '1루타', '번트 안타']
    double = '2루타'
    triple = '3루타'
    homerun = '홈런'
    doubleplay = '병살타'
    ibb = '자동 고의4구'
    bb = '볼넷'
    so = '삼진'
    forceout = '포스 아웃'
    fieldout = ['필드 아웃', '타구맞음 아웃']
    sfly = '희생플라이'
    shhit = '희생번트'

    events_short = ['내야안타', '1루타', '번트 안타', '2루타', '3루타', '홈런', '병살타', '자동 고의4구', '고의4구',
                    '볼넷', '삼진', '포스 아웃', '필드 아웃', '타구맞음 아웃', '희생플라이', '희생번트']
    t = df[columns_needed]
    t = t.assign(play_run_home = t.score_home.shift(-1) - t.score_home,
                 play_run_away = t.score_away.shift(-1) - t.score_away)
    t.play_run_away = t.play_run_away.fillna(0)
    t.play_run_home = t.play_run_home.fillna(0)
    
    # 단타 종류는 모두 1루타로 축약
    t = t.assign(pa_result2 = np.where(t.pa_result.isin(single), '1루타',
                                       np.where(t.pa_result.isin(fieldout),
                                                '필드 아웃',
                                                t.pa_result)))
    
    t = t.assign(play_run = np.where((t.inning_topbot == '말') &
                                     (t.pa_result != 'None'),
                                     t.play_run_home,
                                     np.where((t.inning_topbot == '초') & (t.pa_result != 'None'),
                                              t.play_run_away, 0)))
    t = t.assign(play_run = np.where(t.pa_result == '삼진', 0, t.play_run))
    t = t.assign(play_run = np.where(t.pa_result.isin(['볼넷', '자동 고의4구', '고의4구']),
                                     np.where((t.on_1b != 'None') &
                                              (t.on_2b != 'None') &
                                              (t.on_3b != 'None'), 1, 0),
                                     t.play_run))
    t.play_run = t.play_run.fillna(0)
    
    # RE24 계산을 위해 PA result 있는 데이터만 필터
    # 자동 고의4구도 포함 - 이때는 pitch result가 'None'임
    # PA result가 '투구 외 득점'일 때도 pitch result가 'None'인데 이것도 포함
    pa_res = t.loc[(t.pa_result != 'None')]
    
    # simple 데이터로 필터
    pa_res = pa_res.loc[pa_res.pa_result.isin(events_short)]
    
    # 자동고의4구, 고의4구 하나로 합친다
    pa_res = pa_res.assign(pa_result = np.where(pa_res.pa_result == '자동 고의4구',
                                                '고의4구', pa_res.pa_result))
    
    # base 할당
    pa_res = pa_res.assign(base1 = np.where(pa_res.on_1b != 'None', '1', '_'),
                           base2 = np.where(pa_res.on_2b != 'None', '2', '_'),
                           base3 = np.where(pa_res.on_3b != 'None', '3', '_'))

    pa_res = pa_res.assign(base = pa_res.base1 + pa_res.base2 + pa_res.base3)

    ###############################
    # BASE-OUT 조합에 따른 타석의 숫자  #
    ###############################
    base_out_counts = pa_res.pivot_table('away',
                                         'base', 'outs', 'count', 0).sort_index(ascending=False)
    
    # 이닝 최대 점수
    rg = pa_res.groupby(['game_date', 'home', 'away',
                         'inning', 'inning_topbot'])['score_away', 'score_home']
    pa_res = pa_res.assign(max_score_in_inning = np.where(pa_res.inning_topbot == '초',
                                                          rg.transform(max).score_away,
                                                          rg.transform(max).score_home))

    # 해당 플레이 이후 그 이닝에서 발생하는 점수
    pa_res = pa_res.assign(runs_scored_after_play = np.where(pa_res.inning_topbot == '초',
                                                             pa_res.max_score_in_inning - pa_res.score_away,
                                                             pa_res.max_score_in_inning - pa_res.score_home))
    #####################################################
    # BASE-OUT 조합에 따른, 플레이 이후 그 이닝에 발생한 점수의 합  #
    #####################################################
    base_out_run_sum = pa_res.pivot_table('runs_scored_after_play',
                                          'base', 'outs', 'sum', 0).sort_index(ascending=False)
    
    # RE24 table
    re24 = base_out_run_sum / base_out_counts
    
    base_out_re = re24.sort_index(axis=1, ascending=False).get_values().reshape(-1,1)
    
    ######################################
    # BASE-OUT 조합에 따른 각 타격 이벤트의 개수 #
    ######################################
    event_count_by_base_out = pa_res.pivot_table('runs_scored_after_play', ['base', 'outs'],
                                                 'pa_result2', 'count', 0).sort_index(ascending=False)

    #########################################
    # BASE-OUT 조합에 따른 각 타석 이벤트의 RE sum #
    #########################################
    event_re_sum_by_base_out = event_count_by_base_out * np.repeat(base_out_re,
                                                                   event_count_by_base_out.shape[1],
                                                                   axis=1)

    #########################################
    # BASE-OUT 조합에 따른 각 타석 이벤트의 RE AVG #
    #########################################
    event_re_avg_by_base_out = event_re_sum_by_base_out.sum(axis=0) / event_count_by_base_out.sum(axis=0)
    
    ##############################################
    # 플레이(타석 이벤트) 이후 해당 이닝에 발생한 점수의 평균 #
    ##############################################
    runs_after_play_sum_by_event = pa_res.pivot_table('runs_scored_after_play',
                                                      'pa_result2',
                                                      aggfunc='sum', fill_value=0)
    event_count = pa_res.pivot_table('runs_scored_after_play', 'pa_result2', aggfunc='count', fill_value=0)
    runs_after_play_avg_by_event = (runs_after_play_sum_by_event / event_count).fillna(0)

    rv = runs_after_play_avg_by_event.runs_scored_after_play - event_re_avg_by_base_out
    
    rvdf = pd.DataFrame(rv)
    rvdf = rvdf.rename_axis('event')
    rvdf = rvdf.rename(index=str, columns={0:'Run Value'})
    
    return rvdf


def get_rv_of_ball_strike(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'pa_number', 'pa_result', 'pitch_result']
    t = df.loc[df.outs < 3][columns_needed]
    t = t.assign(pa_code = t.game_date.map(str)+
                           t.away.map(str)+
                           t.inning.map(str)+
                           t.inning_topbot.map(str)+
                           t.pa_number.map(str))
    pa_fin_res = t.loc[(t.pa_result != 'None') & (t.pa_result != '투구 외 득점')][['pa_code', 'pa_result']]
    
    t_join = t.set_index('pa_code').join(pa_fin_res.set_index('pa_code'), how='outer', rsuffix='_callee')
    t_join = t_join.drop(t_join.loc[t_join.pa_result_callee.isnull()].index)
    
    rv = get_rv_event(df)
    dict_rv = dict(rv['Run Value'])
    
    t_join = t_join.assign(rv = t_join.pa_result_callee.map(dict_rv))
    
    strikes = t_join.loc[t_join.pitch_result == '스트라이크']
    balls = t_join.loc[t_join.pitch_result == '볼']
    
    # event(when strike) rv sum
    event_rv_sum_when_strike = strikes.pivot_table('rv',
                                                   columns=['pa_result_callee'],
                                                   aggfunc='sum',
                                                   fill_value=0).sum(axis=1)
    
    # event(when ball) rv sum
    event_rv_sum_when_ball = balls.pivot_table('rv',
                                               columns=['pa_result_callee'],
                                               aggfunc='sum',
                                               fill_value=0).sum(axis=1)
    
    # event count(when strike)
    event_count_strike = strikes.pivot_table('rv',
                                             columns=['pa_result_callee'],
                                             aggfunc='count',
                                             fill_value=0).sum(axis=1)
    # event count(when ball)
    event_count_ball = balls.pivot_table('rv',
                                         columns=['pa_result_callee'],
                                         aggfunc='count',
                                         fill_value=0).sum(axis=1)
    
    return (event_rv_sum_when_ball / event_count_ball)[0], (event_rv_sum_when_strike / event_count_strike)[0]


def get_rv_of_ball_strike_by_count(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'pa_number', 'pa_result', 'pitch_result', 'balls', 'strikes']
    t = df.loc[df.outs < 3][columns_needed]
    t = t.assign(pa_code = t.game_date.map(str)+
                           t.away.map(str)+
                           t.inning.map(str)+
                           t.inning_topbot.map(str)+
                           t.pa_number.map(str))
    pa_fin_res = t.loc[(t.pa_result != 'None') & (t.pa_result != '투구 외 득점')][['pa_code', 'pa_result']]
    
    t_join = t.set_index('pa_code').join(pa_fin_res.set_index('pa_code'), how='outer', rsuffix='_callee')
    t_join = t_join.drop(t_join.loc[t_join.pa_result_callee.isnull()].index)
    
    rv = get_rv_event(df)
    dict_rv = dict(rv['Run Value'])
    
    t_join = t_join.assign(rv = t_join.pa_result_callee.map(dict_rv))
    
    strikes = t_join.loc[t_join.pitch_result == '스트라이크']
    balls = t_join.loc[t_join.pitch_result == '볼']
    
    # event(when strike) rv sum
    event_rv_sum_when_strike = strikes.pivot_table('rv',
                                                   ['strikes', 'balls'],
                                                   columns=['pa_result_callee'],
                                                   aggfunc='sum',
                                                   fill_value=0).sum(axis=1)
    
    # event(when ball) rv sum
    event_rv_sum_when_ball = balls.pivot_table('rv',
                                               ['strikes', 'balls'],
                                               columns=['pa_result_callee'],
                                               aggfunc='sum',
                                               fill_value=0).sum(axis=1)
    
    # event count(when strike)
    event_count_strike = strikes.pivot_table('rv',
                                             ['strikes', 'balls'],
                                             columns=['pa_result_callee'],
                                             aggfunc='count',
                                             fill_value=0).sum(axis=1)
    # event count(when ball)
    event_count_ball = balls.pivot_table('rv',
                                         ['strikes', 'balls'],
                                         columns=['pa_result_callee'],
                                         aggfunc='count',
                                         fill_value=0).sum(axis=1)
    
    return (event_rv_sum_when_ball / event_count_ball), (event_rv_sum_when_strike / event_count_strike)


def calc_framing_gam(df, rv_by_count=False):
    # 10-80% 구간 측정이 mean을 0에 가깝게 맞출 수 있음.
    sub_df = df.loc[df.pitch_result.isin(['스트라이크', '볼']) & (df.stands != 'None') & (df.throws != 'None')]
    sub_df = clean_data(sub_df)
    sub_df = sub_df.assign(stands = np.where(sub_df.stands == '양',
                                     np.where(sub_df.throws == '좌', '우', '좌'),
                                     sub_df.stands))
    sub_df = sub_df.assign(stands = np.where(sub_df.stands=='우', 0, 1)) # 우=0, 좌=1
    sub_df = sub_df.assign(throws = np.where(sub_df.throws=='우', 0, 1)) # 우=0, 좌=1
    sub_df.stadium = pd.Categorical(sub_df.stadium)
    sub_df = sub_df.assign(venue = sub_df.stadium.cat.codes)

    sub_df = sub_df.assign(pitch_result=np.where(sub_df.pitch_result=='스트라이크', 1, 0))

    features = ['px', 'pz', 'stands', 'throws', 'venue']
    label = ['pitch_result']

    x = sub_df[features]
    y = sub_df[label]

    gam = LogisticGAM().fit(x, y)
    predictions = gam.predict(x)
    proba = gam.predict_proba(x)

    logs = sub_df[features + label + ['pos_1', 'pos_2', 'balls', 'strikes', 'stadium']]
    logs = logs.rename(index=str, columns={'pos_1': 'pitcher', 'pos_2':'catcher'})

    logs = logs.assign(prediction = predictions)
    logs = logs.assign(proba = proba)
    
    # Run Value
    rv = None
    if rv_by_count is False:
        b, s = get_rv_of_ball_strike(df)
        rv = b - s
    else:
        b, s = get_rv_of_ball_strike_by_count(df)
        rv = b - s
    
    logs = logs.assign(excall=np.where(logs.prediction!=logs.pitch_result,
                                       np.where(logs.pitch_result==1, 1, -1),0))
    logs = logs.assign(exstr=np.where(logs.excall==1, 1, 0))
    logs = logs.assign(exball=np.where(logs.excall==-1, 1, 0))
    
    # Run Value
    if rv_by_count is False:
        logs = logs.assign(exrv = logs.excall * rv)
        logs = logs.assign(exrv_prob = np.where(logs.excall==1, (1-logs.proba)*rv,
                                                np.where(logs.excall==-1, -logs.proba*rv, 0)))
    else:
        logs = logs.assign(exrv = rv[logs.strikes*4 + logs.balls].get_values())
        logs = logs.assign(exrv = logs.excall * logs.exrv)
        logs = logs.assign(exrv_prob_plus = (1-logs.proba)*logs.exrv,
                           exrv_prob_minus = logs.proba*logs.exrv)
        logs = logs.assign(exrv_prob = np.where(logs.excall==1, logs.exrv_prob_plus,
                                                np.where(logs.excall==-1, logs.exrv_prob_minus, 0)))
        

    # 포수, catch 개수, extra strike, extra ball, RV sum
    tab = logs.pivot_table(index='catcher',
                           values=['exstr', 'exball', 'excall', 'exrv', 'exrv_prob', 'px'],
                           aggfunc={'exstr': 'sum',
                                    'exball': 'sum',
                                    'excall': 'sum',
                                    'exrv': 'sum',
                                    'exrv_prob':'sum',
                                    'px':'count'})
    tab = tab.rename(index=str, columns={'px': 'num'}).sort_values('num', ascending=False)
    
    return logs, tab[['num', 'excall', 'exstr', 'exball', 'exrv', 'exrv_prob']].sort_values('excall', ascending=False)

    
def calc_framing_cell(df, rv_by_count=False):
    # 20-80% 구간 측정이 mean을 0에 가깝게 맞출 수 있음.
    features = ['px', 'pz', 'pitch_result', 'stands', 'throws', 'pitcher', 'catcher',
                'stadium', 'referee', 'balls', 'strikes']

    sub_df = df.loc[df.pitch_result.isin(['스트라이크', '볼']) & (df.stands != 'None') & (df.throws != 'None')]
    sub_df = clean_data(sub_df)
    sub_df = sub_df.assign(stands = np.where(sub_df.stands == '양',
                                     np.where(sub_df.throws == '좌', '우', '좌'),
                                     sub_df.stands))
    sub_df = sub_df.rename(index=str, columns={'pos_1': 'pitcher', 'pos_2':'catcher'})
    logs = sub_df[features]

    logs = logs.assign(pitch_result=np.where(logs.pitch_result=='스트라이크', 1, 0))
    strikes = logs.loc[logs.pitch_result == 1]
    balls = logs.loc[logs.pitch_result == 0]

    lb = -1.5
    rb = +1.5
    bb = 1.0
    tb = 4.0

    bins = 36

    c1, x, y, i = plt.hist2d(strikes.px, strikes.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    c2, x, y, i = plt.hist2d(balls.px, balls.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    plt.close()

    np.seterr(divide='ignore', invalid='ignore')
    r = np.nan_to_num(c1 / (c1+c2))
    np.seterr(divide=None, invalid=None)
    probs = gaussian_filter(r, sigma=1.5, truncate=1, mode='constant')

    logs = logs.assign(x_ind = ((logs.px+1.5)*12).astype(np.int8))
    logs = logs.assign(y_ind = ((logs.pz-1)*12).astype(np.int8))
    logs = logs.assign(proba = -1)
    for i in range(0, bins):
        for j in range(0, bins):
            logs = logs.assign(proba = np.where((logs.x_ind == i) & (logs.y_ind == j),
                                                probs[i][j], logs.proba))

    logs = logs.drop(columns='x_ind')
    logs = logs.drop(columns='y_ind')
    logs = logs.assign(prediction = np.where(logs.proba >=0.5, 1, 0))
    
    # Run Value
    rv = None
    if rv_by_count is False:
        b, s = get_rv_of_ball_strike(df)
        rv = b - s
    else:
        b, s = get_rv_of_ball_strike_by_count(df)
        rv = b - s

    logs = logs.assign(excall=np.where(logs.prediction!=logs.pitch_result,
                                       np.where(logs.pitch_result==1, 1, -1),0))
    logs = logs.assign(exstr=np.where(logs.excall==1, 1, 0))
    logs = logs.assign(exball=np.where(logs.excall==-1, 1, 0))
    
    # Run Value
    if rv_by_count is False:
        logs = logs.assign(exrv = logs.excall * rv)
        logs = logs.assign(exrv_prob = np.where(logs.excall==1, (1-logs.proba)*rv,
                                                np.where(logs.excall==-1, -logs.proba*rv, 0)))
    else:
        logs = logs.assign(exrv = rv[logs.strikes*4 + logs.balls].get_values())
        logs = logs.assign(exrv = logs.excall * logs.exrv)
        logs = logs.assign(exrv_prob_plus = (1-logs.proba)*logs.exrv,
                           exrv_prob_minus = logs.proba*logs.exrv)
        logs = logs.assign(exrv_prob = np.where(logs.excall==1, logs.exrv_prob_plus,
                                                np.where(logs.excall==-1, logs.exrv_prob_minus, 0)))


    # 포수, catch 개수, extra strike, extra ball, RV sum
    tab = logs.pivot_table(index='catcher',
                           values=['exstr', 'exball', 'excall', 'exrv', 'exrv_prob', 'px'],
                           aggfunc={'exstr': 'sum',
                                    'exball': 'sum',
                                    'excall': 'sum',
                                    'exrv': 'sum',
                                    'exrv_prob':'sum',
                                    'px':'count'})
    tab = tab.rename(index=str, columns={'px': 'num'}).sort_values('num', ascending=False)
    
    return logs, tab[['num', 'excall', 'exstr', 'exball', 'exrv', 'exrv_prob']].sort_values('excall', ascending=False)


def calc_framing_gam_adv(df, rv_by_count=False, max_dist=0.25):
    lb = -1.5
    rb = +1.5
    bb = 1.0
    tb = 4.0

    sub_df = clean_data(df)
    strikes = sub_df.loc[sub_df.pitch_result == '스트라이크']
    balls = sub_df.loc[sub_df.pitch_result == '볼']

    bins = 36

    c1, x, y, _ = plt.hist2d(strikes.px, strikes.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    c2, x, y, _ = plt.hist2d(balls.px, balls.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    plt.close()

    np.seterr(divide='ignore', invalid='ignore')
    r = np.nan_to_num(c1 / (c1+c2))
    np.seterr(divide=None, invalid=None)
    rg = gaussian_filter(r, sigma=1.5, truncate=1, mode='constant')

    x, y = np.mgrid[lb:rb:bins*1j, bb:tb:bins*1j]

    CS = plt.contour(x, y, rg, levels=np.asarray([.5]), linewidths=2, zorder=1)
    path = CS.collections[0].get_paths()[0]
    cts = path.vertices
    d = sp.spatial.distance.cdist(cts, cts)
    plt.close()
    
    logs, _ = calc_framing_gam(sub_df, rv_by_count)
    logs = logs.assign(dist = np.min(sp.spatial.distance.cdist(logs[['px', 'pz']], cts), axis=1))

    tab = logs.loc[logs.dist < max_dist].pivot_table(index='catcher',
                           values=['exstr', 'exball', 'excall', 'exrv', 'exrv_prob', 'px'],
                           aggfunc={'exstr': 'sum', 'exball': 'sum', 'excall': 'sum', 'exrv': 'sum', 'exrv_prob':'sum', 'px':'count'})
    tab = tab.rename(index=str, columns={'px': 'num'}).sort_values('num', ascending=False)
    
    return logs.loc[logs.dist < max_dist], tab[['num', 'excall', 'exstr', 'exball', 'exrv', 'exrv_prob']].sort_values('excall', ascending=False)


def calc_framing_cell_adv(df, rv_by_count=False, max_dist=0.25):
    lb = -1.5
    rb = +1.5
    bb = 1.0
    tb = 4.0

    sub_df = clean_data(df)
    strikes = sub_df.loc[sub_df.pitch_result == '스트라이크']
    balls = sub_df.loc[sub_df.pitch_result == '볼']

    bins = 36

    c1, x, y, _ = plt.hist2d(strikes.px, strikes.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    c2, x, y, _ = plt.hist2d(balls.px, balls.pz, range=[[lb, rb], [bb, tb]], bins=bins)
    plt.close()

    np.seterr(divide='ignore', invalid='ignore')
    r = np.nan_to_num(c1 / (c1+c2))
    np.seterr(divide=None, invalid=None)
    rg = gaussian_filter(r, sigma=1.5, truncate=1, mode='constant')

    x, y = np.mgrid[lb:rb:bins*1j, bb:tb:bins*1j]

    CS = plt.contour(x, y, rg, levels=np.asarray([.5]), linewidths=2, zorder=1)
    path = CS.collections[0].get_paths()[0]
    cts = path.vertices
    d = sp.spatial.distance.cdist(cts, cts)
    plt.close()
    
    logs, _ = calc_framing_cell(sub_df, rv_by_count)
    logs = logs.assign(dist = np.min(sp.spatial.distance.cdist(logs[['px', 'pz']], cts), axis=1))

    tab = logs.loc[logs.dist < max_dist].pivot_table(index='catcher',
                           values=['exstr', 'exball', 'excall', 'exrv', 'exrv_prob', 'px'],
                           aggfunc={'exstr': 'sum', 'exball': 'sum', 'excall': 'sum', 'exrv': 'sum', 'exrv_prob':'sum', 'px':'count'})
    tab = tab.rename(index=str, columns={'px': 'num'}).sort_values('num', ascending=False)
    
    return logs.loc[logs.dist < max_dist], tab[['num', 'excall', 'exstr', 'exball', 'exrv', 'exrv_prob']].sort_values('excall', ascending=False)


def soundAlert1():
    display(Audio(url='https://sound.peal.io/ps/audios/000/000/537/original/woo_vu_luvub_dub_dub.wav', autoplay=True))


def soundAlert2():
    display(Audio(url='https://sound.peal.io/ps/audios/000/000/430/original/liljon_3.mp3', autoplay=True))
