#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import shutil

tmp = 'tmp'
if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        out = open(tmp, 'w')
        for line in f.readlines()[0:-2]:
            out.write(line)
        out.close()
    shutil.move(tmp, sys.argv[1])
