# bb.py
#-*- coding: utf-8 -*-
# 타구 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files

from check_args import getArgs
from bbDownload import bbDownload
from bbConvertToCSV import bbConvertToCSV

def run_bbDownload( args ):
    bbDownload( args[0], args[1], args[2], args[3] )

def run_bbConvertToCSV( args ):
    bbConvertToCSV( args[0], args[1], args[2], args[3] )


if __name__ == "__main__":
    args = [] # m_start, m_end, y_start, y_end
    options = []    # onlyConvert, onlyDownload
    getArgs( args, options )

    if (options[0] == True) & (options[1] == False):
        run_bbConvertToCSV( args )
    elif (options[0] == False) & (options[1] == True):
        run_bbDownload( args )
    else:
        run_bbDownload( args )
        run_bbConvertToCSV( args )
