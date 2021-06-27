#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2021 movinator (movinator@github.com)
#
# project: support for penta-sata-tower from radxa
# purpose: as radxa uses dependencies that I couldn't port to LE
#          I wrote this class to use hardware pwm for controlling fan speed
import os
import time

class PWM:
    def __init__(self, chipnum):
        self.pwm_base   = '/sys/class/pwm/pwmchip' + str(chipnum);
        self.pwm_engine = self.pwm_base   + '/pwm0'
        self.pwm_flag   = self.pwm_base   + '/export'
        self.pwm_enable = self.pwm_engine + '/enable'
        self.pwm_pol    = self.pwm_engine + '/polarity'
        self.pwm_period = self.pwm_engine + '/period'
        self.pwm_duty   = self.pwm_engine + '/duty_cycle'
        while not os.path.exists(self.pwm_engine):
              try:
                  with open(self.pwm_flag, 'w') as f:
                      f.write('0')
              except:
                  pass
              time.sleep(1)
        if self.is_enabled():
            self.set_enabled(False)
        self.set_period(50005)
        self.set_polarity()
        self.set_dutycycle(100)
        self.set_enabled(True)
        time.sleep(5)


    def is_enabled(self):
        try:
            with open(self.pwm_enable, 'r') as f:
                enabled = int(f.read().strip())
        except:
            pass
        return enabled


    def set_enabled(self, enable = True):
        try:
            with open(self.pwm_enable, 'w') as f:
                if enable:
                   f.write('1')
                else:
                   f.write('0')
        except:
            pass


    def set_polarity(self, p=True):
        try:
            with open(self.pwm_pol, 'w') as f:
                if p:
                    f.write('normal')
                else:
                    f.write('inversed')
        except:
            pass


    def set_period(self, p=100000):
        self.period = int(0.95 * p)
        try:
            with open(self.pwm_period, 'w') as f:
                f.write(str(p))
        except:
            pass


    def get_period(self):
        try:
            with open(self.pwm_period, 'r') as f:
                p = int(f.read().strip())
        except:
            pass
        return p


    def set_dutycycle(self, d=100.0):
        duty = int(self.period / 100.0 * float(d));
        try:
            with open(self.pwm_duty, 'w') as f:
                f.write(str(duty))
        except:
            pass


if __name__ == '__main__':
    pwm = PWM(1)
    pwm.set_dutycycle(50)
