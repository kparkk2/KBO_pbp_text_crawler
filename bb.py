# bb.py
# 타구 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files

from check_args import get_args
from bb_download import bb_download
from bb_convert_to_csv import bb_convert_to_csv


def run_bb_download(arg):
    bb_download(arg[0], arg[1], arg[2], arg[3])


def run_bb_convert_to_csv(arg):
    bb_convert_to_csv(arg[0], arg[1], arg[2], arg[3])


if __name__ == "__main__":
    args = []       # m_start, m_end, y_start, y_end
    options = []    # onlyConvert, onlyDownload
    get_args(args, options)

    if (options[0] is True) & (options[1] is False):
        run_bb_convert_to_csv(args)
    elif (options[0] is False) & (options[1] is True):
        run_bb_download(args)
    else:
        run_bb_download(args)
        run_bb_convert_to_csv(args)
