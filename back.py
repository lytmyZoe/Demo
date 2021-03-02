#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time

source = ["/home/shiyanlou/Code/"]
target_dir = "/home/shiyanlou/Desktop/"

target = target_dir + time.strftime('%Y%m%d%H%M%S') + '.zip'

zip_command = "zip -qr %s %s" %(target, ' '.join(source))

if os.system(zip_command) == 0:
    print("Successful backup")
else:
    print("Backup Failed")

