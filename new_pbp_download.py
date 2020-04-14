import pandas as pd
import time, requests, json, datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm, trange
from bs4 import BeautifulSoup

from new_pbp_parse import game_status

def get_game_ids(start_date, end_date):
    timetable_url = 'https://sports.news.naver.com/'\
                    'kbaseball/schedule/index.nhn?month='
    
    mon1 = start_date.replace(day=1)
    r = []
    while mon1 <= end_date:
        r.append(mon1)
        mon1 += relativedelta(months=1)
    
    game_ids = []
    
    for d in r:
        month = d.month
        year = d.year
        
        sch_url = timetable_url + f'{month}&year={year}'

        response = requests.get(sch_url)
        soup = BeautifulSoup(response.text, 'lxml')
        response.close()

        buttons = soup.findAll('span',
                               attrs={'class': 'td_btn'})

        for btn in buttons:
            gid = btn.a['href'].split('gameId=')[1]
            gid_date = datetime.date(int(gid[:4]),
                                     int(gid[4:6]),
                                     int(gid[6:8]))
            if start_date <= gid_date <= end_date:
                game_ids.append(gid)
    return game_ids


def get_game_data(game_id):
    relay_url = 'http://m.sports.naver.com/ajax/baseball/'\
            'gamecenter/kbo/relayText.nhn'
    record_url = 'http://m.sports.naver.com/ajax/baseball/'\
                'gamecenter/kbo/record.nhn'
    params = {'gameId': game_id, 'half': '1'}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'm.sports.naver.com',
        'Referer': 'http://m.sports.naver.com/baseball'\
                   '/gamecenter/kbo/index.nhn?&gameId='
                   + game_id
                   + '&tab=relay'
    }
    
    #####################################
    # 1. pitch by pitch 데이터 가져오기 #
    #####################################
    relay_response = requests.get(relay_url,
                                  params=params,
                                  headers=headers)
    if relay_response is None:
        relay_response.close()
        return None
    
    js = relay_response.json()
    if isinstance(js, str):
        js = json.loads(js)
    else:
        relay_response.close()
        return None
    relay_response.close()
    last_inning = js['currentInning']

    if last_inning is None:
        return None

    game_data_set = {}
    game_data_set['relayList'] = []
    for x in js['relayList']:
        game_data_set['relayList'].append(x)

    # 라인업에 대한 기초 정보가 담겨 있음
    game_data_set['homeTeamLineUp'] = js['homeTeamLineUp']
    game_data_set['awayTeamLineUp'] = js['awayTeamLineUp']

    game_data_set['stadium'] = js['schedule']['stadium']
    
    for inn in range(2, last_inning + 1):
        params = {
            'gameId': game_id,
            'half': str(inn)
        }

        relay_inn_response = requests.get(relay_url, params=params, headers=headers)
        if relay_inn_response is not None:
            js = relay_inn_response.json()
            if isinstance(js, str):
                js = json.loads(js)
            else:
                relay_inn_response.close()
                return None
            relay_inn_response.close()

            for x in js['relayList']:
                game_data_set['relayList'].append(x)
        else:
            relay_inn_response.close()
            return None

    #########################
    # 2. 가져온 정보 다듬기 #
    #########################
    relay_list = game_data_set['relayList']
    text_keys = ['seqno', 'text', 'type', 'stuff',
                 'ptsPitchId', 'speed', 'playerChange']
    pitch_keys = ['crossPlateX', 'topSz',
                  'pitchId', 'vy0', 'vz0', 'vx0',
                  'z0', 'ax', 'x0', 'ay', 'az',
                  'bottomSz']

    # pitch by pitch 텍스트 데이터 취합
    text_set = []
    stadium = game_data_set['stadium']
    for k in range(len(relay_list)):
        for j in range(len(relay_list[k].get('textOptionList'))):
            text_row = relay_list[k].get('textOptionList')[j]

            text_row_dict = {}
            text_row_dict['textOrder'] = relay_list[k].get('no')
            for key in text_keys:
                if key == 'playerChange':
                    if text_row.get(key) is not None:
                        for x in ['outPlayer', 'inPlayer', 'shiftPlayer']:
                            if x in text_row.get(key).keys():
                                text_row_dict[x] = text_row.get(key).get(x).get('playerId')
                else:
                    text_row_dict[key] = None if key not in text_row.keys() else text_row.get(key)
            # text_row_dict['referee'] = referee
            text_row_dict['stadium'] = stadium
            text_set.append(text_row_dict)
    text_set_df = pd.DataFrame(text_set)
    text_set_df = text_set_df.rename(index=str, columns={'ptsPitchId': 'pitchId'})
    text_set_df.seqno = pd.to_numeric(text_set_df.seqno)

    # pitch by pitch 트래킹 데이터 취합
    pitch_data_set = []
    pitch_data_df = None
    for k in range(len(relay_list)):
        if relay_list[k].get('ptsOptionList') is not None:
            for j in range(len(relay_list[k].get('ptsOptionList'))):
                pitch_data = relay_list[k].get('ptsOptionList')[j]

                pitch_data_dict = {}
                pitch_data_dict['textOrder'] = relay_list[k].get('no')
                for key in pitch_keys:
                    pitch_data_dict[key] = None if key not in pitch_data.keys() else pitch_data.get(key)
                pitch_data_set.append(pitch_data_dict)

    # 텍스트(중계) 데이터, 트래킹 데이터 취합
    if len(pitch_data_set) > 0:
        pitch_data_df = pd.DataFrame(pitch_data_set)
        relay_df = pd.merge(text_set_df, pitch_data_df, how='outer').sort_values(['textOrder', 'seqno'])
    else:
        relay_df = text_set_df.sort_values(['textOrder', 'seqno'])

    ##################################################
    # 3. 선발 라인업, 포지션, 레퍼리 데이터 가져오기 #
    ##################################################
    lineup_url = 'https://sports.news.naver.com/gameCenter'\
                 '/gameRecord.nhn?category=kbo&gameId='
    lineup_response = requests.get(lineup_url + game_id)
    if lineup_response is None:
        lineup_response.close()
        return None

    lineup_soup = BeautifulSoup(lineup_response.text, 'lxml')
    lineup_response.close()

    scripts = lineup_soup.find_all('script')
    team_names = lineup_soup.find_all('span', attrs={'class': 't_name_txt'})
    away_team_name = team_names[0].contents[0].split(' ')[0]
    home_team_name = team_names[1].contents[0].split(' ')[0]

    for tag in scripts:
        if len(tag.contents) > 0:
            if tag.contents[0].find('DataClass = ') > 0:
                contents = tag.contents[0]
                start = contents.find('DataClass = ') + 36
                end = contents.find('_homeTeam')
                oldjs = contents[start:end].strip()
                while oldjs[-1] != '}':
                    oldjs = oldjs[:-1]
                while oldjs[0] != '{':
                    oldjs = oldjs[1:]
                cont = json.loads(oldjs)
                break

    # 구심 정보 가져와서 취합
    referee = cont.get('etcRecords')[-1]['result'].split(' ')[0]
    relay_df = relay_df.assign(referee = referee)

    # 경기 끝나고 나오는 박스스코어, 홈/어웨이 라인업
    boxscore = cont.get('battersBoxscore')
    away_lineup = boxscore.get('away')
    home_lineup = boxscore.get('home')

    pos_dict = {'중': '중견수', '좌': '좌익수', '우': '우익수',
                '유': '유격수', '포': '포수', '지': '지명타자',
                '一': '1루수', '二': '2루수', '三': '3루수'}

    home_players = []
    away_players = []

    for i in range(len(home_lineup)):
        player = home_lineup[i]
        name = player.get('name')
        pos = player.get('pos')[0]
        pCode = player.get('playerCode')
        home_players.append({'name': name, 'pos': pos, 'pCode': pCode})

    for i in range(len(away_lineup)):
        player = away_lineup[i]
        name = player.get('name')
        pos = player.get('pos')[0]
        pCode = player.get('playerCode')
        away_players.append({'name': name, 'pos': pos, 'pCode': pCode})
    
    
    ##############################
    # 4. 기존 라인업 정보와 취합 #
    ##############################
    hit_columns = ['name', 'pCode', 'posName',
                   'hitType', 'seqno', 'batOrder']
    pit_columns = ['name', 'pCode', 'hitType', 'seqno']

    atl = game_data_set.get('awayTeamLineUp')
    abat = atl.get('batter')
    apit = atl.get('pitcher')
    abats = pd.DataFrame(abat, columns=hit_columns).sort_values(['batOrder', 'seqno'])
    apits = pd.DataFrame(apit, columns=pit_columns).sort_values('seqno')

    htl = game_data_set.get('homeTeamLineUp')
    hbat = htl.get('batter')
    hpit = htl.get('pitcher')
    hbats = pd.DataFrame(hbat, columns=hit_columns).sort_values(['batOrder', 'seqno'])
    hpits = pd.DataFrame(hpit, columns=pit_columns).sort_values('seqno')

    # 선발 출장한 경우, 선수의 포지션을 경기 시작할 때 포지션으로 수정
    # (pitch by pitch 데이터에서 가져온 정보는 경기 종료 시의 포지션임)
    for player in away_players:
        # '교'로 적혀있는 교체 선수는 넘어간다
        if player.get('pos') == '교':
            continue
        abats.loc[(abats.name == player.get('name')) &
                  (abats.pCode == player.get('pCode')), 'posName'] = pos_dict.get(player.get('pos'))

    for player in home_players:
        # '교'로 적혀있는 교체 선수는 넘어간다
        if player.get('pos') == '교':
            continue
        hbats.loc[(hbats.name == player.get('name')) &
                  (hbats.pCode == player.get('pCode')), 'posName'] = pos_dict.get(player.get('pos'))

    abats['homeaway'] = 'a'
    hbats['homeaway'] = 'h'
    apits['homeaway'] = 'a'
    hpits['homeaway'] = 'h'
    abats['team_name'] = away_team_name
    hbats['team_name'] = home_team_name
    apits['team_name'] = away_team_name
    hpits['team_name'] = home_team_name

    batting_df = pd.concat([abats, hbats])
    pitching_df = pd.concat([apits, hpits])
    batting_df.pCode = pd.to_numeric(batting_df.pCode)
    pitching_df.pCode = pd.to_numeric(pitching_df.pCode)

    return pitching_df, batting_df, relay_df


def download_pbp_files(start_date, end_date, save_path=None, debug_mode=False):
    start_time = time.time()
    game_ids = get_game_ids(start_date, end_date)
    end_time = time.time()
    if debug_mode is True:
        print(f'{len(game_ids)} game, elapsed {(end_time - start_time):.2f} sec in get_game_ids')
    
    skipped = 0
    done = 0
    start_time = time.time()
    get_data_time = 0
    for gid in game_ids:
        now = datetime.datetime.now().date()
        gid_to_date = datetime.date(int(gid[:4]),
                            int(gid[4:6]),
                            int(gid[6:8]))
        if gid_to_date > now:
            skipped += 1
            continue
        
        ptime = time.time()
        game_data_dfs = get_game_data(gid) 
        get_data_time += time.time() - ptime
        if game_data_dfs is not None:
            gs = game_status()
            gs.load(gid, game_data_dfs[0], game_data_dfs[1], game_data_dfs[2])
            gs.parse_game()
            gs.save_game(save_path)
            done += 1
        else:
            skipped += 1
            continue
    
    end_time = time.time()
    parse_time = end_time - start_time - get_data_time
    if debug_mode is True:
        print(f'{len(game_ids)} game, elapsed {(get_data_time):.2f} sec in get_game_data')
        print(f'{len(game_ids)} game, elapsed {(parse_time):.2f} sec in parse_game')
