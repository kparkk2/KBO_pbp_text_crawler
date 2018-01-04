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

from matplotlib import font_manager, rc
import os
if os.name == 'posix':
    import matplotlib.font_manager as fm
    fm.get_fontconfig_fonts()
    font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
    font_name = fm.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)
else:
    rc('font', family='NanumSquare')


def check_condition( row, date_start, date_end,
                     inc_left=True, inc_right=True, stadium=None,
                     referee=None, bat_team=None, pit_team=None,
                     pitcherName=None, batterName=None,
                     inn=None, ballcount=None, stuff=None,
                     speed_low=0, speed_high=170, result=None,
                     px_low=-10, px_high=+10, pz_low=-10, pz_high=+10,
                     px_exclude=None, pz_exclude=None):
    if int(row['date']) < date_start:
        return False
    if int(row['date']) > date_end:
        return False
    if (row['stance'] =='L') and (inc_left is False):
        return False
    if (row['stance'] =='R') and (inc_right is False):
        return False
    if stadium is not None:
        if not (row['stadium'] == stadium):
            return False
    if referee is not None:
        if not (row['referee'] == referee):
            return False
    if bat_team is not None:
        if not (row['batter team'] == bat_team):
            return False
    if pit_team is not None:
        if not (row['pitcher team'] == pit_team):
            return False
    if pitcherName is not None:
        if not (row['pitcherName'] == pitcherName):
            return False
    if batterName is not None:
        if not (row['batterName'] == batterName):
            return False
    if inn is not None:
        if not (int(row['inn']) == inn):
            return False
    if stuff is not None:
        if not (row['stuff'] == stuff):
            return False
    if ballcount is not None:
        if not (int(row['ballcount']) == ballcount):
            return False
    if int(row['speed']) > speed_high:
        return False
    if int(row['speed']) < speed_low:
        return False
    if type(result) == list:
        if row['result'] not in result:
            return False
    if type(result) == str:
        if not row['result'] == result:
            return False
    if float(row['plateX']) < px_low:
        return False
    if float(row['plateX']) > px_high:
        return False
    if float(row['plateZ']) < pz_low:
        return False
    if float(row['plateZ']) > pz_high:
        return False
    if px_exclude is not None:
        if not ( (type(px_exclude) is list) or (type(px_exclude) is float) or (type(px_exclude) is int) ):
            return False
        if (type(px_exclude) is list) and (len(px_exclude) > 2):
            return False
        max_pxe = max(px_exclude)
        min_pxe = min(px_exclude)
        x = float(row['plateX'])
        if (min_pxe <= x) and (x <= max_pxe):
            return False
    if pz_exclude is not None:
        if not ( (type(pz_exclude) is list) or (type(pz_exclude) is float) or (type(pz_exclude) is int) ):
            return False
        if (type(pz_exclude) is list) and (len(pz_exclude) > 2):
            return False
        max_pze = max(pz_exclude)
        min_pze = min(pz_exclude)
        z = float(row['plateZ'])
        if (min_pze <= z) and (z <= max_pze):
            return False
    return True


from enum import Enum

Results = Enum('Results', '볼 스트라이크 헛스윙 파울 타격 번트파울 번트헛스윙')
Stuffs = Enum('Stuffs', '직구 슬라이더 포크 체인지업 커브 투심 싱커 커터 너클볼')
Colors = {1: '#3245ef', 2: '#ef2926', 3:'#1a1b1c', 4:'#edf72c', 5:'#8348d1', 6:'#edf72c', 7:'#1a1b1c' }

def get_results( data, date_start, date_end,
                inc_left=True, inc_right=True, stadium=None,
                referee=None, bat_team=None, pit_team=None,
                pitcherName=None, batterName=None,
                inn=None, ballcount=None, stuff=None,
                speed_low=0, speed_high=170, result=None,
                px_low=-10, px_high=+10, pz_low=-10, pz_high=+10,
                px_exclude=None, pz_exclude=None, light=False ):
    # pX, pZ, result, st, sb
    # inn, bc, stuff, speed, date
    values = None
    miscs = None
    for row in data:
        if not check_condition( row, date_start, date_end, inc_left, inc_right,
                                stadium, referee, bat_team, pit_team, pitcherName, batterName,
                                inn, ballcount, stuff, speed_low, speed_high, result,
                                px_low, px_high, pz_low, pz_high,
                                px_exclude, pz_exclude):
            continue
        else:
            px = float(row['plateX'])
            pz = float(row['plateZ'])
            r = Results[row['result']].value
            st = float(row['topSz'])
            sb = float(row['bottomSz'])
            xr = float(row['x0'])
            zr = float(row['z0'])
            
            if light is False:
                i = int(row['inn'])
                b = int(row['ballcount'])
                if row['stuff'] == '':
                    s = -1
                else:
                    s = Stuffs[row['stuff']].value
                v = int(row['speed'])
                d = int(row['date'])
                pfx = float(row['pfx_x'])
                pfz = float(row['pfx_z'])
            
            if values is None:
                values = np.asarray( [px, pz, r, st, sb, xr, zr] )
                if light is True:
                    miscs = None
                else:
                    miscs = np.asarray( [i, b, s, v, d, pfx, pfz] )
            else:
                values = np.vstack( (values, np.asarray( [px, pz, r, st, sb, xr, zr] )) )
                if light is True:
                    miscs = None
                else:
                    miscs = np.vstack( (miscs, np.asarray( [i, b, s, v, d, pfx, pfz] )) )
    return values, miscs


def plot_calls( values, miscs, title=None, specify_count=0, print_std=False, no_color=False, call_option=None, legends=False):
    # pX, pZ, result, st, sb
    # inn, bc, stuff, speed
    from matplotlib import font_manager, rc
    import os
    if os.name == 'posix':
        import matplotlib.font_manager as fm
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')

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
    
    if print_std is True:
        tb = +21/12
        bb = -21/12
        tl = +1.0
        bl = -1.0
        otl = +1.0+1/8
        obl = -1.0-1/8
        
    # strikes, balls
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
    
    if call_option is None:        
        svalues = values[np.where(values[:,2]==2)[0]]

        bvalues = values[np.where(values[:,2]==1)[0]]
        if print_std is True:
            for row in svalues:
                st = row[3]
                sb = row[4]
                row[1] = (row[1]-(st+sb)/2)/((st-sb)/2)
            for row in bvalues:
                st = row[3]
                sb = row[4]
                row[1] = (row[1]-(st+sb)/2)/((st-sb)/2)
        
        if specify_count <= 0:
            plt.scatter( svalues[:, 0], svalues[:, 1], color='#ef2926', alpha=.5, s=np.pi*50, label='스트라이크' )
            if no_color is True:
                plt.scatter( bvalues[:, 0], bvalues[:, 1], color='#ef2926', alpha=.5, s=np.pi*50 )
            else:
                plt.scatter( bvalues[:, 0], bvalues[:, 1], color='#3245ef', alpha=.5, s=np.pi*50, label='볼' )
        else:
            smiscs = miscs[np.where(values[:,2]==2)[0]]
            bmiscs = miscs[np.where(values[:,2]==1)[0]]
            plt.scatter( svalues[ np.where(smiscs[:, 1]==specify_count), 0 ], svalues[ np.where(smiscs[:, 1]==specify_count), 1 ], color='#ef2926', alpha=.5, s=np.pi*50, label='{}구'.format(specify_count) )
            plt.scatter( svalues[ np.where(smiscs[:, 1]!=specify_count), 0 ], svalues[ np.where(smiscs[:, 1]!=specify_count), 1 ], color='#3245ef', alpha=.5, s=np.pi*50 )

            for r, m in zip(svalues, smiscs):
                # pX, pZ, result, st, sb
                # inn, bc, stuff, speed
                if m[1] == specify_count:
                    if (lb < r[0]) and (r[0] < rb) and (bb < r[1]) and (r[1] < tb):
                        ax.text( r[0], r[1]-0.05, str(specify_count), color='white', fontsize=10, horizontalalignment='center')
            
            plt.scatter( bvalues[ np.where(bmiscs[:, 1]==specify_count), 0 ], bvalues[ np.where(bmiscs[:, 1]==specify_count), 1 ], color='#ef2926', alpha=.5, s=np.pi*50, label='{}구'.format(specify_count) )
            plt.scatter( bvalues[ np.where(bmiscs[:, 1]!=specify_count), 0 ], bvalues[ np.where(bmiscs[:, 1]!=specify_count), 1 ], color='#3245ef', alpha=.5, s=np.pi*50 )

            for r, m in zip(bvalues, bmiscs):
                # pX, pZ, result, st, sb
                # inn, bc, stuff, speed
                if m[1] == specify_count:
                    if (lb < r[0]) and (r[0] < rb) and (bb < r[1]) and (r[1] < tb):
                        ax.text( r[0], r[1]-0.05, str(int(r[4])), color='white', fontsize=10, horizontalalignment='center')
    else:
        if type(call_option) is list:
            tvalues = None
            tmiscs = None
            for co in call_option:
                c = Results[co].value
                if tvalues is None:
                    tvalues = values[np.where(values[:,2] == c)[0]]
                else:
                    tvalues = np.vstack( (tvalues, values[np.where(values[:,2] == c)[0]]) )
                if print_std is True:
                    for row in tvalues:
                        st = row[3]
                        sb = row[4]
                        row[1] = (row[1]-(st+sb)/2)/((st-sb)/2)
                
            if specify_count <= 0:
                for co in call_option:
                    c = Results[co].value
                    if no_color is True:
                        plt.scatter( tvalues[np.where(tvalues[:, 2]==c), 0], tvalues[np.where(tvalues[:, 2]==c), 1], color='#ef2926', alpha=.5, s=np.pi*50 )
                    else:
                        plt.scatter( tvalues[np.where(tvalues[:, 2]==c), 0], tvalues[np.where(tvalues[:, 2]==c), 1], color=Colors[c], alpha=.5, s=np.pi*50, label=co )
            else:
                tmiscs = None
                for co in call_option:
                    c = Results[co].value
                    if tmiscs is None:
                        tmiscs = miscs[np.where(values[:,2] == c)[0]]
                    else:
                        tmiscs = np.vstack( (tmiscs, miscs[np.where(values[:,2] == c)[0]]) )
                plt.scatter( tvalues[ np.where(tmiscs[:, 1]==specify_count), 0 ], tvalues[ np.where(tmiscs[:, 1]==specify_count), 1 ], color='#ef2926', alpha=.5, s=np.pi*50, label='{}구'.format(specify_count) )
                plt.scatter( tvalues[ np.where(tmiscs[:, 1]!=specify_count), 0 ], tvalues[ np.where(tmiscs[:, 1]!=specify_count), 1 ], color='#3245ef', alpha=.5, s=np.pi*50 )
                    
                for r, m in zip(tvalues, tmiscs):
                    # pX, pZ, result, st, sb
                    # inn, bc, stuff, speed
                    if m[1] == specify_count:
                        if (lb < r[0]) and (r[0] < rb) and (bb < r[1]) and (r[1] < tb):
                            ax.text( r[0], r[1]-0.05, str(specify_count), color='white', fontsize=10, horizontalalignment='center')
        elif type(call_option) is str:
            c = Results[call_option].value
            tvalues = values[np.where(values[:,2]==c)[0]]
            if print_std is True:
                for row in tvalues:
                    st = row[3]
                    sb = row[4]
                    row[1] = (row[1]-(st+sb)/2)/((st-sb)/2)

            if specify_count <= 0:
                if no_color is True:
                    plt.scatter( tvalues[:, 0], tvalues[:, 1], color='#ef2926', alpha=.5, s=np.pi*50, label=call_option )
                else:
                    plt.scatter( tvalues[:, 0], tvalues[:, 1], color=Colors[c], alpha=.5, s=np.pi*50, label=call_option )
            else:
                tmiscs = miscs[np.where(values[:,2]==c)[0]]
                plt.scatter( tvalues[ np.where(tmiscs[:, 1]==specify_count), 0 ], tvalues[ np.where(tmiscs[:, 1]==specify_count), 1 ], color='#ef2926', alpha=.5, s=np.pi*50, label='{}구'.format(specify_count) )
                plt.scatter( tvalues[ np.where(tmiscs[:, 1]!=specify_count), 0 ], tvalues[ np.where(tmiscs[:, 1]!=specify_count), 1 ], color='#3245ef', alpha=.5, s=np.pi*50 )
                
                for r, m in zip(tvalues, tmiscs):
                    # pX, pZ, result, st, sb
                    # inn, bc, stuff, speed
                    if m[1] == specify_count:
                        if (lb < r[0]) and (r[0] < rb) and (bb < r[1]) and (r[1] < tb):
                            ax.text( r[0], r[1]-0.05, str(specify_count), color='white', fontsize=10, horizontalalignment='center')
                    else:
                        plt.scatter( r[0], r[1], color='#3245ef', alpha=.5, s=np.pi*50 )
        else:
            print()
            print( 'ERROR: call option must be string/list' )
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
    
    if (legends is True) and (no_color is False):
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=2)

    plt.show()
    #return fig, ax


def get_heatmap( res, threshold=0.5, print_std=False ):
    # pX, pZ, result, stop, sbot
    x = np.arange(-1.5, +1.5, 1/12)
    if print_std is True:
        y = np.arange(-1.5, +1.5, 1/12)
    else:
        y = np.arange(+1.0, +4.0, 1/12)
    
    #strikes = list((row for row in values if row[2] == 2))
    #balls = list((row for row in values if row[2] == 1))
    
    rs = np.zeros( (res.shape[0], 2) )
    if print_std is True:
        rs[:, 0] = res[:, 0]
        rs[:, 1] = (res[:, 1] - (res[:, 3] + res[:, 4])/2) / ((res[:, 3] - res[:, 4])/2)
    
    P = np.zeros((36,36))
    S = np.zeros((36,36))
    for i in range(len(x)):
        for j in range(len(y)):
            s = 0
            b = 0
            if i == 0:
                if j == 0:
                    if print_std is True:
                        s = np.dot((res[:,2] == 2) & (rs[:,0] <= x[i]) & (rs[:,1] <= y[j]), np.ones(rs.shape[0]))
                        b = np.dot((res[:,2] == 1) & (rs[:,0] <= x[i]) & (rs[:,1] <= y[j]), np.ones(rs.shape[0]))
                    else:
                        s = np.dot((res[:,2] == 2) & (res[:,0] <= x[i]) & (res[:,1] <= y[j]), np.ones(res.shape[0]))
                        b = np.dot((res[:,2] == 1) & (res[:,0] <= x[i]) & (res[:,1] <= y[j]), np.ones(res.shape[0]))
                else:
                    if print_std is True:
                        s = np.dot((res[:,2] == 2) & (rs[:,0] <= x[i]) & (rs[:,1] <= y[j]) & (rs[:,1] > y[j-1]), np.ones(rs.shape[0]))
                        b = np.dot((res[:,2] == 1) & (rs[:,0] <= x[i]) & (rs[:,1] <= y[j]) & (rs[:,1] > y[j-1]), np.ones(rs.shape[0]))
                    else:
                        s = np.dot((res[:,2] == 2) & (res[:,0] <= x[i]) & (res[:,1] <= y[j]) & (res[:,1] > y[j-1]), np.ones(res.shape[0]))
                        b = np.dot((res[:,2] == 1) & (res[:,0] <= x[i]) & (res[:,1] <= y[j]) & (res[:,1] > y[j-1]), np.ones(res.shape[0]))
            else:
                if j == 0:
                    if print_std is True:
                        s = np.dot((res[:,2] == 2) & (rs[:,0] <= x[i]) & (rs[:,0] > x[i-1]) & (rs[:,1] <= y[j]), np.ones(rs.shape[0]))
                        b = np.dot((res[:,2] == 1) & (rs[:,0] <= x[i]) & (rs[:,0] > x[i-1]) & (rs[:,1] <= y[j]), np.ones(rs.shape[0]))
                    else:
                        s = np.dot((res[:,2] == 2) & (res[:,0] <= x[i]) & (res[:,0] > x[i-1]) & (res[:,1] <= y[j]), np.ones(res.shape[0]))
                        b = np.dot((res[:,2] == 1) & (res[:,0] <= x[i]) & (res[:,0] > x[i-1]) & (res[:,1] <= y[j]), np.ones(res.shape[0]))
                else:
                    if print_std is True:
                        s = np.dot((res[:,2] == 2) & (rs[:,0] <= x[i]) & (rs[:,0] > x[i-1]) & (rs[:,1] <= y[j]) & (rs[:,1] > y[j-1]), np.ones(rs.shape[0]))
                        b = np.dot((res[:,2] == 1) & (rs[:,0] <= x[i]) & (rs[:,0] > x[i-1]) & (rs[:,1] <= y[j]) & (rs[:,1] > y[j-1]), np.ones(rs.shape[0]))
                    else:
                        s = np.dot((res[:,2] == 2) & (res[:,0] <= x[i]) & (res[:,0] > x[i-1]) & (res[:,1] <= y[j]) & (res[:,1] > y[j-1]), np.ones(res.shape[0]))
                        b = np.dot((res[:,2] == 1) & (res[:,0] <= x[i]) & (res[:,0] > x[i-1]) & (res[:,1] <= y[j]) & (res[:,1] > y[j-1]), np.ones(res.shape[0]))
            if s+b > 0:
                P[i,j] = s/(s+b)
            else:
                P[i,j] = 0
    P = P.T
    S = (P >= threshold)
    return P, S


def fmt(x, pos):
    return r'{}%'.format(int(x*100))


def plot_heatmap( res, print_std=False, title=None ):
    # pX, pZ, result, stop, sbot
    # inn, bc, stuff, speed
    P, S = get_heatmap( res, print_std=print_std )
    
    lb = -1.5  # leftBorder
    rb = +1.5  # rightBorder
    
    x = np.arange(lb, rb, 1/12)
    
    if print_std is True:
        bb = -1.5  # bottomBorder
        tb = +1.5  # topBorder
        y = np.arange(bb, tb, 1/12)
    else:
        bb = +1.0  # bottomBorder
        tb = +4.0  # topBorder
        y = np.arange(+1.0, +4.0, 1/12)
    X, Y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(6,5), dpi=80, facecolor='white')
    
    from matplotlib import font_manager, rc
    import os
    if os.name == 'posix':
        import matplotlib.font_manager as fm
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')

    plt.rcParams['axes.unicode_minus'] = False
    #plt.pcolormesh(X, Y, P, cmap='gist_gray')
    plt.pcolormesh(X, Y, P)
    plt.colorbar(format=ticker.FuncFormatter(fmt))
    
    ll = -17/24
    rl = +17/24
    oll = -20/24
    orl = +20/24
    bl = 1.579
    tl = 3.325
    obl = 1.579-3/24
    otl = 3.325+3/24
    
    if print_std is True:
        bl = -1.0
        tl = +1.0
        obl = -1.0-3/24
        otl = +1.0+3/24
    
    plt.plot( [ll, ll], [bl, tl], color='#ffffff', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#ffffff', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#ffffff', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#ffffff', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#ffffff', linestyle= '-', lw=1 )
    plt.plot( [orl, orl], [obl, otl], color='#ffffff', linestyle= '-', lw=1 )

    plt.plot( [oll, orl], [obl, obl], color='#ffffff', linestyle= '-', lw=1 )
    plt.plot( [oll, orl], [otl, otl], color='#ffffff', linestyle= '-', lw=1 )

    if title is None:
        plt.title('2017 KBO S-Zone heatmap')
    else:
        plt.title(title)

    plt.axis( [lb+1/12, rb-1/12, bb+1/12, tb-1/12])

    
def plot_szone( res, threshold=0.5, print_std=False, title=None, show_area=False ):
    # pX, pZ, result, stop, sbot
    # inn, bc, stuff, speed
    P, S = get_heatmap( res, threshold=threshold, print_std=print_std )
    
    fig = plt.figure(figsize=(5,5), dpi=80, facecolor='white')
    ax = fig.add_subplot(111)
        
    lb = -1.5  # leftBorder
    rb = +1.5  # rightBorder
    
    x = np.arange(lb, rb, 1/12)
    
    if print_std is True:
        bb = -1.5  # bottomBorder
        tb = +1.5  # topBorder
        y = np.arange(bb, tb, 1/12)
    else:
        bb = +1.0  # bottomBorder
        tb = +4.0  # topBorder
        y = np.arange(+1.0, +4.0, 1/12)
    X, Y = np.meshgrid(x, y)
    
    plt.rcParams['axes.unicode_minus'] = False
    cmap = matplotlib.colors.ListedColormap(['white', '#ccffcc'])
    plt.pcolor(X, Y, S, cmap=cmap)
    ax.set_title('threshold: {}%'.format(round(threshold*100,1)))
    for i in range(len(x)):
        plt.axvline(x=float(x[i]), color='grey', linestyle='--', lw=0.2)

    for j in range(len(y)):
        plt.axhline(y=float(y[j]), color='grey', linestyle='--', lw=0.2)
        
    ll = -17/24
    rl = +17/24
    oll = -20/24
    orl = +20/24
    if print_std is True:
        bl = -1.0
        tl = +1.0
        obl = -1.0-3/24
        otl = +1.0+3/24
    else:
        bl = 1.579
        tl = 3.325
        obl = 1.579-3/24
        otl = 3.325+3/24
        
    plt.plot( [rl, rl], [bl, tl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [ll, ll], [bl, tl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [ll, rl], [bl, bl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [ll, rl], [tl, tl], color='dimgrey', linestyle= '-', lw=0.3 )
    
    plt.plot( [oll, oll], [obl, otl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [orl, orl], [obl, otl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [oll, orl], [obl, obl], color='dimgrey', linestyle= '-', lw=0.3 )
    plt.plot( [oll, orl], [otl, otl], color='dimgrey', linestyle= '-', lw=0.3 )

    plt.axis( [lb, rb, bb, tb])
    #fig.savefig('s-zone.png', facecolor='white')
    
    
    if title is None:
        ax.text( 0, tl+0.25, 'S-Zone size: {} sq.inch'.format(np.sum(S)), color='black', fontsize=10, horizontalalignment='center')
    else:
        ax.text( 0, tl+0.25, title, color='black', fontsize=10, horizontalalignment='center')
        
    area = np.sum(S)
    print('S-Zone size: {} sq.inch'.format(area))
    
    if show_area is True:
        ax.text( 0, (tl+bl)/2, '{} sq. inch'.format(str(area)), color='black', fontsize=12, horizontalalignment='center' )


def plot_contour_balls( res, title=None, print_std=False, vmin=None, vmax=None ):
    # pX, pZ, result, st, sb
    x = res[:,0]
    if print_std is False:
        y = res[:,1]
    else:
        y = (res[:,1]-(res[:,3]+res[:,4])/2)/(res[:,3]-res[:,4])

    lb = -2.0
    rb = +2.0
    ll = -17/24
    rl = +17/24
    oll = -20/24
    orl = +20/24
    
    if print_std is False:
        bb = 0.5
        tb = 4.5
        bl = 1.579
        tl = 3.325
        obl = 1.579-3/24
        otl = 3.325+3/24
    else:
        lb = -4.0
        rb = +4.0
        bb = -4.0
        tb = +4.0
        bl = -1.0
        tl = +1.0
        obl = -1.0-3/24
        otl = +1.0+3/24
        
    from scipy.stats.kde import gaussian_kde

    k = gaussian_kde(np.vstack([x, y]))
    
    #xi, yi = np.mgrid[x.min():x.max():x.size**0.5*1j,y.min():y.max():y.size**0.5*1j]
    xi, yi = np.mgrid[lb:rb:x.size**0.5*1j,bb:tb:y.size**0.5*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    fig = plt.figure(figsize=(4,3), dpi=160)
    ax1 = fig.add_subplot(111)

    if print_std is False:
        if vmin is not None:
            if vmax is not None:
                cs = ax1.contourf(xi, yi, zi.reshape(xi.shape), cmap='YlOrRd', vmin=vmin, vmax=vmax )
            else:
                cs = ax1.contourf(xi, yi, zi.reshape(xi.shape), cmap='YlOrRd', vmin=vmin )
        else:
            if vmax is not None:
                cs = ax1.contourf(xi, yi, zi.reshape(xi.shape), cmap='YlOrRd', vmax=vmax )
            else:
                cs = ax1.contourf(xi, yi, zi.reshape(xi.shape), cmap='YlOrRd' )
    else:
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list('mycmap', ['#ffffff', '#ffffff', '#fff3b8', '#ffe671', '#ffda2b',
                                                            '#fbb300', '#f26500', '#e91700', '#aa0000',
                                                            '#550000', '#000000'])
        cs = ax1.contourf(xi, yi, zi.reshape(xi.shape), cmap=cmap, interpolation='nearest' )
    
    cbar = plt.colorbar(cs, format=ticker.FuncFormatter(fmt))

    ax1.set_xlim(lb, rb)
    ax1.set_ylim(bb, tb)
    
    plt.plot( [ll, ll], [bl, tl], color='#2d2d2d', linestyle= '-', lw=1 )
    plt.plot( [rl, rl], [bl, tl], color='#2d2d2d', linestyle= '-', lw=1 )

    plt.plot( [ll, rl], [bl, bl], color='#2d2d2d', linestyle= '-', lw=1 )
    plt.plot( [ll, rl], [tl, tl], color='#2d2d2d', linestyle= '-', lw=1 )

    plt.plot( [oll, oll], [obl, otl], color='#000000', linestyle= '-', lw=0.5 )
    plt.plot( [orl, orl], [obl, otl], color='#000000', linestyle= '-', lw=0.5 )

    plt.plot( [oll, orl], [obl, obl], color='#000000', linestyle= '-', lw=0.5 )
    plt.plot( [oll, orl], [otl, otl], color='#000000', linestyle= '-', lw=0.5 )

    plt.axis( [lb, rb, bb, tb] )

    ax1.axis('off')
    ax1.set_yticklabels([])
    ax1.set_xticklabels([])
    ax1.autoscale_view('tight')
    fig.set_facecolor('white')

    if title is not None:
        st = fig.suptitle(title, fontsize=16)
        st.set_weight('bold')
        
    plt.show()

    
def plot_match_calls( values, title=None ):
    # pX, pZ, result, st, sb
    # inn, bc, stuff, speed
    from matplotlib import font_manager, rc
    import os
    if os.name == 'posix':
        import matplotlib.font_manager as fm
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')
        
    #Results = Enum('Results', '볼 스트라이크 헛스윙 파울 타격 번트파울 번트헛스윙')
    #Stuffs = Enum('Stuffs', '직구 슬라이더 포크 체인지업 커브 투심 싱커 커터 너클볼')

    bvalues = values[np.where(values[:,2]==1)]
    
    svalues = values[np.where(values[:,2]==2)]
    
    wvalues = values[ np.where(values[:,2]==3) or np.where(values[:,2]==7) ]
    
    fvalues = values[ np.where(values[:,2]==4) or np.where(values[:,2]==6) ]
    
    ivalues = values[np.where(values[:,2]==5)]
    
    # strikes, balls
    fig = plt.figure(figsize=(12,7), dpi=160, facecolor='#898f99')
    
    from matplotlib import font_manager, rc
    import os
    if os.name == 'posix':
        import matplotlib.font_manager as fm
        fm.get_fontconfig_fonts()
        font_location = '/Library/Fonts/NanumSquareOTFRegular.otf'
        font_name = fm.FontProperties(fname=font_location).get_name()
        rc('font', family=font_name)
    else:
        rc('font', family='NanumSquare')

    plt.rcParams['axes.unicode_minus'] = False
    ax = fig.add_subplot(231, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')
    
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
        
    for r in svalues:
        plt.scatter( r[0], r[1], color='#ef2926', alpha=.5, s=np.pi*50, label='스트라이크' )
    for r in bvalues:
        plt.scatter( r[0], r[1], color='#3245ef', alpha=.5, s=np.pi*50, label='볼' )
        
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
    ax.text('0', '3.8', '스트라이크+볼', color='white', fontsize=14, horizontalalignment='center', weight='bold')

    ############
    # strikes
    ############
    ax = fig.add_subplot(232, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    for r in svalues:
        plt.scatter( r[0], r[1], color='#ef2926', alpha=.5, s=np.pi*50, label='스트라이크' )

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
    ax.text('0', '3.8', '스트라이크', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    
    
    ############
    # balls
    ############
    ax = fig.add_subplot(233, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    for r in bvalues:
        plt.scatter( r[0], r[1], color='#3245ef', alpha=.5, s=np.pi*50, label='볼' )

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
    ax.text('0', '3.8', '볼', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')
    
    ############
    # whiffs
    ############
    ax = fig.add_subplot(2,3,4, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    for r in wvalues:
        plt.scatter( r[0], r[1], color='#1a1b1c', alpha=.5, s=np.pi*50, label='헛스윙' )

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
    ax.text('0', '3.8', '헛스윙', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')

    ############
    # fouls
    ############
    ax = fig.add_subplot(235, facecolor='#313133')
    ax.tick_params(axis='x', colors='white')

    for r in fvalues:
        plt.scatter( r[0], r[1], color='#edf72c', alpha=.5, s=np.pi*50, label='파울' )

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
    ax.text('0', '3.8', '파울', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')

    ############
    # inplays
    ############
    ax = fig.add_subplot(236, facecolor='#d19c49')
    ax.tick_params(axis='x', colors='white')

    for r in ivalues:
        plt.scatter( r[0], r[1], color='#8348d1', alpha=.5, s=np.pi*50, label='인플레이' )

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
    ax.text('0', '3.8', '인플레이', color='white', fontsize=14, horizontalalignment='center', weight='bold')
    ax.autoscale_view('tight')
    
    plt.show()


def get_pitch_info( data, name, stuff=None, date_start=160101, date_end=171231, inc_right=True, inc_left=True ):
    pfx_x = 0
    pfx_z = 0
    speed = 0
    count = 0
    total = 0
    pct = 0
    xrel = 0
    zrel = 0
    for row in data:
        if check_condition( row, pitcherName=name, stuff=stuff, date_start=date_start, date_end=date_end, inc_right=inc_right, inc_left=inc_left ):
            pfx_x += float(row['pfx_x'])
            pfx_z += float(row['pfx_z'])
            speed += float(row['speed'])
            count += 1
            xrel += float(row['x0'])
            zrel += float(row['z0'])
        if check_condition( row, pitcherName=name, stuff=None, date_start=date_start, date_end=date_end, inc_right=inc_right, inc_left=inc_left ):
            total += 1
    if count > 0:
        pfx_x = pfx_x/count*12
        pfx_z = pfx_z/count*12
        speed = speed/count
        xrel = xrel/count
        zrel = zrel/count
    if total > 0:
        pct = count/total
        
    return pfx_x, pfx_z, speed, count, pct, xrel, zrel


def show_pitcher_info( data, name, date_start=None, date_end=None, inc_right=True, inc_left=True ):
    p=name
    st = ['직구', '투심', '싱커', '슬라이더', '커터', '커브', '체인지업', '포크', '너클볼' ]
    if date_start is None:
        date_start = int('{}0301'.format(datetime.datetime.now().strftime('%y')))
    if date_end is None:
        date_end = int(datetime.datetime.now().strftime('%y%m%d'))

    print('{} 구종 정보'.format(p))
    for s in st:
        pfx_x, pfx_z, speed, count, pct, xrel, zrel = get_pitch_info(data, p, stuff=s, date_start=date_start, date_end=date_end, inc_right=inc_right, inc_left=inc_left)
        if pct >= 0.01:
            print( '{0:<8}'.format(s), end="" )
            print( 'speed: {0:.1f}'.format(speed), end="")
            print( '{0:>4}pct: {1:.1f}%'.format('',pct*100), end="")
            print( '{0:>4}h-mov: {1:.2f} in.'.format('', pfx_x), end="")
            print( '{0:>4}v-mov: {1:.2f} in.'.format('', pfx_z), end="")
            print( '{0:>4}x-rel: {1:.2f} ft.'.format('', xrel), end="")
            print( '{0:>4}z-rel: {1:.2f} ft.'.format('', zrel))