# check_args.py

import datetime
# import logging
import argparse


def get_args(output, options):
    # convert arguments
    # check if not number, integer

    parser = argparse.ArgumentParser(description='Get batted ball data.')
    parser.add_argument('dates',
                        metavar='dates',
                        type=int,
                        nargs='*',
                        default=2016,
                        help='start/end (month/year)')

    parser.add_argument('-c',
                        action='store_true',
                        help='JSON->csv only')

    parser.add_argument('-d',
                        action='store_true',
                        help='Download only')

    '''
    logger = logging.getLogger('mylogger')
    fomatter = logging.Formatter('[%(filename)s::%(lineno)s] %(asctime)s > %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(fomatter)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG)
    '''

    args = parser.parse_args()

    dates = args.dates
    year_max = datetime.datetime.now().year

    months = []
    years = []

    if type(dates) is int:
        dates = [2016, 2016, 3, 3]
    elif len(dates) > 4:
        logger.debug('too many date')
        print('too many date')
        exit(1)

    for d in dates:
        if (d > 12) & (d > 2010) & (d <= year_max):
            years.append(d)
        elif (d >= 1) & (d <= 12):
            months.append(d)
        else:
            #logger.debug('invalid date')
            print('invalid date')
            print('possible year range: 2011~%d'%(year_max))
            print('possible month range: 1~12')
            exit(1)

    if len(years) > 2:
        #logger.debug('too many year')
        print('too many year')
        exit(1)

    if len(months) > 2:
        #logger.debug('too many month')
        print('too many month')
        exit(1)

    mmin = 4
    mmax = 4
    ymin = 2016
    ymax = 2016

    if len(months) == 1:
        mmin = months[0]
        mmax = mmin
    elif len(months) == 2:
        mmin = min(months)
        mmax = max(months)

    if len(years) == 0:
        ymin = 2016
        ymax = 2016
    elif len(years) == 1:
        ymin = years[0]
        ymax = ymin
    else:
        ymin = min(years)
        ymax = max(years)

    output.append(mmin)
    output.append(mmax)
    output.append(ymin)
    output.append(ymax)

    options.append(args.c)
    options.append(args.d)