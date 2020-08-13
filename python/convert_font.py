#!/usr/bin/env python3
#encoding=utf-8

from util import TtfConvertor
import TtfConfig

def scan_folders(weight_code, target_path, bmp_path):
    #path="."
    print("Checking path:", target_path)
    if len(bmp_path) > 0:
        print("bmp path:", bmp_path)

    tc = TtfConvertor.Convertor()
    file_count = 0
    file_count = tc.convert(target_path, TtfConfig.TtfConfig(weight_code), bmp_path)
    print("Finish!\ncheck file count:%d\n" % (file_count))

if __name__ == '__main__':
    import sys
    argument_count = 3
    if len(sys.argv) >= argument_count:
        weight_code = sys.argv[1]
        target_path = sys.argv[2]
        bmp_path = ""
        if len(sys.argv) >= (argument_count+1):
            bmp_path = sys.argv[3]
        scan_folders(weight_code, target_path, bmp_path)
    else:
        print("Argument must be: %d" % (argument_count -1))
        print("Ex:%s weight_code project.sfdir" % (sys.argv[0]))


