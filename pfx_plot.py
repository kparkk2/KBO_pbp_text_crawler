# coding: utf-8

import csv
import json
import collections
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import numpy.random
import matplotlib.ticker as ticker
import datetime
from matplotlib import font_manager as fm, rc
import os
from enum import Enum

Results = Enum('Results', '볼 스트라이크 헛스윙 파울 타격 번트파울 번트헛스윙')
Stuffs = Enum('Stuffs', '직구 슬라이더 포크 체인지업 커브 투심 싱커 커터 너클볼')
Colors = {'볼': '#3245ef', '스트라이크': '#ef2926', '헛스윙':'#1a1b1c', '파울':'#edf72c', '타격':'#8348d1', '번트파울':'#edf72c', '번트헛스윙':'#1a1b1c' }

def plot_calls(df, title=None, print_std=False, calls=None, legends=True, show_pitch_number=False):
    if os.name == 'posix':
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')

    # 단위: 피트; 좌우폭=17인치=17/24피트, 공1개 지름=약 3인치=1/4피트; 공반개=1/8피트
    lb = -1.5  # leftBorder
    rb = +1.5  # rightBorder
    tb = +4.0  # topBorder
    bb = +1.0  # bottomBorder
    
    ll = -17/24  # leftLine
    rl = +17/24  # rightLine
    tl = +3.325  # topLine
    bl = +1.579  # bototmLine
    
    oll = -17/24-1/8  # outerLeftLine
    orl = +17/24+1/8  # outerRightLine
    otl = +3.325+1/8  # outerTopLine
    obl = +1.579-1/8  # outerBottomLine
    
    # 타자 상하 존 경계에 맞춰 표준화하는 경우 -> 추후 구현
    if print_std is True:
        lb = -1.5  # leftBorder
        rb = +1.5  # rightBorder
        tb = +4.0  # topBorder
        bb = +1.0  # bottomBorder
        '''
        tb = +21/12
        bb = -21/12
        tl = +1.0
        bl = -1.0
        otl = +1.0+1/8
        obl = -1.0-1/8
        '''
        
    # 스트라이크, 볼만 표기 -> 서브플롯 1개
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(4, 4)
    fig.set_dpi(80)
    fig.set_facecolor('#898f99')
    
    ax.set_facecolor('#898f99')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='x', colors='white')
    
    if title is not None:
        st = fig.suptitle(title, fontsize=20)
        st.set_color('white')
        st.set_weight('bold')
        st.set_horizontalalignment('center')
    
    if calls is None:
        plt.scatter(df.px, df.pz, color='#ef2926', alpha=.5, s=np.pi*50, label=df.pitch_result)
        
        if show_pitch_number is True:
            for i in df.index:
                ax.text(df.loc[i].px, df.loc[i].pz-0.05, df.loc[i].pitch_number,
                        color='white', fontsize=10, horizontalalignment='center')
        '''
        strikes = df.loc[df.pitch_result == '스트라이크']
        balls = df.loc[df.pitch_result == '볼']
        
        plt.scatter(strikes.px, strikes.pz, color='#ef2926', alpha=.5, s=np.pi*50, label=df.pitch_result)
        plt.scatter(balls.px, balls.pz, color='#3245ef', alpha=.5, s=np.pi*50, label='볼')

        if show_pitch_number is True:
            for i in strikes.index:
                ax.text(strikes.loc[i].px, strikes.loc[i].pz-0.05, strikes.loc[i].pitch_number,
                        color='white', fontsize=10, horizontalalignment='center')
            for i in balls.index:
                ax.text(balls.loc[i].px, balls.loc[i].pz-0.05, balls.loc[i].pitch_number,
                        color='white', fontsize=10, horizontalalignment='center')
        '''
    else:
        if type(calls) is list:
            for call in calls:
                filtered = df.loc[df.pitch_result == call]
                color = Colors[call]
                
                plt.scatter(filtered.px, filtered.pz, color=color, alpha=.5, s=np.pi*50, label=call)
                
                if show_pitch_number is True:
                    for i in filtered.index:
                        ax.text(filtered.loc[i].px, filtered.loc[i].pz-0.05, filtered.loc[i].pitch_number,
                                color='white', fontsize=10, horizontalalignment='center')
        elif type(calls) is str:
            filtered = df.loc[df.pitch_result == calls]
            color = Colors[calls]
            
            plt.scatter(filtered.px, filtered.pz, color=color, alpha=.5, s=np.pi*50, label=calls)            
            
            if show_pitch_number is True:
                for i in filtered.index:
                    ax.text(filtered.loc[i].px, filtered.loc[i].pz-0.05, filtered.loc[i].pitch_number,
                            color='white', fontsize=10, horizontalalignment='center')
        else:
            print()
            print( 'ERROR: call option must be either string or list' )
            exit(1)

    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    x = np.arange(lb, rb, 1/12)
    y = np.arange(bb, tb, 1/12)
    X, Y = np.meshgrid(x, y)

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.autoscale_view('tight')

    if legends is True:
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=2)
        
    plt.show()
    #return fig, ax
    
    
# 경기 전체 call
def plot_match_calls( df, title=None ):
    if os.name == 'posix':
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')
    fig = plt.figure(figsize=(12,7), dpi=160, facecolor='#898f99')

    plt.rcParams['axes.unicode_minus'] = False
        
    lb = -1.5  # leftBorder
    rb = +1.5  # rightBorder
    tb = +4.0  # topBorder
    bb = +1.0  # bottomBorder
    
    ll = -17/24  # leftLine
    rl = +17/24  # rightLine
    tl = +3.325  # topLine
    bl = +1.579  # bototmLine
    
    oll = -17/24-1/8  # outerLeftLine
    orl = +17/24+1/8  # outerRightLine
    otl = +3.325+1/8  # outerTopLine
    obl = +1.579-1/8  # outerBottomLine
    
    if title is not None:
        st = fig.suptitle(title, fontsize=20)
        st.set_color('white')
        st.set_weight('bold')
        st.set_horizontalalignment('center')

    # NaN, None 값들을 제거
    sub_df = df
    if df.px.isnull().any():
        sub_df = df.drop(df.loc[df.px.isnull()].index)
    
    strikes = sub_df.loc[sub_df.pitch_result == '스트라이크']
    balls = sub_df.loc[sub_df.pitch_result == '볼']
    whiffs = sub_df.loc[(sub_df.pitch_result == '헛스윙') | (sub_df.pitch_result == '번트헛스윙')]
    fouls = sub_df.loc[(sub_df.pitch_result == '파울') | (sub_df.pitch_result == '번트파울')]
    inplays = sub_df.loc[sub_df.pitch_result == '타격']
    
    ############
    # 1/6 : 스트라이크+볼
    ############
    ax = fig.add_subplot(231, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')
    
    plt.scatter(strikes.px, strikes.pz, color='#ef2926', alpha=.5, s=np.pi*50, label='스트라이크')
    plt.scatter(balls.px, balls.pz, color='#3245ef', alpha=.5, s=np.pi*50, label='볼')
    
    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.autoscale_view('tight')
    ax.text(0, 3.8, '스트라이크+볼', color='white', fontsize=14, horizontalalignment='center', weight='bold')

    ############
    # 2/6 : 스트라이크
    ############
    ax = fig.add_subplot(232, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    plt.scatter(strikes.px, strikes.pz, color='#ef2926', alpha=.5, s=np.pi*50, label='스트라이크')
    
    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.autoscale_view('tight')
    ax.text(0, 3.8, '스트라이크', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    
    ############
    # 3/6 : 볼
    ############
    ax = fig.add_subplot(233, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    plt.scatter(balls.px, balls.pz, color='#3245ef', alpha=.5, s=np.pi*50, label='볼')

    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )
    
    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.text(0, 3.8, '볼', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')
    
    ############
    # 4/6 : 헛스윙
    ############
    ax = fig.add_subplot(2,3,4, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    plt.scatter(whiffs.px, whiffs.pz, color='#1a1b1c', alpha=.5, s=np.pi*50, label='헛스윙')

    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.text(0, 3.8, '헛스윙', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')

    ############
    # 5/6 : 파울
    ############
    ax = fig.add_subplot(235, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    plt.scatter(fouls.px, fouls.pz, color='#edf72c', alpha=.5, s=np.pi*50, label='파울')

    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.text(0, 3.8, '파울', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')

    ############
    # 6/6 : 인플레이(타격)
    ############
    ax = fig.add_subplot(236, facecolor='#d19c49')
    ax.tick_params(axis='x', colors='white')

    plt.scatter(inplays.px, inplays.pz, color='#8348d1', alpha=.5, s=np.pi*50, label='인플레이')

    plt.plot( [ll, ll], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color='#f9f9ff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#f9f9ff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#d0cfd3', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#d0cfd3', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.axis('off')
    ax.text(0, 3.8, '인플레이', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')
    
    plt.show()