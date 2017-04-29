# bb.py
#-*- coding: utf-8 -*-
# 타구 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files

import sys
from check_args import check_args
from check_args import convert_args
from bb_data_get_json import bb_data_get_json
from bb_data_json_to_csv import bb_data_json_to_csv

def run_bb_data_get_json( args ):
    bb_data_get_json( args[0], args[1], args[2], args[3] )

def run_bb_data_json_to_csv( args ):
    bb_data_json_to_csv( args[0], args[1], args[2], args[3] )

if __name__ == "__main__":
    args = ['x', 'x', 'x', 'x']
    options = [False, False]
    convert_args( args, sys.argv, options)
    check_args( args )
    onlyConvert = options[0]
    onlyDownload = options[1]

    for i in range(len(args)):
        if not isinstance( args[i], int ):
            if args[i].isdigit():
                args[i] = int(args[i])
#    print args

    if onlyConvert == True:
        run_bb_data_json_to_csv( args )
    elif onlyDownload == True:
        run_bb_data_get_json( args )
    else:
        run_bb_data_get_json( args )
        run_bb_data_json_to_csv( args )
