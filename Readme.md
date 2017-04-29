# Code Description

이 branch에 남은 코드는

N사의 text relay 시스템에서 파일을 가져와 download & parse를 통해서

play-by-play data & lineup data & batted-ball data를 수집하는 것을 목표로 한다.

# Requirement
* Python 2.7.x
  * Python Modules : lxml, BeautifulSoup, urllib2
* Windows, OS X, Linux
* internet connection


# File Desciption

### play-by-play data downloader
pbp.py : pbp data 수집을 위한 코드 main.  
아래 두 모듈에 구현된 함수를 실행한다.  
* pbp_data_get_json.py
  - N사의 text relay 웹페이지에 접속해서 파일의 링크를 따고 download한다. JSON 형식의 데이터가 HTML 파일의 script tag 안에 둘러싸여 있기 때문에 적당히 parse해서 저장해야 한다.
* pbp_data_json_to_csv.py
  - download한 JSON 파일을 읽어서 원하는 데이터를 추출, pbp data를 뽑아내고 가공된 pbp data를 CSV파일로 저장한다.

### lineup data downloader
lineup.py : lineup data 수집을 위한 코드 main.  
내부에 모든 구현이 되어 있어 stand-alone으로 실행시키면 된다.

### batted ball data downloader
bb.py  : bb data 수집을 위한 코드 main.  
아래 두 모듈에 구현된 함수를 실행한다.  
* bb_data_get_json.py  
  - N사의 match result 웹페이지에 접속해서 파일의 링크를 따고 download한다. JSON 형식의 데이터가 HTML 파일의 script tag 안에 둘러싸여 있기 때문에 적당히 parse해서 저장해야 한다.
* bb_data_json_to_csv.py  
  - download한 JSON 파일을 읽어서 원하는 데이터를 추출, bb data를 뽑아내고 가공된 bb data를 CSV파일로 저장한다.

# HOW TO RUN
- data를 추출할 시기를 입력값으로 줄 수 있다.
- 입력값을 주지 않으면 pbp.py, lineup.py bb.py 내부에 기본 입력값으로 설정된 대로 실행된다.
- 기본 설정은 **[3 10 2010 2016]** 이다.
- 입력값의 순서는 다음과 같아야 한다.
  1. 시작 월
  2. 종료 월
  3. 시작 연도
  4. 종료 연도
- 4개를 순서대로 적어야 한다.
- 뒤의 입력값은 빼도 되지만, 앞의 값이 없는데 뒤의 것을 줄 수는 없다.
  - 1, 2, 3만 입력으로 줄 수 있지만(ex: pbp.py 4 8 2010)
  - 1, 3을 입력으로 줄 수는 없다.(ex: pbp.py 4 2010 - FAIL)
- pbp.py와 bb.py는 옵션으로 -c를 주면 download 대신 JSON->CSV 변환만 진행한다.  

### pbp.py  
```sh
$ python pbp.py # default
$ python pbp.py 3 10 2010 2016 # 2010~2016년까지 3월~10월 데이터 추출
$ python pbp.py 6 10 # 6월~10월 데이터 추출, 연도는 기본 설정대로
$ python pbp.py -c # JSON->CSV 변환만 진행, 기간은 기본 설정대로
```

### lineup.py
```sh
$ python lineup.py # default
$ python lineup.py 3 10 2010 2016 # 2010~2016년까지 3월~10월 데이터 추출
$ python lineup.py 6 10 # 6월~10월 데이터 추출, 연도는 기본 설정대로
```

### bb.py
```sh
$ python bb.py # default
$ python bb.py 3 10 2010 2016 # 2010~2016년까지 3월~10월 데이터 추출
$ python bb.py 6 10 # 6월~10월 데이터 추출, 연도는 기본 설정대로
$ python bb.py -c # JSON->CSV 변환만 진행, 기간은 기본 설정대로
```
### make
```sh
make # pbp data, bb data를 모두 추출
make pbp # pbp data를 추출, 설정은 기본 값
make bb # bb data를 추출, 설정은 기본 값
make clean # download & convert한 데이터 및 경로를 모두 삭제
make cf # 데이터만 모두 삭제(pbp, bb, lineup)
make clean_csv # convert한 CSV 데이터를 모두 삭제(bb)
make clean_json # download한 JSON 데이터를 모두 삭제(pbp, bb, lineup)
```

# TroubleShooting
- 웹페이지 open 도중 멈추는 경우가 있다.
  - 이런 경우는 중단하고 진행 중이던 기간부터 다시 실행하기를 권장한다.
  - python 모듈 문제라 어찌 할 수가 없다.
- 기본 기간 설정 값은 pbp.py, lineup.py, bb.py의 내용을 고쳐서 수정할 수 있다.
``` pbp.py
$ ...
$ if __name__ == "__main__":
$    args = [4, 6, 2016, 2016] # 이 부분을 수정해준다.
$...
```


# Visualization
tableau에서 배경화면(N사 문자중계 결과에 나오는 구장 background image)은 아래와 같이 size conversion한다.
- 원본은 500x500, css의 position 은 445x445, image의 크기는 445x414, 원본의 width는 355로 resize, height는 375로 resize
- new gx = gx * 355 / 500 + 46, 최소 46, 최대 401
- new gy = gy * 375 / 500 - 31, 최소 -31, 최대 344
- gx, gy 값을 위 식에 따라 바꾼 뒤 그 값을 tableau에 뿌린다.
- background image는 왼쪽 0, 오른쪽 445, 아래쪽 414, 위쪽 0으로 세팅
