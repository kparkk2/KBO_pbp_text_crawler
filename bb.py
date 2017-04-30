# bb.py
#-*- coding: utf-8 -*-
# 타구 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files

import sys
from check_args import check_args
from check_args import convert_args
from bbDownload import bbDownload
from bbConvertToCSV import bbConvertToCSV

def run_bbDownload( args ):
    bbDownload( args[0], args[1], args[2], args[3] )

def run_bbConvertToCSV( args ):
    bbConvertToCSV( args[0], args[1], args[2], args[3] )

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

    if onlyConvert == True:
        run_bbConvertToCSV( args )
    elif onlyDownload == True:
        run_bbDownload( args )
    else:
        run_bbDownload( args )
        run_bbConvertToCSV( args )
