# check_args.py

import datetime
import argparse


def get_args(output, options):
    # convert arguments
    # check if not number, integer

    parser = argparse.ArgumentParser(description='Get batted ball data.')
    parser.add_argument('dates',
                        metavar='dates',
                        type=int,
                        nargs='*',
                        default=datetime.datetime.now().year,
                        help='start/end (month/year); year > 2007')

    parser.add_argument('-c',
                        action='store_true',
                        help='JSON->csv only')

    parser.add_argument('-d',
                        action='store_true',
                        help='Download only')

    parser.add_argument('-p',
                        action='store_true',
                        help='pfx Download only')

    args = parser.parse_args()

    dates = args.dates
    now = datetime.datetime.now()

    if type(dates) is int:
        # month or year?
        if dates > 12:
            # year
            if (dates < 2008) or (dates > now.year):
                print('invalid year')
                exit(1)
            else:
                year = dates
                if year == now.year:
                    # current season
                    if now.month < 3:
                        print('invalid year : season has not begun...')
                        exit(1)
                    else:
                        dates = [now.year, now.year, 3, now.month]
                else:
                    # previous season
                    dates = [now.year, now.year, 3, 10]
        elif dates > 0:
            # month
            if (dates < 3) or (dates > 10):
                print('invalid month : possible range is 3~10')
                exit(1)
            else:
                month = dates
                if month <= now.month:
                    dates = [now.year, now.year, month, month]
                else:
                    # trying for future...
                    print('invalid month : current month is {}; you entered{}.'.format(now.month, month))
                    exit(1)
        else:
            print('invalid parameter')
            exit(1)
    elif len(dates) > 4:
        print('too many date option')
        exit(1)

    months = []
    years = []

    for d in dates:
        if (d > 12) & (d > 2007) & (d <= now.year):
            years.append(d)
        elif (d >= 1) & (d <= 12):
            months.append(d)
        else:
            print('invalid date')
            print('possible year range: 2008~%d'%(now.year))
            print('possible month range: 1~12')
            exit(1)

        if len(years) > 2:
            print('too many year')
            exit(1)

        if len(months) > 2:
            print('too many month')
            exit(1)

    mmin = 3
    mmax = 3
    ymin = now.year
    ymax = now.year

    if len(months) == 0:
        mmin = 3
        mmax = 10
    elif len(months) == 1:
        mmin = mmin = months[0]
    else:
        mmin = min(months)
        mmax = max(months)

    if len(years) == 0:
        ymin = now.year
        ymax = 2016
    elif len(years) == 1:
        ymin = ymin = years[0]
    else:
        ymin = min(years)
        ymax = max(years)

    output.append(mmin)
    output.append(mmax)
    output.append(ymin)
    output.append(ymax)

    options.append(args.c)
    options.append(args.d)
    options.append(args.p)