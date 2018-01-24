# pbp.py
# Play-By-Play 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get batted ball data in JSON form & convert to CSV files

from utils import get_args
from pbp_download import pbp_download
from pbp_parser import pbp_parser
from pfx_download import pfx_download
from pbp_parse2 import parse_main
from pbp_download2 import download_relay, download_pfx
import logManager


def run_pbp_download(args, lm=None):
    # pbp_download(args[0], args[1], args[2], args[3], lm)
    download_relay(args, lm)


def run_pbp_parser(args, lm=None):
    # pbp_parser(args[0], args[1], args[2], args[3], lm)
    parse_main(args, lm)


def run_pfx_download(args, lm=None):
    # pfx_download(args[0], args[1], args[2], args[3], lm)
    download_pfx(args, lm)


if __name__ == "__main__":
    args = []  # m_start, m_end, y_start, y_end
    options = []  # onlyConvert, onlyDownload, onlyPFXDownload
    parser = get_args(args, options)

    # option : -c, -d, -p
    if (options[0] is True) & (options[1] is False) & (options[2] is False):
        relay_lm = logManager.LogManager()  # background logger
        run_pbp_parser(args, relay_lm)
        relay_lm.killLogManager()
    elif (options[0] is False) & (options[1] is True) & (options[2] is False):
        download_lm = logManager.LogManager()  # background logger
        run_pbp_download(args, download_lm)
        download_lm.killLogManager()
    elif (options[0] is False) & (options[1] is False) & (options[2] is True):
        pfx_lm = logManager.LogManager()  # background logger
        run_pfx_download(args, pfx_lm)
        pfx_lm.killLogManager()
    elif (options[0] is False) & (options[1] is False) & (options[2] is False):
        print('choose at least one option!\n')
        parser.print_help()
    else:
        print('choose one option at once!\n')
        parser.print_help()