# -*- coding: utf-8 -*-
from Behavior import Behavior
import platform
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from AandD import AandD
from platform import getAgents, api


def fullDegradation(func):
    def wrapper(self, *args):
        if self.mainApp.degradeStatus == 2:
            print 'Node is degrading.'
            return False
        else:
            return func(self, *args)
    return wrapper


class ServerAPI(BaseService):
    def __init__(self):
        super(ServerAPI, self).__init__()
        self.mainApp = getApplication()
        self.mainApp.degradeStatus = 0
        self.behavior = Behavior()
        self.aAndD = AandD()
        agents = self.aAndD.agentListCheck()
        for agent, ip in agents.items():
            api(ip).agentListCheck()

    def makeAPIDeclarations(self):  # Объявление методов API
        self.declareAPI('ServerAPI', (
            'connCheck',
            'createScale',
            'createScaleLocal',
            'searchScale',
            'searchScaleLocal',
            'searchOneScale',
            'getScales',
            'getScalesLocal',
            'updateScale',
            'deleteScale',
            'deleteScaleLocal',
            'startScale',
            'stopScale',
            'countStatus',
            'countStatusLocal',
            'start',
            'stop',
            'getScaleFromIp',
            'agentListCheck',
            'actualization',
            'deathReaction',
            'setDegradeStatus',
            'getDegradeStatus',
        ))

    def connCheck(self):
        print 'conn check'
        return True

    @fullDegradation
    def createScale(self, scaleName):
        if self.mainApp.degradeStatus:
            return False
        temp = self.behavior.createScale(scaleName.encode('utf-8'))
        if temp is True:
            print '{} created'.format(scaleName)
            return True
        else:
            print '{} already exist'.format(scaleName)
            return False

    @fullDegradation
    def createScaleLocal(self, scaleName):
        if self.mainApp.degradeStatus:
            return False
        temp = self.behavior.createScaleLocal(scaleName)
        if temp is True:
            print '{} created'.format(scaleName)
            return True
        else:
            print '{} already exist'.format(scaleName)
            return False

    def searchScale(self, scaleName):
        print 'name or names {} sended'.format(scaleName)
        return self.behavior.searchScaleWithLike(scaleName)

    def searchScaleLocal(self, scaleName):
        print 'found {}'.format(scaleName)
        return self.behavior.searchScaleWithLikeLocal(scaleName)

    def searchOneScale(self, scaleName):
        return self.behavior.searchScale(scaleName)

    def getScales(self):
        print 'scales sended'
        return self.behavior.getScales()

    def getScalesLocal(self):
        print 'scales sended'
        return self.behavior.getScalesLocal()

    @fullDegradation
    def updateScale(self, dictAboutScale):
        self.behavior.updateScale(dictAboutScale)
        print '{} updated'.format(dictAboutScale['nameOfScale'])
        return True

    def deleteScale(self, scaleName):
        delScale = self.behavior.deleteScale(scaleName.encode('utf8'))
        print '{} deleted'.format(scaleName)
        return delScale

    def deleteScaleLocal(self, scaleName):
        if self.behavior.deleteScaleLocal(scaleName.encode('utf8')):
            return True
        else:
            return False

    @fullDegradation
    def startScale(self, scaleName):
        if self.behavior.startScale(scaleName):
            print '{} started'.format(scaleName)
            return True
        else:
            print '{} already started'.format(scaleName)
            return False

    @fullDegradation
    def stopScale(self, scaleName):
        if self.behavior.stopScale(scaleName):
            print '{} stopped'.format(scaleName)
            return True
        else:
            print '{} already stopped'.format(scaleName)
            return False

    def countStatus(self):
        print 'scales status sent'
        return self.behavior.countStatus()

    def countStatusLocal(self):
        print 'test count'
        return self.behavior.countStatusLocal()

    @fullDegradation
    def start(self, dt, name):
        return self.behavior.start(dt, name.encode('utf8'))

    @fullDegradation
    def stop(self, dt, name):
        return self.behavior.stop(dt, name.encode('utf8'))

    @fullDegradation
    def getScaleFromIp(self, name, ip='0'):
        print 'getScaleFromIp'
        return self.behavior.getScaleFromIp(name, ip)

    def searchScaleList(self, names):
        print 'searchScaleList'
        return self.behavior.searchScaleList(names)

    @fullDegradation
    def minScales(self, scaleName):
        print 'minScales'
        return self.behavior.minScales(scaleName)

    @fullDegradation
    def agentListCheck(self):
        try:
            print 'agentListCheck'
            self.aAndD.agentListCheck()
            return True
        except Exception, e:
            print e
            return False

    @fullDegradation
    def actualization(self):
        try:
            print 'actualization'
            self.aAndD.actualization()
            return True
        except Exception, e:
            print e
            return False

    @fullDegradation
    def deathReaction(self):
        try:
            print 'deathReaction'
            self.aAndD.deathReaction()
            return True
        except Exception, e:
            print e
            return False

    def setDegradeStatus(self, degradeStatus):
        try:
            print 'setDegradeStatus'
            self.mainApp.degradeStatus = degradeStatus
            if self.mainApp.degradeStatus == 2:
                self.behavior.fullDegradeStart()
            return True
        except Exception, e:
            print e
            return False

    def getDegradeStatus(self):
        print 'getDegradeStatus'
        return self.mainApp.degradeStatus
