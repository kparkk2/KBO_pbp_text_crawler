#pbp.py
#-*- coding: utf-8 -*-
# Play-By-Play 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files
# 변환 파트는 현재 미구현

import sys
from check_args import check_args
from check_args import convert_args
#from pbp_data_parser import pbp_data_parser
from pbp_bb_field_parser import pbp_bb_field_parser
from pbp_data_get_json import pbp_data_get_json

def run_pbp_bb_field_parser( args ):
    pbp_bb_field_parser( args[0], args[1], args[2], args[3] )

def run_pbp_data_get_json( args ):
    pbp_data_get_json( args[0], args[1], args[2], args[3] )

if __name__ == "__main__":
    args = [0, 0, 0, 0]
    # 기본값; 3~10월, 2010~올해까지로 자동 세팅
    options = [False, False]
    convert_args( args, sys.argv, options )
    check_args( args )
    onlyConvert = options[0]
    onlyDownload = options[1]

    for i in range(len(args)):
        if not isinstance( args[i], int ):
            if args[i].isdigit():
                args[i] = int(args[i])
            print 'arg must be digit.. something is wrong: ',
            print args[i]

    if onlyConvert == True:
        run_pbp_bb_field_parser( args )
#    elif onlyDownload == True:
#        run_pbp_data_get_json( args )
    else:
        run_pbp_data_get_json( args )
        #run_pbp_bb_field_parser( args )
