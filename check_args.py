#check_args.py
#-*- coding: utf-8 -*-

import datetime

def convert_args( arr, args, options ):
    # convert arguments
    # check if not number, integer
    onlyConvert = False
    onlyDownload = False
    year_max = datetime.datetime.now().year

    if len(args) < 2:
        arr[0] = 3
        arr[1] = 10
        arr[2] = 2016
        arr[3] = year_max
        return
    if len(args) < 7:
        i = 0
        for arg in args:
            if not arg.isdigit():
                if arg.find('-c') >= 0:
                    onlyConvert = True
                elif arg.find('-d') >= 0:
                    onlyDownload = True
                elif arg.find('.py') >= 0:
                    continue
                else:
                    print args
                    print "invalid argument"
                    exit(1)
            else:
                arr[i] = int(arg)
                i = i+1
    if i == 0:
        arr[0] = 3
        arr[1] = 10
        arr[2] = 2016
        arr[3] = year_max

    options[0] = onlyConvert
    options[1] = onlyDownload

def check_args( args ):
    # check month & year condition
    mon_start = 0
    mon_end = 0
    year_start = 0
    year_end = 0
    year_max = datetime.datetime.now().year

    digits = 0
    for arg in args:
        if not isinstance( arg, int ):
            if arg.isdigit():
                digits += 1
        else:
            digits += 1

    years = 0
    mons = 0
    for i in range(digits):
        if args[i] > 12 and args[i] <= year_max:
            if year_start == 0:
                year_start = int(args[i])
                years += 1
            elif year_end == 0:
                if year_start <= int(args[i]):
                    year_end = int(args[i])
                    years += 1
                else:
                    year_end = year_start
                    year_start = int(args[i])
                    years += 1
            else:
                print args
                print "invalid argument - year too many"
                exit(1)
        elif args[i] > 0:
            if mon_start == 0:
                mon_start = int(args[i])
                mons += 1
            elif mon_end == 0:
                if mon_start <= int(args[i]):
                    mon_end = int(args[i])
                    mons += 1
                else:
                    mon_end = mon_start
                    mon_start = int(args[i])
                    mons += 1
            else:
                print args
                print "invalid argument - month too many"

    if year_start > 0 and year_end == 0:
        year_end = year_start
        years += 1
    if mon_start > 0 and mon_end == 0:
        mon_end = mon_start
        mons += 1

    if year_start < 2010:
        print args
        print "year_start error: must be larger than 2010"
        exit(1)
    if year_end > year_max:
        print args
        print "year_end error: upper bound is " + str(year_max)
        exit(1)

    if years == 0:
        year_start = 2010
        year_end = year_max
    if mons == 0:
        mon_start = 3
        mon_end = 10

    args[0] = mon_start
    args[1] = mon_end
    args[2] = year_start
    args[3] = year_end
