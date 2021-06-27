#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2021 movinator (movinator@github.com)
#
# project: support for penta-sata-tower from radxa
# purpose: helper classes for fan control and button support
import os
import re
import PWM
import time
import syslog
import subprocess

class FanControl:
    def __init__(self, cbcputemp, cbhddtemp, ctemps, htemps, speeds, ne):
        self.cbcpu    = cbcputemp
        self.cbhdd    = cbhddtemp
        self.cputemps = ctemps
        self.hddtemps = htemps
        self.speeds   = speeds
        self.engine   = PWM.PWM(ne)


    def calc_speed(self, temps, temp=100):
        for i in range(len(temps)):
            if temps[i] <= temp:
               return self.speeds[i];
        return 100.0


    def set_speed(self, speed=100):
        self.engine.set_dutycycle(speed)


    def control_loop(self, flag):
        while True:
            if flag.value == 1:
                self.set_speed(100)
            else:
                t0 = self.cbcpu()
                s0 = self.calc_speed(self.cputemps, t0)
                t1 = self.cbhdd()
                s1 = self.calc_speed(self.hddtemps, t1)
                speed = max(s0, s1)
                syslog.syslog('Temperature cpu: ' + str(t0) + ' hdd: ' + str(t1) + '  Fan-speed: ' + str(speed) + '%')
                self.set_speed(speed)
            time.sleep(5)


class Sensor:
    def __init__(self, idsensor):
        self.path = '/sys/class/thermal/thermal_zone' + str(idsensor) + '/temp'


    def path(self):
        return self.path


    def read_temperature(self):
        temp = 0.0
        with open(self.path) as f:
            temp = int(f.read().strip()) / 1000.0
        return temp


class HDD_Temp:
    def __init__(self, path):
        self.p = path


    def path(self):
        return self.p


    def read_temperature(self):
        temp = 0.0
        with open(self.p) as f:
             temp = int(f.read().strip())
        return temp


class HDD_Sensor:
    def __init__(self, path):
        self.p = path


    def path(self):
        return self.p


    def read_temperature(self):
        rv = 0.0
        p  = subprocess.Popen(('/usr/sbin/smartctl', '-A', self.p), stdout=subprocess.PIPE)
        try:
            info  = subprocess.check_output(('/usr/bin/grep', 'Temperature'), stdin=p.stdout)
            parts = re.split('\s+', str(info))
            tmp   = parts[9];
            t     = re.findall("\d+", parts[9].strip())
            rv    = t[0]
        except:
            pass
        return float(rv)


class Config:
    def __init__(self, path):
        self.settings = {}
        self.read_settings(path)


    def read_settings(self, path):
        try:
            f = open(path, 'r')
            for line in f:
                if line[0] == '#':
                    continue
                parts = re.split('\s*=\s*', line)
                if (len(parts) == 2):
                    val = parts[1].strip()
                    if val[0] == '(':
                        self.settings[parts[0].strip()] = []
                        tmp = val[1:len(val)-1]
                        subparts = re.split('\s+', tmp)
                        for sp in subparts:
                            if len(sp) < 1:
                                continue
                            self.settings[parts[0].strip()].append(float(sp))
                    else:
                        self.settings[parts[0].strip()] = val
        except FileNotFound:
            print('missing or invalid config file! [' + str(path) + ']')
        finally:
            f.close()


    def check_ranges(self):
        at0 = self.settings["temperature"]
        at1 = self.settings["hdd-temps"]
        as0 = self.settings["speedfactor"]
        atest = [80.0, 70.0, 60.0, 55.0, 45.0, 38.0, 35.0, 34.0, 30.0, 20.0, 10.0, 0.0]
        for t in atest:
            for i in range(len(at0)):
                if t > at0[i]:
                    print("\tset speed to " + str(as0[i]) + ' for cpu-temp: ' + str(t))
                    break
            for i in range(len(at1)):
                if t > at1[i]:
                    print("\tset speed to " + str(as0[i]) + ' for hdd-temp: ' + str(t))
                    break


    def dump(self):
        for k in self.settings:
            v = self.settings[k]
            if type(v) is list:
                print(k + ' is array: ')
                for e in v:
                    print(e)
            elif type(v) is str:
                print(k + ' => ' + v)
        self.check_ranges()


    def get_cpu_temps(self):
        return self.settings["temperature"]


    def get_hdd_temps(self):
        return self.settings["hdd-temps"]


    def get_speeds(self):
        return self.settings["speedfactor"]


    def get_doubleclick(self):
        return self.settings["doubleclicked"]


    def get_click(self):
        return self.settings["clicked"]


    def get_pressed(self):
        return self.settings["pressed"]


if __name__ == '__main__':
    cfg = Config('/etc/rockpi-sata.conf')
    cfg.dump()
