#!/usr/bin/env python3
#encoding=utf-8

import os
import json
import glob

from . import Spline

# for read bmp.
from PIL import Image
#import cv2
import numpy

class Convertor():
    sp = Spline.Spline()
    config = None

    cache_bmp_info_filename = "cache_bmp_info.json"
    cache_bmp_info_filepath = None
    cache_bmp_info_json = {}

    def __init__(self):
        pass

    def get_cache_bmp_filepath(self):
        if self.cache_bmp_info_filepath is None:
            filepath = None
            bmp_path = self.config.BMP_PATH
            if not bmp_path is None:
                if len(bmp_path) > 0:
                    filepath = os.path.join(bmp_path,self.cache_bmp_info_filename)
                    self.cache_bmp_info_filepath = filepath
        return self.cache_bmp_info_filepath

    def open_cache_bmp_json(self):
        filepath = self.get_cache_bmp_filepath()
        #print("open json filepath:", filepath)
        if not filepath is None:
            if os.path.exists(filepath):
                self.cache_bmp_info_json = self.open_json(filepath)

    def open_json(self,filepath):
        dict_data = {}
        with open(filepath, 'r') as read_file:
            dict_data = json.load(read_file)
            read_file.close()
        return dict_data

    def save_cache_bmp_json(self):
        filepath = self.get_cache_bmp_filepath()
        if not filepath is None:
            self.save_json(filepath,self.cache_bmp_info_json)
            #print("save cached result to filepath:", filepath)

    def save_json(self, filepath,json_obj):
        # save to disk.
        json_string = json.dumps(json_obj)
        with open(filepath, 'w') as outfile:
            outfile.write(json_string)
            outfile.close()

    def load_to_memory(self, filename_input):
        # return field.
        stroke_dict = {}
        encoding_string = None
        width_string = None
        
        dot_dict = {}
        dots_array = []
        default_int = -9999

        #print("load to memory, filename_input:", filename_input)
        myfile = open(filename_input, 'r')

        code_encoding_string = 'Encoding: '
        code_encoding_string_length = len(code_encoding_string)

        code_width_string = 'Width: '
        code_width_string_length = len(code_width_string)

        code_begin_string = 'SplineSet'
        code_begin_string_length = len(code_begin_string)

        code_end_string = 'EndSplineSet'
        code_end_string_length = len(code_end_string)

        is_code_flag=False

        stroke_index = 0

        for x_line in myfile:
            if code_encoding_string == x_line[:code_encoding_string_length]:
                encoding_string = x_line[code_encoding_string_length:]

            if code_width_string == x_line[:code_width_string_length]:
                width_string = x_line[code_width_string_length:].strip()

            if not is_code_flag:
                # check begin.

                if code_begin_string == x_line[:code_begin_string_length]:
                    is_code_flag = True
            else:
                # is code start.
                #print("x_line:", x_line)

                if x_line[:1] != ' ':
                    if stroke_index >= 1:
                        stroke_dict[stroke_index]={}
                        stroke_dict[stroke_index]['dots'] = dots_array
                        #if stroke_index == 1:
                            #print("key:", stroke_index, "data:", stroke_dict)
                        
                        # reset new
                        dots_array = []

                    stroke_index += 1

                # check end
                if code_end_string == x_line[:code_end_string_length]:
                    #is_code_flag = False
                    break

                dot_dict = {}

                # type
                t=''
                if ' m ' in x_line:
                    t='m'
                if ' l ' in x_line:
                    t='l'
                if ' c ' in x_line:
                    t='c'
                dot_dict['t']=t

                x=default_int
                y=default_int
                x1=default_int
                y1=default_int
                x2=default_int
                y2=default_int

                # need format code to "ROUND int"
                new_code = ""
                if ' ' in x_line:
                    x_line_array = x_line.split(' ')
                    if t=='m':
                        x=int(float(x_line_array[0]))
                        y=int(float(x_line_array[1]))

                        x_line_array[0]=str(x)
                        x_line_array[1]=str(y)
                        new_code = "%d %d m 1\n" % (x,y)

                    if t=='l':
                        x=int(float(x_line_array[1]))
                        y=int(float(x_line_array[2]))
                        l_type = x_line_array[4].strip()
                        if ',' in l_type:
                            l_type = l_type.split(',')[0]

                        x_line_array[1]=str(x)
                        x_line_array[2]=str(y)
                        new_code = " %d %d l %s\n" % (x,y,l_type)

                    if t=='c':
                        if len(x_line_array) >=7:
                            x=int(float(x_line_array[5]))
                            y=int(float(x_line_array[6]))
                            x1=int(float(x_line_array[1]))
                            y1=int(float(x_line_array[2]))
                            x2=int(float(x_line_array[3]))
                            y2=int(float(x_line_array[4]))

                            x_line_array[1]=str(x1)
                            x_line_array[2]=str(y1)
                            x_line_array[3]=str(x2)
                            x_line_array[4]=str(y2)
                            x_line_array[5]=str(x)
                            x_line_array[6]=str(y)

                            c_type = x_line_array[8].strip()
                            if ',' in c_type:
                                c_type = c_type.split(',')[0]

                            new_code = " %d %d %d %d %d %d c %s\n" % (x1,y1,x2,y2,x,y,c_type)

                    #print("add to code:", x_line)
                    #dot_dict['code'] = x_line
                    # keep extra infomation cause more error.
                    #new_code = ' '.join(x_line_array)
                dot_dict['code'] = new_code

                dot_dict['x']=x
                dot_dict['y']=y

                dot_dict['x1']=x1
                dot_dict['y1']=y1
                dot_dict['x2']=x2
                dot_dict['y2']=y2

                dots_array.append(dot_dict)

        myfile.close()
        return stroke_dict, encoding_string, width_string

    def write_to_file(self, filename_input, stroke_dict, readonly):
        filename_input_new = filename_input + ".tmp"

        myfile = open(filename_input, 'r')
        myfile_new = open(filename_input_new, 'w')
        code_begin_string = 'SplineSet'
        code_begin_string_length = len(code_begin_string)
        code_end_string = 'EndSplineSet'
        code_end_string_length = len(code_end_string)

        is_code_flag=False

        stroke_index = 0
        #print("write_to_file:", filename_input)
        for x_line in myfile:
            #print("x_line:", x_line)
            if not is_code_flag:
                # check begin.

                if code_begin_string == x_line[:code_begin_string_length]:
                    is_code_flag = True
                myfile_new.write(x_line)

            else:
                # check end
                if code_end_string == x_line[:code_end_string_length]:
                    #print("code_end_string:", x_line)

                    is_code_flag = False

                    #flush memory to disk
                    for key in stroke_dict.keys():
                        #print("key:", key)
                        spline_dict = stroke_dict[key]
                        #print("spline_dict:", spline_dict)
                        for dot_dict in spline_dict['dots']:
                            new_line = dot_dict['code']
                            myfile_new.write(new_line)

                    myfile_new.write(x_line)
                    #break

        myfile.close()
        myfile_new.close()

        if not readonly:
            os.remove(filename_input)
            os.rename(filename_input_new, filename_input)

        return stroke_dict

    def convet_font(self, filename_input, final_bmp_path, readonly=False):
        ret = False

        unicode_int = 0
        bmp_image = None
        
        stroke_dict = {}
        encoding_string = None
        stroke_dict, encoding_string, width_string = self.load_to_memory(filename_input)
        
        unicode_int = -1
        if not encoding_string is None:
            if ' ' in encoding_string:
                encoding_string_array = encoding_string.split(' ')
                unicode_string = encoding_string_array[self.config.UNICODE_FIELD-1]
                if len(unicode_string) > 0:
                    unicode_int = int(unicode_string)
                
                is_need_load_bmp = self.config.NEED_LOAD_BMP_IMAGE
                if is_need_load_bmp:
                    if unicode_int <= 0:
                        is_need_load_bmp = False

                    if final_bmp_path is None:
                        is_need_load_bmp = False
                    else:
                        if len(final_bmp_path)<=1:
                            is_need_load_bmp = False

                if is_need_load_bmp:
                    # due to the file count too large.
                    profix_folder = str(unicode_int)[:1]
                    target_folder = os.path.join(final_bmp_path,profix_folder)

                    filename = "U_%s.bmp" % (unicode_int)
                    bmp_path = os.path.join(target_folder, filename)
                    #print("bmp:", bmp_path, ", current gylph:", filename_input)
                    if os.path.exists(bmp_path):
                        # PIL
                        #bmp_image = Image.open(bmp_path)
                        im = Image.open(bmp_path)
                        # numpy
                        bmp_image = numpy.asarray(im)
                        
                        # OpenCV
                        #bmp_image = cv2.imread(bmp_path)
                    else:
                        print("exported image not exist:", bmp_path)
                        pass
        
        width_int = -1
        if len(width_string) > 0:
            width_int = int(width_string)
            #print("glyph width:", width_int)
            if width_int <= 0:
                # do nothing.
                unicode_int = -1

            #if width_int <= 990:
                #unicode_int = -1

        # special range only
        # CJK Radicals Supplement, U+2E80 - U+2EFF
        # 中日韓統一表意文字擴充區A, 3400 – U+4DBF
        # CJK Unified Ideographs, 4E00 - U+9FFF
        # CJK Compatibility Ideographs, U+F900 - U+FAFF
        # 中日韓統一表意文字擴充區B, U+20000 – U+2A6DF
        # 中日韓統一表意文字擴展區G, U+30000 – U+3134F
        #print("unicode_int:", unicode_int)
        convert_range_list = [['2E80','9FFF'],['F900','FAFF'],['20000','3134F']]
        convert_target_range = False
        #convert_target_range = True     # not full scan, debug purpose.
        if convert_target_range:
            is_match_convert_target = False

            for r in convert_range_list:
                if unicode_int >= int(r[0],16) and unicode_int<=int(r[1],16):
                    is_match_convert_target = True
                if is_match_convert_target:
                    break
            #print("is_match_convert_target:", is_match_convert_target)
            if not is_match_convert_target:
                unicode_int = -1

        is_modified = False
        if unicode_int > 0: 
            is_modified, stroke_dict = self.sp.trace(stroke_dict, unicode_int, bmp_image)

        if is_modified:
            if not stroke_dict is None:
                #print("write to file:", filename_input)
                self.write_to_file(filename_input,stroke_dict,readonly)
                stroke_dict = None
                ret = True

        return ret

    def convert(self, path, config, bmp_path):
        self.config = config
        readonly = True     #debug
        readonly = False    #online

        idx=0
        convert_count=0


        final_bmp_path = self.config.BMP_PATH
        # overwrite bmp path by command line.
        if len(bmp_path) > 0:
            final_bmp_path = bmp_path
            # overwrite setting from command line.
            self.config.BMP_PATH = final_bmp_path

        # cache bmp info.
        self.open_cache_bmp_json()

        self.sp.assign_config(self.config)
        self.sp.assign_cache_bmp_info(self.cache_bmp_info_json)

        filename_pattern = path + "/*.glyph"
        for name in glob.glob(filename_pattern):
            idx+=1
            #print(idx,":convert filename:", name)

            # debug single index.
            #if not idx == 19:
                #continue

            #if idx <= 27700:
                #continue

            is_convert = False
            is_convert = self.convet_font(name,final_bmp_path,readonly)
            if is_convert:
                convert_count+=1
                #print("convert list:", name)
            #break
            if idx % 1000 == 0:
                print("Processing:", idx)

            if idx % 4000 == 0:
                self.save_cache_bmp_json()

        # cache bmp info.
        self.save_cache_bmp_json()

        return idx
