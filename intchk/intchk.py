#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
import argparse
from time import time
from os.path import join, walk
from db import SQLhash, dbstats, dbfile, slurp_all
from deflog import now, init_logger
from actions import rescan
from tools import grab_unit, init_env, ftime, LOG_DIR
r'''
This tool scans directories and stores the size of the file in bytes
and also the sha512sum (or another hash, decide for yourself, which
one is your favourite or just runs faster at a big amount of data...).
Once you gathered this information, you are able to run this tool
again and check, if the data has changed. Stored are also the dates of
the first scan and the date of the last check as a unix timestamp.

linux packages:
    md5deep

    author: thorsten hillebrand
    mail:   thrstn.hllbrnd@gmail.com

TODO
    - check, if a md5checksum(-file) exists for this file and
        verify it's still the same
    - check, if there are files with the same name
    - search for specific content, like covers, lyrics, depending
        on the appropriate filetype
    - gui for searching: TreasureSeeker
    - add network support
'''
ICENV = init_env()

def dump_entries():
    keys = ICENV['WATCHED'].keys()
    return map(slurp_all,
                map(dbfile, keys,
                            [ICENV for _ in range(len(keys))]))

def show_store(name, dry=True):
    return '''
{line}
::summary
{line}
:algorithm     {algorithm}
:label         {label}   ->   {path}

            files       size
new             {fnew:>}        {size_new:>}
skipped         {fskipped:>}        {size_skipped:>}
total           {filecount:>}        {size_sum:>}

this run took {took}
average speed {speed}MB/s
{line}'''.format(**scan_store(name, dry))

def scan_store(name, dry=False):
    stats = dict(fnew=0, fdiffers=0, ftotal=0, fskipped=0, size_new=0, size_skipped=0)
    if name not in ICENV['WATCHED']:
        raise IOError('store does not exist!')
    path = ICENV['WATCHED'][name]
    stats['path'] = path
    logger = init_logger(join(LOG_DIR, '{}-{}-{}.log'.format(name, ICENV['ALGORITHM'], now())))
    sql_hasher = SQLhash(dbfile(name, ICENV), ICENV['ALGORITHM'])
    tstart = time()
    try:
        if not dry:
            walk(path, rescan, (ICENV, logger, sql_hasher, stats))
    except KeyboardInterrupt:
        logger.debug('caught KeyboardInterrupt; stop!')
    except Exception as err:
        logger.debug('undefined error: {}'.format(err))
        raise err
    tstop = time()
    stats['size'] = sql_hasher.size()
    stats['tdiff'] = tstop - tstart
    stats['speed'] = (stats['size_new'] / pow(1024, 2)) / (stats['tdiff'] or 1)
    stats['line'] = 79 * '-'
    stats['algorithm'] = ICENV['ALGORITHM']
    stats['label'] = name
    stats['filecount'] = sql_hasher.length()
    stats['runtime'] = round(tstop - tstart, 5)
    stats['size_sum'] = grab_unit(stats['size'])
    stats['took'] = ftime(stats['tdiff'])
    for key in ['size_new', 'size_skipped']:
        stats[key] = grab_unit(stats[key])
    return stats

def intchk_parser():
    parser = argparse.ArgumentParser()
    options = {
            'store': ['-s', '--store', 'show label', str],
            'scan': ['-S', '--scan', 'scan store', str],
            'algorithm': ['-a', '--algorithm', 'set cryptographic hash type', str],
            'dump': ['-d', '--dump', 'dump all entries', 'store_true'],
            'all':   ['-r', '--rescan', 'rescan all', 'store_true'],
            'logs': ['-l', '--logs', 'show logs', 'store_true'],
            'verbose': ['-v', '--verbose', 'increase output verbosity', 'store_true']}
    for k, opt in options.items():
        short, long, help, action = opt
        if type(action) == type:
            parser.add_argument(short, long, help=help, type=action)
        else:
            parser.add_argument(short, long, help=help, action=action)
    args = parser.parse_args()
    return args

def labels():
    lab = ['  - {} => {}'.format(k,v) for k,v in ICENV['WATCHED'].items()]
    ret = 'labels:\n{}'.format('\n'.join(lab))
    return ret

def run():
    args = intchk_parser()
    if args.logs:
        return dbstats(ICENV)
    if args.dump:
        data = dump_entries()
        print(data)
        return data
    if args.store:
        print(show_store(args.store))
    if args.scan:
        print(show_store(args.scan, False))
    if args.rescan:
        for name in ICENV['WATCHED'].keys():
            print(show_store(name, False))
    if not args.store and not args.rescan:
        print(labels())
        return


if __name__ == '__main__':
    run()
