#/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2021 movinator (movinator@github.com)
#
# project: support for penta-sata-tower from radxa
# purpose: as radxa uses dependencies that I couldn't port to LE
#          I wrote this class to use gpio through sysfs
import os
import time

class PushButton:
    def __init__(self, pin):
        self.gpio_base    = '/sys/class/gpio'
        self.button_base  = '/sys/class/gpio/gpio' + str(pin)
        self.button_value = self.button_base + '/value'
        if not os.path.exists(self.button_base):
            try:
                f = open(self.gpio_base + '/export', 'w')
                f.write(str(pin))
            except:
                pass


    def get_value(self):
        try:
            with open(self.button_value, 'r') as f:
                v = int(f.read().strip())
        except:
            pass
        return v


    def read_key(self):
        s0 = 1
        while True:
            s0 = self.get_value()
            time.sleep(0.03)
            if not s0:
                break
        t0   = time.time()
        tEnd = t0 + 1.8
        cnt  = 1
        t1   = t0
        t2   = t0
        while t2 < tEnd:
            s1 = self.get_value()
            time.sleep(0.03)
            if s1 != s0:
               s0 = s1
               if s1:
                   t1 = time.time()
               else:
                   cnt += 1
            t2 = time.time()
            if t1 > t0:
                if cnt == 1 and (t2 - t1) > 0.3:
                    return 1
                if cnt > 1 and (t2 - t1) > 0.1 and (t2 - t1) < 0.3 and (t1 - t0) < 0.25:
                    return 2
        if cnt == 1 and not s1:
            return 99
        return 1


if __name__ == '__main__':
    pb = PushButton(146)
    while True:
        k = pb.read_key()
        print('got key-type: ' + str(k))
        time.sleep(1)
