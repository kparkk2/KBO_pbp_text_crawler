# pbp.py
# Play-By-Play 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files
# 변환 파트는 현재 미구현

from check_args import get_args
from pbp_download import pbp_download
from pbp_parser import pbp_parser
import logManager


def run_pbp_download(args, lm=None):
    pbp_download(args[0], args[1], args[2], args[3], lm)


def run_pbp_parser(args, lm=None):
    pbp_parser(args[0], args[1], args[2], args[3], lm)


if __name__ == "__main__":
    args = []  # m_start, m_end, y_start, y_end
    options = []  # onlyConvert, onlyDownload
    get_args(args, options)
    lm = logManager.LogManager()

    if (options[0] is True) & (options[1] is False):
        run_pbp_parser(args, lm)
    elif (options[0] is False) & (options[1] is True):
        run_pbp_download(args, lm)
    else:
        run_pbp_download(args, lm)
        run_pbp_parser(args, lm)
    lm.killLogManager()