#!/bin/python
# coding:utf-8

import plugin
import Queue

QNewReport = Queue.Queue()
QInstallReport = Queue.Queue()

RunFlag = True

LogPath = 'log'
PluginPath = 'plugin'

LogSuffix = '.Log'
StatusSuffix = '.Status'

PluginConfFile = 'plugin.conf'

ListTitle = [u'Type', u'Ip', u'User',
             u'Password', u'MAC', u'Status', u'Version']
TaskDict = [u'type', u'ip', u'user', u'passwd',
            u'mac', u'status', u'package', u'tar']
PluginConf = {
    "Device Type": "",
    "Install": {
        "parameter": "",
        "script": ""
    },
    "Uninstall": {
        "parameter": "",
        "script": ""
    },
    "Package": "",
    "Password": "",
    "Start": {
        "parameter": "",
        "script": ""
    },
    "Stop": {
        "parameter": "",
        "script": ""
    },
    "User": "",
    "Version": ""
}
Plugin = plugin.PluginDict()
