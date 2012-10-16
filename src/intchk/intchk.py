#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
from time import time
from os.path import join, walk
from db import SQLhash, dbstats
from deflog import now, init_logger
from actions import rescan
from tools import grab_unit, init_env, ftime, DB_DIR, LOG_DIR
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
    - argparser
'''
ICENV = init_env()


def service(label, algorithm=None):
    if not label:
        lab = ['  - {} => {}'.format(k,v) for k,v in ICENV['WATCHED'].items()]
        print('labels:\n{}'.format('\n'.join(lab)))
        return
    if label == 'stats':
        dbstats(ICENV)
        return
    stats = dict(fnew=0, fdiffers=0, ftotal=0, fskipped=0, size_new=0, size_skipped=0)
    for name, path in ICENV['WATCHED'].items():
        if name != label and label != 'all':
            continue
        out = '{}-{}'.format(name, ICENV['ALGORITHM'])
        dbfp = join(DB_DIR, out + '.sqlite')
        logfp = join(LOG_DIR, '{}-{}.log'.format(out, now()))
        logger = init_logger(logfp)
        sql_hasher = None
        if algorithm:
            out = 'using non-config algorithm!\n'\
                    'config-algorithm: {}\n'\
                    'using:            {}'
            logger.info(out.format(ICENV['ALGORITHM'], algorithm))
            sql_hasher = SQLhash(logger, dbfp, algorithm)
        else:
            out = 'using config algorithm: {}'
            logger.info(out.format(ICENV['ALGORITHM']))
            sql_hasher = SQLhash(dbfp, ICENV['ALGORITHM'])
        tstart = time()
        try:
            walk(path, rescan, (ICENV, logger, sql_hasher, stats))
        except KeyboardInterrupt:
            logger.debug('caught KeyboardInterrupt; stop!')
        except Exception as err:
            logger.debug('undefined error: {}'.format(err))
            raise err
        tstop = time()
        data = dict(line = 79 * '-',
                    algorithm = ICENV['ALGORITHM'],
                    label =  name,
                    path = path,
                    filecount = sql_hasher.length(),
                    runtime = round(tstop - tstart, 5),
                    size_sum = grab_unit(sql_hasher.size()),
                    took = ftime(tstop - tstart))
        summary = '''
{line}
::summary
{line}
:algorithm     {algorithm}
:label         {label}   ->   {path}

            files       size
new             {fnew:>}        {size_new:>}
skipped         {fskipped:>}        {size_skipped:>}
total           {ftotal:>}        {size_sum:>}

this run took {took}
{line}'''
        data.update(stats)
        for key in ['size_new', 'size_skipped']:
            data[key] = grab_unit(data[key])
        logger.info(summary.format(**data))


if __name__ == '__main__':
    label = None
    algorithm = None
    if len(sys.argv) > 1:
        label = sys.argv[1]
    if len(sys.argv) > 2:
        algorithm = sys.argv[2]
    service(label, algorithm)
