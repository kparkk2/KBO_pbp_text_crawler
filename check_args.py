#check_args.py
#-*- coding: utf-8 -*-

import datetime
import logging
import logging.handlers

logger = logging.getLogger('mylogger')
fomatter = logging.Formatter('[%(levelname)s\t||%(filename)s::%(lineno)s] %(asctime)s > %(message)s')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(fomatter)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)


def convert_args( output, input, options ):
    # convert arguments
    # check if not number, integer
    onlyConvert = False
    onlyDownload = False
    year_max = datetime.datetime.now().year

    if len(input) < 2:
        output[0] = 3
        output[1] = 10
        output[2] = 2016
        output[3] = min(2016, year_max)
        return

    # max 6 args - PYFILE ARG1 ARG2 ARG3 ARG4 ARG5
    if len(input) < 7:
        i = 0
        for arg in input:
            if not arg.isdigit():
                if arg.find('-c') >= 0:
                    onlyConvert = True
                elif arg.find('-d') >= 0:
                    onlyDownload = True
                elif arg.find('.py') >= 0:
                    continue
                else:
                    logger.setLevel(logging.DEBUG)
                    logger.debug( input )
                    logger.debug("invalid argument")
                    exit(1)
            else:
                output[i] = int(arg)
                i = i+1
    if i == 0:
        output[0] = 3
        output[1] = 10
        output[2] = 2016
        output[3] = min(2016, year_max)

    options[0] = onlyConvert
    options[1] = onlyDownload

def check_args( args ):
    # check month & year condition
    mon_start = 13
    mon_end = 0
    year_max = datetime.datetime.now().year
    year_start = year_max
    year_end = 0

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
            if years == 2:
                logger.setLevel(logging.DEBUG)
                logger.debug( args )
                logger.debug("invalid argument : %d"%(args[i]))
                logger.debug("%d %d %d %d" % (mon_start, mon_end, year_start, year_end))
                exit(1)

            year_start = min(year_start, args[i])
            year_end = max(year_end, args[i])
            years +=1

        elif args[i] > 0:
            if mons == 2:
                logger.setLevel(logging.DEBUG)
                logger.debug(args)
                logger.debug("invalid argument : %d"%(args[i]))
                logger.debug("%d %d %d %d"%(mon_start, mon_end, year_start, year_end))
                exit(1)

            mon_start = min(mon_start, args[i])
            mon_end = max(mon_end, args[i])
            mons += 1

        else:
            logger.setLevel(logging.DEBUG)
            logger.debug(args)
            logger.debug("wrong argument: %d"%(args[i]))
            logger.debug("%d %d %d %d" % (mon_start, mon_end, year_start, year_end))
            exit(1)

    args[0] = mon_start
    args[1] = mon_end
    args[2] = year_start
    args[3] = year_end
