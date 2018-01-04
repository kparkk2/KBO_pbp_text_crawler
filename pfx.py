# pfx.py
# Pfx 데이터 JSON 형식으로 받아서 CSV 파일로 변환
# get pfx data in JSON form & convert to CSV files

from check_args import get_args
from pfx_download import pfx_download
import logManager


def run_pfx_download(args, lm=None):
    pfx_download(args[0], args[1], args[2], args[3], lm)


if __name__ == "__main__":
    args = []  # m_start, m_end, y_start, y_end
    options = []  # onlyConvert, onlyDownload
    get_args(args, options)
    lm = logManager.LogManager()

    run_pfx_download(args, lm)
    lm.killLogManager()