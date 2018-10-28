# -*- coding: utf-8 -*-
import psycopg2
import sys
import locale
reload(sys)
sys.setdefaultencoding('utf-8')


def connect(ip):
    try:
        conn = psycopg2.connect(
            host=ip,
            user='agent',
            port='5432',
            dbname='agents'
        )
        return conn
    except DataBaseException as e:
        sys.exit(_('\nОшибка базы данных: "%s"\n') % str(e))


class DataBaseException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        stk = traceback.extract_tb(tb, 1)
        fname = stk[0][2]
        return 'DataBaseApi exception: func name: {}, exception: {}'.format(fname, self.value)


class DataBaseApi():

    def __init__(self, connect):
        self.conn = connect
        self.cursor = self.conn.cursor()
        self.mainApp = getApplication()

    def __del__(self):
        self.conn.close()

    def createTable(self):
        try:
            statement = '''CREATE TABLE IF NOT EXISTS "scales" (
                        scale_name varchar(150) PRIMARY KEY,
                        start timestamp,
                        stop timestamp,
                        status smallint
                        );'''
            self.cursor.execute(statement)
            self.conn.rollback()
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            sys.exit(_('\nОшибка базы данных: "%s"\n') % str(e))

    def createScale(self, name):
        try:
            statement = '''SELECT "scale_name" from scales where scale_name = (%s) and status = 3'''
            self.cursor.execute(statement, name)
            if self.cursor.fetchone():
                return False
            statement = '''INSERT INTO scales("scale_name", "status") values (%s, 0)'''
            self.cursor.execute(statement, (name,))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def searchScaleWithLike(self, name):
        try:
            if isinstance(name, list):
                if name:
                    name = tuple(name)
                    statement = '''SELECT "scale_name", COALESCE("start",  TIMESTAMP '-infinity'),
                    COALESCE("stop",  TIMESTAMP '-infinity'), "status" from scales where scale_name in %s'''
                    self.cursor.execute(statement, (name,))
                    _cursor = self.cursor.fetchall()
                    return _cursor
                else:
                    return []
            else:
                statement = '''SELECT "scale_name", COALESCE("start",  TIMESTAMP '-infinity'),
                COALESCE("stop",  TIMESTAMP '-infinity'), "status" from scales where scale_name like (%s) and status <> 3'''
                self.cursor.execute(statement, ('%' + name + '%',))
                return self.cursor.fetchall()
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))

    def searchScale(self, name):
        try:
            statement = '''SELECT "scale_name", COALESCE("start",  TIMESTAMP '-infinity'),
            COALESCE("stop",  TIMESTAMP '-infinity'), "status" from scales where scale_name = (%s) and status <> 3'''
            self.cursor.execute(statement, (name,))
            return self.cursor.fetchall()
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))

    def insertScale(self, scale):
        try:
            statement = '''SELECT "scale_name" from scales where scale_name = (%s) and status = 3 '''
            self.cursor.execute(statement, (scale[0],))
            temp = self.cursor.fetchone()
            if temp:
                return False
            else:
                statement = '''INSERT into scales("scale_name", "start", stop, "status") values (%s, %s, %s, %s)'''
                self.cursor.execute(statement, scale)
                self.conn.commit()
                return True
        except DataBaseException, e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def getScales(self):
        '''get name of scale'''
        try:
            statement = '''SELECT "scale_name", COALESCE("start",  TIMESTAMP '-infinity'),
            COALESCE("stop",  TIMESTAMP '-infinity'), "status" from scales WHERE status <> 3'''
            self.cursor.execute(statement)
            return self.cursor.fetchall()
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))

    def deleteScale(self, nameOfScale):
        '''нет проверки на наличие в бд'''
        try:
            # statement = '''DELETE FROM scales WHERE scale_name = (%s)'''
            statement = '''UPDATE scales SET status = 3 WHERE scale_name = (%s)'''
            self.cursor.execute(statement, (nameOfScale,))
            self.conn.commit()
            return True
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def updateScale(self, dictOfValue):
        '''dict of nameOfScale, column, value'''
        try:
            statement = '''UPDATE scales SET {} = (%s)
                        WHERE scale_name = (%s)'''.format(dictOfValue['column'])
            self.cursor.execute(
                statement, (dictOfValue['value'], dictOfValue['nameOfScale']))
            self.conn.commit()
            return True
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def queryExec(self, statement):
        try:
            self.cursor.execute(statement)
            return self.cursor.fetchone()
        except DataBaseException, e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))

    def start(self, dt, name):
        try:
            statement = '''UPDATE scales SET start = (%s), status = 1 WHERE scale_name = (%s)'''
            self.cursor.execute(statement, (dt, name))
            self.conn.commit()
            return True
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def stop(self, dt, name):
        try:
            statement = '''UPDATE scales SET stop = (%s), status = 2 WHERE scale_name = (%s)'''
            self.cursor.execute(statement, (dt, name))
            self.conn.commit()
            return True
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def countStatusLocal(self):
        try:
            statement = '''SELECT (SELECT COUNT("scale_name") as "c1" FROM scales WHERE status = 0) as count_1,
            (select count("scale_name") as c2 from scales where status = 1) as count_2,
            (select count("scale_name") as c3 from scales where status = 2) as count_3'''
            self.cursor.execute(statement)
            return self.cursor.fetchone()
        except DataBaseException as e:
            self.conn.rollback()
            log.error(self.mainApp.errorLoggerName, str(e))


if __name__ == '__main__':
    pass
