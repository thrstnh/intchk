#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlite3 import connect
from time import time


STMT = {'CREATE': '''CREATE TABLE IF NOT EXISTS intchk (
                                path TEXT NOT NULL,
                                chksum TEXT NOT NULL,
                                size INTEGER NOT NULL,
                                took INTEGER NOT NULL,
                                first INTEGER NOT NULL,
                                last INTEGER NOT NULL,
                                UNIQUE(path));''',

        'INSERT': '''INSERT INTO intchk
                                (path, chksum, size, took, first, last)
                        VALUES  (?, ?, ?, ?, ?, ?);''',

        'SIZE': 'SELECT SUM(size) FROM intchk;',

        'LENGTH': 'SELECT COUNT(path) FROM intchk;',

        'SELECT_path': '''SELECT path, chksum, size, took, first, last
                            FROM intchk
                            WHERE 1
                                AND path = ?;''',

        'OLDEST': '''SELECT MIN(first) FROM intchk;''',

        'NEWEST': '''SELECT MAX(first) FROM intchk;''',

        'SINCE': '''SELECT MAX(first) - MIN(first) FROM intchk;'''}


class SQLhash(object):

    def __init__(self, dbfile=None, ctype='SHA512'):
        self.connection = None
        self.cursor = None
        self.dbfile = dbfile
        self.ctype = ctype
        self._initDB()

    def now(self):
        return int(time())

    def _initDB(self):
        self.connection = connect(self.dbfile)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        self._exec_sql(STMT['CREATE'])

    def _exec_sql(self,sql, params=None, commit=True):
        if not params:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)
        if commit:
            self.connection.commit()

    def insert(self, path, chash, size, took=0, ts_first=None, ts_last=None):
        self._exec_sql(STMT['INSERT'], (path, chash, size, took,
                            ts_first if ts_first else self.now(),
                            ts_last if ts_last else self.now()))

    def read(self, path):
        self._exec_sql(STMT['SELECT_path'], (path,))
        return self.cursor.fetchone()

    def size(self):
        self._exec_sql(STMT['SIZE'])
        return self.cursor.fetchone()[0]

    def length(self):
        self._exec_sql(STMT['LENGTH'])
        return self.cursor.fetchone()[0]
