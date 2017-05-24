#pbp.py
#-*- coding: utf-8 -*-
# Play-By-Play 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files
# 변환 파트는 현재 미구현

from check_args import getArgs
#from pbp_data_parser import pbp_data_parser
#from pbp_bb_field_parser import pbp_bb_field_parser
from pbp_data_get_json import pbp_data_get_json

#def run_pbp_bb_field_parser( args ):
#    pbp_bb_field_parser( args[0], args[1], args[2], args[3] )

def run_pbp_data_get_json( args ):
    pbp_data_get_json( args[0], args[1], args[2], args[3] )

if __name__ == "__main__":
    args = [] # m_start, m_end, y_start, y_end
    options = []    # onlyConvert, onlyDownload
    getArgs( args, options )

    run_pbp_data_get_json( args )
#    if onlyConvert == True:
#        run_pbp_bb_field_parser( args )
#    elif onlyDownload == True:
#        run_pbp_data_get_json( args )
#    else:
#        run_pbp_data_get_json( args )
        #run_pbp_bb_field_parser( args )
