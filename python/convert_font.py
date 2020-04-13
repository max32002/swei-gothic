#!/usr/bin/env python3
#encoding=utf-8

from util import TtfConvertor
import TtfConfig

def scan_folders(target_path):
    #path="."
    print("Checking path:", target_path)
    tc = TtfConvertor.Convertor()
    file_count = 0
    file_count = tc.convert(target_path, TtfConfig.TtfConfig())
    print("Finish!\ncheck file count:%d\n" % (file_count))

if __name__ == '__main__':
    import sys
    argument_count = 2
    if len(sys.argv)==argument_count:
        target_path = sys.argv[1]
        scan_folders(target_path)
    else:
        print("Argument must be: %d" % (argument_count -1))
        print("Ex:%s project.sfdir" % (sys.argv[0]))


