#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import mkdir
from os.path import expanduser, join, exists
from json import dumps, loads


ICENV = None
ROOT_DIR = expanduser('~/.intchk')
LOG_DIR = join(ROOT_DIR, 'log')
DB_DIR = join(ROOT_DIR, 'db')
CONFIG_FILE = join(ROOT_DIR, 'config')

if not exists(ROOT_DIR):
    mkdir(ROOT_DIR)
    mkdir(LOG_DIR)
    mkdir(DB_DIR)

UNITS = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
UNITS_SIZE = {val: (unit, pow(1024, val)) for unit, val in zip(UNITS, range(len(UNITS)))}

def grab_unit(size_in_bytes):
    counter = 0
    for unit, val in UNITS_SIZE.items():
        if size_in_bytes / val[1] < 1024:
            return '{0:>.3f}{1:>2}'.format(round(size_in_bytes / float(UNITS_SIZE[counter][1]), 3), UNITS_SIZE[counter][0])
        else:
            counter += 1

def ftime(seconds):
    if seconds < 1.0:
        return '{}ms'.format(int(seconds * 1000.))
    return '{}s'.format(round(seconds, 3))


class ICenv(object):

    def __init__(self, data=None):
        self.data = data or {}
        self.load()

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def save(self):
        with open(CONFIG_FILE, 'w') as conf:
            conf.write(dumps(self.data, sort_keys=True, indent=4))

    def load(self):
        try:
            self.data.update(self._load())
        except:
            self._defaults()
            self.save()

    def _load(self):
        with open(CONFIG_FILE) as conf:
            return loads(conf.read())

    def _defaults(self):
        self.data.update(self._default_data())

    def _default_data(self):
        r'''
        ALGORIGHTM:     MD5, MD5DEEP, WHIRLPOOL, SHA1, SHA256, SHA256DEEP, SHA512
        INTERVAL:       periodically check files after interval in seconds
        WATCHED:        dict with an label and the appropriate directory path
        PROCESSES:      num of processes to scan parallel
        '''
        return {'ALGORITHM': 'SHA512',
                'INTERVAL': 259200,
                'WATCHED': {'testdata': '/home/user/test/'},
                'PROCESSES': 1}

    def __str__(self):
        return dumps(self.data, sort_keys=True, indent=4)

def init_env():
    global ICENV
    if not ICENV:
        ICENV = ICenv()
    return ICENV
