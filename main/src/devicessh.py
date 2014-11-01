import socket
import paramiko
import threading
import Queue
from contextlib import closing
import scpclient
import time
import os
import globalvalue

socket.setdefaulttimeout(1)


def GetTimeString():
    return '(' + time.strftime('%m-%d,%H:%M:%S', time.localtime(time.time())) + '): '


def GetLogFile(ssh, type, ip):
    remotefile = type + '.Log'
    logfile = type + '-' + ip + '.Log'
    command = "if [ -f 'Device_Control/%s/%s' ]; then cat  'Device_Control/%s/%s';else echo 'no logfile'; fi" % (
        type, remotefile, type, remotefile)
    stdin, stdout, stderr = ssh.exec_command(command)
    log = stdout.read().strip("\n")
    if log == 'no logfile':
        return
    else:
        path = os.getcwd()
        workdir = path + os.path.sep + globalvalue.LogPath
        if not os.path.isdir(workdir):
            os.mkdir(workdir)
        os.chdir(workdir)
        with open(logfile, 'w') as f:
            try:
                f.write(log)
            except:
                print 'write log file err.'
            finally:
                f.close()
        os.chdir(path)


class InstallThread(threading.Thread):

    def __init__(self, install_in):
        threading.Thread.__init__(self)
        self.inst_in = install_in
        self.inst_out = globalvalue.QNewReport
        self.out = globalvalue.QInstallReport

    def run(self):
        while globalvalue.RunFlag:
            try:
                task = self.inst_in.get(False)
                if task == 'install over':
                    self.inst_out.put(task)
                    break
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        hostname=task['ip'], port=22, username=task['user'], password=task['passwd'])
                    command = "if [ ! -d 'Device_Control/%s' ]; then mkdir -p 'Device_Control/%s'; fi" % (
                        task['type'], task['type'])
                    ssh.exec_command(command)
                    try:
                        with closing(scpclient.Write(ssh.get_transport(),
                                                     remote_path='~/Device_Control/%s' % (task['type']))) as scp:
                            scp.send_file(task['package'], True)

                        # tar
                        command = "tar xf 'Device_Control/%s/%s' -C Device_Control/%s" % (
                            task['type'], task['tar'], task['type'])
                        ssh.exec_command(command)
                        # script
                        command = "sh 'Device_Control/%s/%s/%s'  %s" % (
                            task['type'], task['path'], task['script'], task['parameter'])
                        stdin, stdout, stderr = ssh.exec_command(command)
                        report = stdout.read().strip("\n")
                        del task['tar']
                        del task['package']
                        del task['script']
                        del task['parameter']
                        del task['path']
                        if report == 'install ok':
                            task['status'] = GetTimeString() + report
                            self.out.put(task)
                        elif report.rstrip() == '':
                            task[
                                'status'] = GetTimeString() + stderr.read().strip("\n")
                        else:
                            task['status'] = GetTimeString() + report
                    except Exception, e:
                        print 'install :scp exec %s' % (task['ip']), e
                        task['status'] = 'execute  err or file not exist'
                except Exception, e:
                    print 'install :ssh %s' % (task['ip']), e
                    task['status'] = 'install err.'
                finally:
                    GetLogFile(ssh, task['type'], task['ip'])
                    ssh.close()
                self.inst_out.put(task)
            except Queue.Empty:
                break
        print 'exitinstall '


class ScanThread(threading.Thread):

    def __init__(self, scan_in):
        threading.Thread.__init__(self)
        self.scan_in = scan_in
        self.scan_out = globalvalue.QNewReport
        self.out = globalvalue.QInstallReport

    # task "{'type':'','ip':'','user':'','passwd':''}"
    def run(self):
        while globalvalue.RunFlag:
            try:
                task = self.scan_in.get(False)
                if task == 'scan over':
                    self.scan_out.put(task)
                    break
                try:
                    testhost = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    testhost.connect((task['ip'], 22))
                    testhost.shutdown
                    testhost.close()
                except:
                    pass
                else:
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(
                            paramiko.AutoAddPolicy())
                        ssh.connect(
                            hostname=task['ip'], port=22, username=task['user'], password=task['passwd'])

                        command = '/sbin/ifconfig -a |grep HWaddr |awk \'{if(NR==1) print $5}\''
                        stdin, stdout, stderr = ssh.exec_command(command)
                        task['mac'] = stdout.read().strip("\n").upper()
                        command = "if [ -f 'Device_Control/%s/%s' ]; then cat  'Device_Control/%s/%s';else echo 'ready'; fi" % (
                            task['type'], task['type'] +
                            globalvalue.StatusSuffix, task['type'],
                            task['type'] + globalvalue.StatusSuffix)
                        stdin, stdout, stderr = ssh.exec_command(command)
                        version = stdout.read().strip("\n")
                        if version != 'ready':
                            try:
                                ver = dict(eval(version))
                                ver = ver.get('Version', '')
                            except:
                                ver = version
                            finally:
                                task['version'] = ver
                                task['status'] = GetTimeString() + 'installed'
                                self.out.put(task)
                        else:
                            task['version'] = ''
                            task['status'] = GetTimeString() + 'ready'
                        self.scan_out.put(task)
                        try:
                            GetLogFile(ssh, task['type'], task['ip'])
                        except Exception, e:
                            print 'scan :get log file err %s' % (task['ip']), e

                    except Exception, e:
                        print 'scan :ssh %s' % (task['ip']), e
                    finally:
                        ssh.close()

            except Queue.Empty:
                break

        print 'exitscan '


class ExecThread(threading.Thread):

    def __init__(self, exec_in):
        threading.Thread.__init__(self)
        self.exec_in = exec_in
        self.out = globalvalue.QInstallReport

    def run(self):
        while globalvalue.RunFlag:
            try:
                task = self.exec_in.get(False)
                if task == 'exec over':
                    self.out.put(task)
                    break
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        hostname=task['ip'], port=22, username=task['user'], password=task['passwd'])

                    command = "sh ./Device_Control/%s/%s/%s %s " % (
                        task['type'], task['path'], task['script'], task['parameter'])
                    stdin, stdout, stderr = ssh.exec_command(command)
                    report = stdout.read().strip("\n")
                    if report == '':
                        report = stderr.read().strip("\n")
                    task['status'] = GetTimeString() + report
                    GetLogFile(ssh, task['type'], task['ip'])
                except Exception, e:
                    print 'exec :ssh %s' % (task['ip']), e
                    task['status'] = GetTimeString() + 'exec err.'
                finally:
                    ssh.close()
                    self.out.put(task)
            except Queue.Empty:
                break
        print 'exit exec'


class DeviceSsh:

    def __init__(self, queue_in=None):
        self.queue_in = queue_in

    def Destroy(self):
        pass
    def threads(self, num, threadfunc, q_in):
        threads_arr = []
        if num > 10:
            for i in range(0, 10):
                threads_arr.append(threadfunc(q_in))
        else:
            for i in range(num):
                threads_arr.append(threadfunc(q_in))
        for t in threads_arr:
            t.setDaemon(True)
            t.start()

    def scan(self, num=10):
        self.threads(num, ScanThread, self.queue_in)

    def install(self, num=10):
        self.threads(
            num, InstallThread, self.queue_in)

    def execScript(self, num=10):
        self.threads(num, ExecThread, self.queue_in)
