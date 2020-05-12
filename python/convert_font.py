#!/usr/bin/env python3
#encoding=utf-8

from util import TtfConvertor
import TtfConfig

def scan_folders(weight_code, target_path):
    #path="."
    print("Checking path:", target_path)
    tc = TtfConvertor.Convertor()
    file_count = 0
    file_count = tc.convert(target_path, TtfConfig.TtfConfig(weight_code))
    print("Finish!\ncheck file count:%d\n" % (file_count))

if __name__ == '__main__':
    import sys
    argument_count = 3
    if len(sys.argv)==argument_count:
        weight_code = sys.argv[1]
        target_path = sys.argv[2]
        scan_folders(weight_code, target_path)
    else:
        print("Argument must be: %d" % (argument_count -1))
        print("Ex:%s weight_code project.sfdir" % (sys.argv[0]))


