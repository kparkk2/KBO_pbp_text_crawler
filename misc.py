# coding: utf-8

import numpy as np
import pandas as pd

def get_re24(df):
    columns_needed = ['game_date', 'away', 'home', 'inning', 'inning_topbot',
                      'outs', 'score_home', 'score_away', 'pitch_result', 'pa_result',
                      'on_1b', 'on_2b', 'on_3b']
    t = df[columns_needed]
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
    t = df[columns_needed]
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
    t = df[columns_needed]
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
    t = df[columns_needed]
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

