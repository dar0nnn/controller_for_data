# -*- coding: UTF-8 -*-
import datetime
from db_api import DataBaseApi, connect
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from platform import api, getAgents, nameOfPlatform


class ScalesActionLocal(object):
    def __init__(self):
        self.mainApp = getApplication()
        self.dbAPI = DataBaseApi(connect(self.mainApp.dbip))
        self.dbAPI.createTable()

    def createScaleLocal(self, scaleName):
        '''
        Создает шкалу на локальном узле
        :args scaleName -> string, имя шкалы
        :return True при регистрации, False при неудаче
        '''
        try:
            return self.dbAPI.createScale(scaleName)
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def deleteScaleLocal(self, scaleName):
        '''
        Удаляет шкалу на локальном узле
        :return True при успешном удалении, False при неудаче
        '''
        try:
            return self.dbAPI.deleteScale(scaleName.encode('utf8'))
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def start(self, dt, name):
        '''
        Метод для обращения другого агента с прямым указанием старта шкалы
        :args dt -> datetime, время старта
        :args name -> string, имя шкалы.
        :return True при успешном старте, False при неудаче
        '''
        try:
            localScale = self.dbAPI.searchScale(name)
            if localScale[0][1] == datetime.datetime(1, 1, 1, 0, 0):
                return self.dbAPI.start(dt, name)
            else:
                return False
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def stop(self, dt, name):
        '''
        Метод для обращения другого агента с прямым указанием стопа шкалы
        :args dt -> datetime, время стопа
        :args name -> string, имя шкалы.
        :return True при успешном стопе, False при неудаче
        '''
        try:
            return self.dbAPI.stop(dt, name)
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def updateScale(self, dictAboutScale):
        '''
        Обновляет столбец в базе
        :args dictAboutScale -> dict, ключи 'value', 'column', 'nameOfScale'
        :return True при успешном обновлении, False при неудаче
        '''
        try:
            if self.dbAPI.updateScale(dictAboutScale):
                return True
            else:
                return False
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def searchScale(self, scaleName):
        '''
        Ищет одну, конкретную шкалу шкалу на узле
        :args scaleName -> string, имя шкалы
        :return list of lists, список, внутри шкалы
        '''
        try:
            return self.dbAPI.searchScale(scaleName.encode('utf8'))
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def searchScaleWithLikeLocal(self, scaleName):
        '''
        Метод поиска шкалы по любому количеству знаков на локальном узле. Нужен для searchScaleWithLike
        :args scaleName -> string, имя шкалы или часть имени
        :return list of lists, список, внутри шкалы
        '''
        try:
            return self.dbAPI.searchScaleWithLike(scaleName)
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def countStatusLocal(self):
        '''
        Метод сбора состяний шкал в сети на локальном узле:
        0 - зарегестрирована, 1 - запущена, 2 - остановлена
        :return dictOut -> dict, ключ - имя узла, значение - список, внутри него количество состояний
        [0, 1, 2] шкал.
        '''
        try:
            status = list(self.dbAPI.countStatusLocal())
            status.append(self.mainApp.degradeStatus)
            return {self.mainApp.serverName: status}
        except Exception, e:
            print e
            log.error(self.mainApp.errorLoggerName, str(e))

    def getScalesLocal(self):
        '''
        Собирает шкалы одного, локального узла.
        :return dictOut -> dict ключ имя узла, значение - все шкалы на узле
        '''
        try:
            return {self.mainApp.serverName: self.dbAPI.getScales()}
        except Exception, e:
            log.error(self.mainApp.errorLoggerName, str(e))
