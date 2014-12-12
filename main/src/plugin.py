import os
import tarfile
import json
from copy import deepcopy
import globalvalue

# coding:utf-8
# plugindict={'devicetype':{'user','passwd',}}

class PluginDict():
    def __init__(self):
        self.plugindict = {}
        nowdir = os.getcwd()
        plist = []
        for dirpaths, dirnames, filenames in os.walk(globalvalue.PluginPath):
            if 'plugin.conf' in filenames:
                conf = os.path.join(dirpaths, globalvalue.PluginConfFile)
                with open(conf, 'r') as f:
                    try:
                        str = dict(eval(f.read()))
                        if 'Path' not in str.keys() or str['Path'].replace(' ', '') == '':
                            str['Path'] = dirpaths
                        self.plugindict[str['Device Type']] = str
                    except:
                        pass
                    finally:
                        f.close()

    def GetPlugin(self):
        return self.plugindict

    def GetPluginType(self):
        return self.plugindict.keys()

    def GetPluginInfo(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict.get(type)
        return ''

    def GetPluginUser(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('User', '')
        return ''

    def GetPluginVersion(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('Version', 'Ver 0.0')
        return ''

    def GetPluginPasswd(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('Password', '')
        return ''

    def GetPluginPath(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('Path', '')
        return ''

    def GetPluginPackage(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('Package', '')
        return ''

    def GetPluginSrc(self, type):
        if self.isTypeExist(self.plugindict, type):
            return self.plugindict[type].get('Source', '')
        return ''

    def GetPluginScript(self, type, script):
        if self.isTypeExist(self.plugindict, type):
            plugininfo = self.GetPluginInfo(type)
            if self.isTypeExist(plugininfo, script):
                return self.plugindict[type][script].get('script', '')
        return ''

    def GetPluginParameter(self, type, script):
        if self.isTypeExist(self.plugindict, type):
            plugininfo = self.GetPluginInfo(type)
            if self.isTypeExist(plugininfo, script):
                return self.plugindict[type][script].get('parameter')
        return ''

    def GetPluginConfPath(self, type):
        print self.GetPluginPath(type) + os.path.sep + globalvalue.PluginConfFile
        if self.isTypeExist(self.plugindict, type):
            return self.GetPluginPath(type) + os.path.sep + globalvalue.PluginConfFile
        return ''

    def isTypeExist(self, pdict, type):
        if pdict != None:
            if type in pdict.keys():
                return True
        return False

    def SetPluginConfSave(self, type, user, passwd):
        self.plugindict[type]['User'] = user
        self.plugindict[type]['Password'] = passwd
        with open(self.GetPluginConfPath(type), 'w') as json_file:
            dictconf = deepcopy(self.GetPluginInfo(type))
            del dictconf['Path']
            json_str = json.dumps(dictconf, sort_keys=True, indent=4, separators=(',', ': '))
            json_file.write(json_str)
            json_file.close()
        print json_str

    def PutTarfile(self):
        type = self.GetPluginType()
        path = os.getcwd()
        for item in type:
            os.chdir(path + os.path.sep + self.GetPluginPath(item))
            verfile = self.pluginVerfile(item)
            targz = self.GetPluginPackage(item) + '.tar.gz'
            print targz
            if os.path.isfile(targz):
                os.remove(targz)
                print 'del', targz
            print self.GetPluginPackage(item)
            if not os.path.isdir(self.GetPluginPackage(item)) and not os.path.isfile(self.GetPluginPackage(item)):
                print 'file not exit'
                continue
            with tarfile.open(targz, "w") as tar:
                try:
                    tar.add(self.GetPluginPackage(item))
                    tar.add(verfile)
                except:
                    print 'file err.'
                finally:
                    tar.close()
        os.chdir(path)

    def pluginVerfile(self, type):
        verfile = type + globalvalue.StatusSuffix
        with open(verfile, 'w') as json_file:
            dictconf = {}
            try:
                dictconf['Version'] = self.GetPluginVersion(type)
                json_str = json.dumps(dictconf, sort_keys=True, indent=4, separators=(',', ': '))
                json_file.write(json_str)
            finally:
                json_file.close()
        return verfile