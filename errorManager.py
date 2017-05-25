# errorManager.py

import traceback


error_msg = None


def getTracebackStr():
    lines = traceback.format_exc().strip().split('\n')
    if error_msg is not None:
        rl = [error_msg, lines[-1]]
    else:
        rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    for i in range(0, len(lines), 2):
        rl.append('  %s at %s' % (lines[i].strip(), lines[i + 1].strip()))
    return '\n'.join(rl)
