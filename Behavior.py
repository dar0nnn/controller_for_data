# -*- coding: UTF-8 -*-
import datetime
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from platform import api, getAgents, nameOfPlatform


class BehaviorException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        stk = traceback.extract_tb(tb, 1)
        fname = stk[0][2]
        return 'Behavior exception: func name: {}, exception: {}'.format(fname, self.value)


class Behavior(ScalesActionLocal):
    def __init__(self):
        super(Behavior, self).__init__()

    def createScale(self, scaleName):
        '''
        Описывает поведение при регистрации шкалы в системе. Проверяет на ее наличие,
        и создает в системе 2 копии: на локали и на узле, где меньше всего шкал
        :args scaleName -> string, имя шкалы
        :return True при регистрации, False при любом не соблюденном условии
        '''
        try:
            listOut = []
            agents = getAgents()
            for k, v in agents.items():
                searchOut = api(v).searchOneScale(scaleName)
                listOut.extend(searchOut)
            if not listOut:
                try:
                    if api(self.minScales(scaleName, False)).createScaleLocal(scaleName) is True:
                        return self.dbAPI.createScale(scaleName)
                    else:
                        return False
                except AddressError, e:
                    try:
                        return self.dbAPI.createScale(scaleName)
                    except BehaviorException, e:
                        log.error(self.mainApp.errorLoggerName, str(e))
                        return False
            else:
                return False
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def searchScaleWithLike(self, scaleName):
        '''
        Метод поиска шкалы по любому количеству знаков по всей системе
        :args scaleName -> string, имя шкалы или часть имени
        :return dictOut -> dict, ключ имя узла,
        значение - найденные шкалы на узле, удовлетворяющие набору знаков
        '''
        try:
            scaleName = scaleName.encode('utf8')
            dictOut = {}
            agents = getAgents()
            for k, v in agents.items():
                searchOut = api(v).searchScaleLocal(scaleName.encode('utf8'))
                dictOut[k] = searchOut
            dictOut[self.mainApp.serverName] = self.dbAPI.searchScaleWithLike(
                scaleName)
            return dictOut
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def getScales(self):
        '''
        Собирает шкалы со всех узлов.
        :return dictOut -> dict ключ имя узла, значение - все шкалы на узле
        '''
        try:
            dictOut = {}
            agents = getAgents()
            for k, v in agents.items():
                dictOut.update(api(v).getScalesLocal())
            dictOut[self.mainApp.serverName] = self.dbAPI.getScales()
            return dictOut
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def deleteScale(self, scaleName):
        '''
        Удаляет шкалу из системы
        :return True при успешном удалении, False при неудаче
        '''
        try:
            agents = getAgents()
            for v in agents.values():
                api(v).deleteScaleLocal(scaleName)
            return self.dbAPI.deleteScale(scaleName)
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def startScale(self, name):
        '''
        Отвечает за старт таймера шкалы.
        :args name -> string, имя шкалы
        :return True при успешном старте, False при неудаче
        '''

        def _getScaleFromIpStart(name, k):
            try:
                scale = api(k).searchOneScale(name)
                scale[0][2] = None
                local = self.dbAPI.insertScale(tuple(scale[0]))
                return local
            except BehaviorException, e:
                log.error(self.mainApp.errorLoggerName, str(e))

        try:
            dt = datetime.datetime.now()
            name = name.encode('utf8')
            dictOut = {}
            agents = getAgents()
            local = False
            out = False
            for nameOfAgent, ip in agents.items():
                searchOut = api(ip).searchOneScale(name)
                dictOut[ip] = searchOut
            print 'dictOut: ', dictOut
            localScale = self.searchScale(name)
            if dictOut.keys():
                for ip, scales in dictOut.items():
                    print 'her1'
                    if scales:
                        print 'her2', scales
                        for scale in scales:
                            print 'her3', scale
                            if scale[1] == datetime.datetime(1, 1, 1, 0, 0):
                                out = api(ip).start(dt, name)
                                ipWithScale = ip
                    else:
                        out = True
            else:
                out = True
            print 'out: ', out
            if localScale:
                local = self.start(dt, name)
            else:
                if self.mainApp.degradeStatus:
                    local = True
                else:
                    local = _getScaleFromIpStart(name, ipWithScale)
            print 'local: ', local
            if out and local is True:
                return True
            else:
                return False
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def stopScale(self, name):
        '''
        Отвечает за стоп таймера шкалы.
        :args name -> string, имя шкалы
        :return True при успешном стопе, False при неудаче
        '''
        try:
            dt = datetime.datetime.now()
            name = name.encode('utf8')
            dictOut = {}
            agents = getAgents()
            local = False
            out = False
            for k, scales in agents.items():
                searchOut = api(scales).searchScaleLocal(name)
                dictOut[scales] = searchOut
            if dictOut.keys():
                for k, scales in dictOut.items():
                    if scales:
                        for item in scales:
                            if item[2] == datetime.datetime(1, 1, 1, 0, 0):
                                out = api(k).stop(dt, name)
                    else:
                        out = True
            else:
                out = True
            if self.dbAPI.searchScale(name):
                local = self.dbAPI.stop(dt, name)
            if out and local is True:
                return True
            else:
                return False
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def countStatus(self):
        '''
        Метод сбора состяний шкал в сети на всех узлах:
        0 - зарегестрирована, 1 - запущена, 2 - остановлена
        :return dictOut -> dict, ключ - имя узла, значение - список, внутри него количество состояний
        [0, 1, 2] шкал.
        '''
        try:

            dictOut = {}
            agents = getAgents()
            for k, v in agents.items():
                dictOut.update(api(v).countStatusLocal())
            dictOut.update(self.countStatusLocal())
            return dictOut
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def getScaleFromIp(self, name, ip):
        '''
        Метод забирает шкалу с узла в сети себе
        :args name - имя шкалы, ip - ip адресс узла, с которого нужно забрать шкалу. None by default
        :return True при успехе, False при неудаче
        '''
        try:
            if ip != '0':
                scale = api(ip).searchOneScale(name)
                return self.dbAPI.insertScale(tuple(scale[0]))
            else:
                return self.dbAPI.insertScale(name)
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def minScales(self, scaleName, flag=True):
        '''
        Ищет минимально загруженный узел, на котором нет шкалы scaleName
        :args scaleName - имя шкалы
        :return ip адрес узла
        '''
        def _lenScalesFunc(lenScales, name, ip):
            numScales = len(api(ip).getScalesLocal().values()[0])
            lenScales[numScales] = name
            return lenScales

        try:
            lenScales = {}
            agents = getAgents()
            for name, ip in agents.items():
                if api(ip).getDegradeStatus():
                    continue
                if flag:
                    if not api(ip).searchOneScale(scaleName):
                        lenScales = _lenScalesFunc(lenScales, name, ip)
                else:
                    lenScales = _lenScalesFunc(lenScales, name, ip)
            if lenScales.keys():
                minimumScales = min(lenScales.keys())
            return agents[lenScales[minimumScales]]
        except (UnboundLocalError, BehaviorException), e:
            log.error(self.mainApp.errorLoggerName, str(e))
            return False

    def searchScaleList(self, names):
        '''
        Ищет в сети заданные шкалы
        :args names - список имен шкал
        :return Возвращает список, в котором находится список "узел", в котором находятся шкалы. Структура
        вида [ [ [],[],[] ],[ [], [], [] ] ]
        '''
        try:
            listOut = []
            agents = getAgents()
            for name, ip in agents.items():
                if api(ip).getDegradeStatus():
                    continue
                listOut.append(api(ip).searchScaleLocal(names))
            return listOut
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))

    def fullDegradeStart(self):
        '''
        Рассылает локальные шкалы по сети и удаляет их из локальной базы
        :return True при успешной рассылке шкал и удалении их с локали
        '''
        try:
            hostScales = self.getScalesLocal()
            for scale in hostScales.values()[0]:
                scaleName = scale[0]
                ipWhomToSend = self.minScales(scaleName)
                api(ipWhomToSend).getScaleFromIp(scale)
                self.deleteScaleLocal(scaleName)
            return True
        except BehaviorException, e:
            log.error(self.mainApp.errorLoggerName, str(e))
            return False


if __name__ == '__main__':
    pass
