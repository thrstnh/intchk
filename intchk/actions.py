#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import time
from os.path import join, isfile, abspath
from subprocess import PIPE, STDOUT, Popen
from tools import ftime, grab_unit


CHECKSUMBIN = {'MD5': 'md5sum',
               'MD5DEEP': 'md5deep',
               'WHIRLPOOL': 'whirlpooldeep',
               'SHA1': 'sha1deep',
               'SHA256': 'sha256sum',
               'SHA256DEEP': 'sha256deep',
               'SHA512': 'sha512sum'}

def hash_pipe(path, ctype):
    start = time()
    cmd = [CHECKSUMBIN[ctype], path]
    checksum = Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0].strip().split()[0]
    stop = time()
    took = stop - start
    return checksum, took

def rescan(args, dirname, files):
    env, log, sql_hasher, stats = args
    for f in files:
        path = abspath(join(dirname, f))
        upath = path.encode('utf-8')
        if isfile(path):
            dbentry = sql_hasher.read(path)
            if dbentry:
                last_check = (time() - dbentry[5])
                if last_check < env['INTERVAL']:
                    stats['fskipped'] += 1
                    stats['size_skipped'] += dbentry[2]
                    days = (env['INTERVAL'] - last_check) / (60 * 60 * 24)
                    out = '- [in {} days] \t{}'
                    log.info(out.format(round(days, 2), upath))
                else:
                    st_path, st_hash, st_size, st_took, st_first, st_last = dbentry
                    chash, took = hash_pipe(path, sql_hasher.ctype)
                    out = '= [{}  {}] \t{}'
                    log.info(out.format(grab_unit(st_size), ftime(took), upath))
                    if st_hash != chash:
                        err = '! {}\n\tstored:  {}\n\tcurrent: {}\n'
                        log.error(err.format(path, st_hash, chash))
                        raise AssertionError(err)
            else:
                fpinfo = os.stat(path)
                checksum, took = hash_pipe(path, sql_hasher.ctype)
                size = fpinfo.st_size
                stats['size_new'] += size
                out = '* [{0:>5} {1:>7}] \t{2}'
                log.info(out.format(grab_unit(size), ftime(took), upath))
                sql_hasher.insert(path, checksum, size, took)
                stats['fnew'] += 1
            stats['ftotal'] += 1
