#-*- coding: utf-8 -*-
# get_lineup.py

from check_args import check_args
from check_args import convert_args
import sys
import os
from bs4 import BeautifulSoup
import urllib2
import datetime
import httplib
from urlparse import urlparse

def checkURL(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400

def get_lineup( mon_start, mon_end, year_start, year_end ):
    # set url prefix
    url_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="
    relay_prefix = "http://www.koreabaseball.com/Schedule/Game/BoxScore.aspx?leagueId=1&seriesId=0&gameId="

    # make directory
    if not os.path.isdir("./lineup_data"):
        os.mkdir("./lineup_data")
    os.chdir("./lineup_data")
    # current path : ./lineup_data/

    print "##################################################"
    print "#######          GET LINEUP DATA           #######"
    print "##################################################"
    year_max = datetime.datetime.now().year
    for year in range(year_start, year_end+1):
        # make year directory
        if not os.path.isdir("./" + str(year)):
            os.mkdir("./" + str(year))
        os.chdir(str(year))
        # current path : ./lineup_data/YEAR/

        print "  for Year " + str(year) + "... "

        for month in range(mon_start, mon_end+1):
            if not os.path.isdir( str(month) ):
                os.mkdir( str(month) )
            os.chdir( str(month) )
            # current path : ./lineup_data/YEAR/MONTH/

            # clear path
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for file_name in files:
                os.remove( file_name )

            # get URL
            url = url_prefix + str(month) + "&year=" + str(year)

            # progress bar
            print "    Month " + str(month) + "... "
            sys.stdout.write('\r    [waiting]'),
            sys.stdout.flush()

            # open URL
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year
            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup( html, "lxml" )
            schedule_button = soup.findAll('span', attrs={'class':'td_btn'})

            gameIDs = []
            for btn in schedule_button:
                link = btn.a['href']
                gameIDs.append( link.split('gameId=')[1][0:13] )

            done = 0
            mon_file_num = 0
            for gameID in gameIDs:
                relayLink = relay_prefix + gameID + '&gyear=' + str(year)

                if int(gameID[0:4]) > year_max:
                    continue
                if int(gameID[0:4]) < 2010:
                    continue

                if checkURL(relayLink) :
                    mon_file_num += 1


            for gameID in gameIDs:
                relayLink = relay_prefix + gameID + '&gyear=' + str(year)

                if checkURL(relayLink) :
                    done = done+1
                    try:
                        relay = urllib2.urlopen(relayLink).read()
                    except urllib2.URLError as e:
                        print str(e)
                    soup = BeautifulSoup( relay, "lxml" )

                    bat_table = soup.findAll('table', attrs={'id':'xtable1'})

                    away_bat_name = bat_table[0].tbody.findAll('th', attrs={'class':'name'})
                    away_bat_pos1 = bat_table[0].tbody.findAll('th', attrs={'class':'pos'})
                    away_bat_pos2 = bat_table[0].tbody.findAll('th', attrs={'class':'pos2'})
                    home_bat_name = bat_table[1].tbody.findAll('th', attrs={'class':'name'})
                    home_bat_pos1 = bat_table[1].tbody.findAll('th', attrs={'class':'pos'})
                    home_bat_pos2 = bat_table[1].tbody.findAll('th', attrs={'class':'pos2'})

                    outname = gameID + '_lineup.txt'
                    of = open(outname, 'w')

                    of.write('away_bat\n')
                    for i in range(len(away_bat_name)):
                        of.write(away_bat_pos1[i].text.encode('utf-8') + "," + away_bat_pos2[i].text.encode('utf-8') + "," + away_bat_name[i].text.encode('utf-8') + "\n")

                    of.write('home_bat\n')
                    for i in range(len(home_bat_name)):
                        of.write(home_bat_pos1[i].text.encode('utf-8') + "," + home_bat_pos2[i].text.encode('utf-8') + "," + home_bat_name[i].text.encode('utf-8') + "\n")

                    pit_table = soup.findAll('table', attrs={'id':'xtable3'})

                    away_pit_name = pit_table[0].tbody.findAll('th', attrs={'class':'name'})
                    home_pit_name = pit_table[1].tbody.findAll('th', attrs={'class':'name'})

                    of.write('away_pit\n')
                    for i in range(len(away_pit_name)):
                        of.write(away_pit_name[i].text.encode('utf-8') + "\n")

                    of.write('home_pit\n')
                    for i in range(len(home_pit_name)):
                        of.write(home_pit_name[i].text.encode('utf-8') + "\n")

                    of.close()

                if mon_file_num > 30 :
                    progress_pct = (float(done) / float(mon_file_num))
                    bar = '█' * int(progress_pct*30) + '-'*(30-int(progress_pct*30))
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, progress_pct*100)),
                    sys.stdout.flush()
                elif mon_file_num == 0:
                    mon_file_num = 0
                    # do nothing
                else:
                    bar = '█' * done + '-' * (mon_file_num - done)
                    sys.stdout.write('\r    [%s] %s / %s, %2.1f %%' % (bar, done, mon_file_num, float(done)/float(mon_file_num)*100)),
                    sys.stdout.flush()

            sys.stdout.write('\n')
            sys.stdout.flush()
            print '        Downloaded ' + str(done) + ' files'
            os.chdir('..')
            # current path : ./lineup_data/YEAR/

        os.chdir("..")
        # current path : ./lineup_data/

        print "  YEAR " + str(year) + " Done."

    os.chdir("..")
    # current path : ./

def run_get_lineup( args ):
    get_lineup( args[0], args[1], args[2], args[3] )

if __name__ == "__main__":
    args = [0, 0, 0, 0]
    # 기본값; 3~10월, 2010~올해까지로 자동 세팅
    options = [False, False]
    convert_args( args, sys.argv, options )
    check_args( args )
    run_get_lineup( args )
