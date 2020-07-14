#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util

import os
import cv2
import numpy as np

class Rule():
    config = None
    unicode_int = -1
    bmp_image = None
    bmp_x_offset = 0
    bmp_y_offset = 0

    def __init__(self):
        pass

    def assign_unicode(self, val):
        self.unicode_int = val

    # 0-24F
    def is_Latin(self):
        ret = False
        if self.unicode_int > 0:
            if self.unicode_int <= 591:
                ret = True
        return ret

    # Hangul Syllables, U+AC00 - U+D7AF[3]
    def is_Hangul(self):
        ret = False
        if self.unicode_int > 0:
            if self.unicode_int >= 44032 and self.unicode_int <= 55215:
                ret = True
        return ret

    def assign_x_offset(self, offset):
        self.bmp_x_offset = offset

    def assign_y_offset(self, offset):
        self.bmp_y_offset = offset

    def ff_x_to_bmp_x(self, x):
        return x + self.bmp_x_offset

    def ff_y_to_bmp_y(self, y):
        FF_TOP = 900
        top = FF_TOP - self.bmp_y_offset
        return top + (y * -1)

    def get_mask_array(self, x1, y1, x2, y2, x3, y3, x4=None, y4=None):
        bmp_x1 = self.ff_x_to_bmp_x(x1)
        bmp_y1 = self.ff_y_to_bmp_y(y1)
        bmp_x2 = self.ff_x_to_bmp_x(x2)
        bmp_y2 = self.ff_y_to_bmp_y(y2)
        bmp_x3 = self.ff_x_to_bmp_x(x3)
        bmp_y3 = self.ff_y_to_bmp_y(y3)
        
        poly_array=[[bmp_x1,bmp_y1],[bmp_x2,bmp_y2],[bmp_x3,bmp_y3]]


        bmp_x4 = None
        bmp_y4 = None
        if not x4 is None and not y4 is None:
            bmp_x4 = self.ff_x_to_bmp_x(x4)
            bmp_y4 = self.ff_y_to_bmp_y(y4)
            poly_array.append([bmp_x4,bmp_y4])
        #print("bmp coordinate x,y to x,y",bmp_x1,bmp_y1,bmp_x2,bmp_y2,bmp_x3,bmp_y3,bmp_x4,bmp_y4)

        # create mask with zeros

        mask = np.zeros((self.bmp_image.shape), dtype=np.uint8)
        mask_value = (128,128,128)

        pts = np.array( [poly_array], dtype=np.int32 )
        cv2.fillPoly(mask, pts, mask_value )

        # get color values
        image = self.bmp_image
        values = image[np.where((mask == mask_value).all(axis=2))]
        #print(values)

        return values

    # test triangle but only near center conver pixels.
    # Save resule to cache.
    # PS: x2,y2 is center coordinate.
    def test_inside_coner(self, x1, y1, x2, y2, x3, y3, coner_offset, inside_stroke_dict, debug_mode = False):
        previous_x,previous_y=spline_util.two_point_extend(x1,y1,x2,y2,-1 * coner_offset)
        next_x,next_y=spline_util.two_point_extend(x3,y3,x2,y2,-1 * coner_offset)
        inside_stroke_key = "%d,%d_%d,%d_%d,%dx%d" % (previous_x, previous_y, x1, y1, next_x, next_y, coner_offset)
        if inside_stroke_key in inside_stroke_dict:
            inside_stroke_flag = inside_stroke_dict[inside_stroke_key]
        else:
            # start to parse.
            inside_stroke_flag = self.is_inside_triangle(previous_x,previous_y,x2,y2,next_x,next_y, debug_mode=debug_mode)
        return inside_stroke_flag,inside_stroke_dict

    # for triangle
    # only test center point.
    def is_inside_triangle(self, x1, y1, x2, y2, x3, y3, debug_mode=False):
        ret = True

        if not self.bmp_image is None:
            h,w = self.bmp_image.height,self.bmp_image.width
            margin=5
            left=0+margin
            top=0
            right=w-margin
            bottom=h-margin

            center_x = int((x1+x3)/2)
            center_y = int((y1+y3)/2)

            bmp_x = self.ff_x_to_bmp_x(center_x)
            bmp_y = self.ff_y_to_bmp_y(center_y)

            if bmp_x <= left:
                bmp_x = left
            if bmp_x >= right:
                bmp_x = right
            if bmp_y <= top:
                bmp_y = top
            if bmp_y >= bottom:
                bmp_y = bottom

            data=self.bmp_image.getpixel((bmp_x, bmp_y))

            if debug_mode:
                print("center_x,y:",center_x,center_y)
                print("bmp_x,y:",bmp_x,bmp_y)
                print("bmp x_offset:", self.bmp_x_offset)
                print("bmp y_offset:", self.bmp_y_offset)
                print("data:", data)

            if data>=128:
                ret=False
        else:
            #print("bmp is None!")
            pass
        return ret

    # for triangle
    def is_inside_triangle_cv(self, x1, y1, x2, y2, x3, y3):
        ret = True

        if not self.bmp_image is None:
            values = self.get_mask_array(x1, y1, x2, y2, x3, y3)
            #print("values:", values)

            flag_avg = 0.0
            flag_total = 0

            idx=0
            for item in values:
                idx += 1
                flag = 1
                if item[0]==0:
                    flag = 0
                flag_total += flag

            if idx > 0:
                flag_avg = flag_total / idx
                if flag_avg > 0.5:
                    ret = False
            else:
                #print("not pixel selected!")
                pass
        else:
            #print("bmp is None!")
            pass
        return ret

    # for rectangle
    # threshold more lower, means more easy to become stroke, maybe for thin or extra-light style.
    def is_inside_stroke(self, x1, y1, x2, y2, x3, y3, x4, y4, threshold=0.5):
        ret = False

        #bmp_x1 = self.ff_x_to_bmp_x(x1)
        #bmp_y1 = self.ff_y_to_bmp_y(y1)
        #bmp_x2 = self.ff_x_to_bmp_x(x2)
        #bmp_y2 = self.ff_y_to_bmp_y(y2)
        #bmp_x3 = self.ff_x_to_bmp_x(x3)
        #bmp_y3 = self.ff_y_to_bmp_y(y3)
        #bmp_x4 = self.ff_x_to_bmp_x(x4)
        #bmp_y4 = self.ff_y_to_bmp_y(y4)
        #print("bmp coordinate x,y to x,y",bmp_x1,bmp_y1,bmp_x2,bmp_y2,bmp_x3,bmp_y3,bmp_x4,bmp_y4)

        if not self.bmp_image is None:
            #diff_x = x2-x1
            #diff_y = y2-y3
            #print("diff_x:", diff_x)
            #print("diff_y:", diff_y)

            values = self.get_mask_array(x1, y1, x2, y2, x3, y3, x4, y4)

            flag_avg = 0.0
            flag_total = 0

            idx=0
            for item in values:
                idx += 1
                if item[0]==0:
                    # match black point.
                    flag_total += 1

            if idx > 0:
                # avg is for black point.
                flag_avg = flag_total / idx

                #print("count:", idx)
                #print("total:", flag_total)
                #print("average:", flag_avg)

                #np_re = np.array(values_formated)
                #np2 = np_re.reshape([diff_x+1,diff_y+1])
                #print("np2:", np2)

                # avg higher, means more white point.
                if flag_avg > threshold:
                    ret = True
        return ret


    # purpose: check is join line.
    #  return:  True, 是中間的交叉線。
    #           False, 角落轉彎線。
    #      PS:  使用原理是檢查white dot
    def join_line_check(self,x0,y0,x1,y1,x2,y2, debug_mode=False):
        is_join_line_flag = False

        if self.bmp_image is None:
            # 沒圖，假設是線條吧，呵呵
            is_join_line_flag = True
        else:
            coner_offset = 10

            if debug_mode:
                filename = "U_%s.bmp" % (self.unicode_int)
                bmp_path = os.path.join(self.config.BMP_PATH, filename)
                print("bmp_path:", bmp_path)
                print("image file:")
                print("test coordinate:", x0,y0, "-" , x1,y1, "-", x2,y2)

            # prepare the get-pixel environment.
            # get stroke width #1
            next_x,next_y=spline_util.two_point_extend(x2,y2,x1,y1, -1 * coner_offset)
            if debug_mode:
                print("next_x,next_y:", next_x,next_y)

            # 取 stroke width 前，因 bmp 偏移，會造成誤判。需要往第3點偏移。
            next_offset_stroke_width_x = next_x-x1
            next_offset_stroke_width_y = next_y-y1

            stroke_width_lower = self.get_stroke_width(x0+next_offset_stroke_width_x,y0+next_offset_stroke_width_y,x1+next_offset_stroke_width_x,y1+next_offset_stroke_width_y)
            if debug_mode:
                print("offset_stroke_width_x,y:", next_offset_stroke_width_x, next_offset_stroke_width_y)
                print("stroke_width test offset:", x0+next_offset_stroke_width_x,y0+next_offset_stroke_width_y,x1+next_offset_stroke_width_x,y1+next_offset_stroke_width_y)
                print("stroke_width_lower:", stroke_width_lower)

            # get stroke width #2
            previous_x,previous_y=spline_util.two_point_extend(x0,y0,x1,y1, -1 * coner_offset)
            if debug_mode:
                print("previous_x,previous_y:", previous_x,previous_y)

            # 取 stroke width 前，因 bmp 偏移，會造成誤判。需要往第3點偏移。
            previous_offset_stroke_width_x = previous_x-x1
            previous_offset_stroke_width_y = previous_y-y1
            if debug_mode:
                print("offset_stroke_width_x,y:", previous_offset_stroke_width_x, previous_offset_stroke_width_y)

            stroke_width_upper = self.get_stroke_width(x2+previous_offset_stroke_width_x,y2+previous_offset_stroke_width_y,x1+previous_offset_stroke_width_x,y1+previous_offset_stroke_width_y)
            if debug_mode:
                print("stroke_width test offset:", x2+previous_offset_stroke_width_x,y2+previous_offset_stroke_width_y,x1+previous_offset_stroke_width_x,y1+previous_offset_stroke_width_y)
                print("stroke_width_upper:", stroke_width_upper)
            
            # for case: 「屰」線的上方有線，造成取stroke width 取出為最大值。
            if stroke_width_upper >= self.config.STROKE_WIDTH_AVERAGE:
                stroke_width_upper = self.config.STROKE_WIDTH_AVERAGE


            # test range margin.
            h,w = self.bmp_image.height,self.bmp_image.width
            margin=5
            left=0+margin
            top=0
            right=w-margin
            bottom=h-margin

            # get offset to the stroke inside.
            # 「縏」的「又」，在 0.5 會 fail.
            UPPER_STROKE_OFFSET_RATE = 0.6
            next_extend_x,next_extend_y=spline_util.two_point_extend(x2,y2,x1,y1, int(stroke_width_upper * UPPER_STROKE_OFFSET_RATE))
            next_extend_x_offset = x1-next_extend_x
            next_extend_y_offset = y1-next_extend_y

            # all test should be in-stroke
            found_white_dot = False

            LOWER_STROKE_OFFSET_RATE = 1.2
            stroke_test_end = int(stroke_width_lower * 0.95)
            stroke_test_begin = int(stroke_width_lower * LOWER_STROKE_OFFSET_RATE)
            if debug_mode:
                print("stroke_test_end:", stroke_test_end)
                print("stroke_test_begin:", stroke_test_begin)
                pass

            for idx in range(stroke_test_end,stroke_test_begin):
                previous_extend_x,previous_extend_y = spline_util.two_point_extend(x0,y0,x1,y1, idx)
                test_x = previous_extend_x - next_extend_x_offset
                test_y = previous_extend_y - next_extend_y_offset

                bmp_x = self.ff_x_to_bmp_x(test_x)
                bmp_y = self.ff_y_to_bmp_y(test_y)

                if bmp_x <= left:
                    bmp_x = left
                if bmp_x >= right:
                    bmp_x = right
                if bmp_y <= top:
                    bmp_y = top
                if bmp_y >= bottom:
                    bmp_y = bottom
                if debug_mode:
                    print("test_x,y:", test_x, test_y)
                    print("bmp_x,y:",bmp_x,bmp_y)
                    pass
                data=self.bmp_image.getpixel((bmp_x, bmp_y))
                if debug_mode:
                    print("data:", data)
                    pass
                if data >=128:
                    if debug_mode:
                        print("found white dot.")
                        pass
                    found_white_dot = True
                    break

            if not found_white_dot:
                # whole is black.
                is_join_line_flag = True

            # alternate solution, not used, now.
            #is_join_line_flag = self.is_inside_stroke(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4)
            #print("is_join_line_flag:",is_join_line_flag)

        return is_join_line_flag

    def get_stroke_width(self,x0,y0,x1,y1):
        stroke_width=0

        if not self.bmp_image is None:
            h,w = self.bmp_image.height, self.bmp_image.width
            margin=5
            left=0+margin
            top=0
            right=w-margin
            bottom=h-margin
            #print("margin:",top,left,right,bottom)
            #print("get_stroke_width:",x0,y0,x1,y1)
            
            # min stroke is excepted.
            STROKE_MATCH_MIN = 25

            # test begin with counter.
            STROKE_TEST_BEGIN = 10

            stroke_count = STROKE_TEST_BEGIN

            black_dot_count = 0
            for idx in range(STROKE_TEST_BEGIN, self.config.STROKE_WIDTH_MAX):
                test_x,test_y = spline_util.two_point_extend(x0,y0,x1,y1,idx)
                #print("extend:", idx, "test_x,y:",test_x,test_y)

                bmp_x = self.ff_x_to_bmp_x(test_x)
                bmp_y = self.ff_y_to_bmp_y(test_y)
                #print("bmp_x,y:",bmp_x,bmp_y)

                if bmp_x <= left:
                    break
                if bmp_x >= right:
                    break
                if bmp_y <= top:
                    break
                if bmp_y >= bottom:
                    break

                data=self.bmp_image.getpixel((bmp_x, bmp_y))
                #print("data:", data)
                if data <=128:
                    black_dot_count +=1

                # 功成身退了，感謝你的努力。
                if black_dot_count >= STROKE_MATCH_MIN and data >=128:
                    break

                # 試了一半，還是沒資料，就放棄吧。
                if black_dot_count == 0 and idx >= (self.config.STROKE_WIDTH_MAX/2):
                    break

                stroke_count +=1

            if stroke_count >= STROKE_MATCH_MIN:
                stroke_width = stroke_count

        return stroke_width


    # purpose: check is join line.
    def join_line_check_cv(self,x0,y0,x1,y1,x2,y2):
        inside_stroke_flag = False

        # try to cross a stroke. 新位置右下。RB (Begin point)
        previous_extend_x,previous_extend_y = spline_util.two_point_extend(x0,y0,x1,y1, self.config.STROKE_WIDTH_AVERAGE)
        previous_extend_x_offset = x1-previous_extend_x
        previous_extend_y_offset = y1-previous_extend_y

        #print("previous_extend_x_offset:", previous_extend_x_offset)
        #print("previous_extend_y_offset:", previous_extend_y_offset)

        # 新位置，左下. LB
        previous_left_x,previous_left_y = spline_util.two_point_extend(x0,y0,x1,y1, int(2.0 *self.config.STROKE_WIDTH_AVERAGE))
        
        # 新位置，右上. RT (Endding point)
        tmp_next_extend_x,tmp_next_extend_y=spline_util.two_point_extend(x2,y2,x1,y1, self.config.STROKE_WIDTH_AVERAGE)
        next_extend_x = tmp_next_extend_x - previous_extend_x_offset
        next_extend_y = tmp_next_extend_y - previous_extend_y_offset

        # 新位置，左上. 
        next_left_x = next_extend_x - previous_extend_x_offset
        next_left_y = tmp_next_extend_y - previous_extend_y_offset -previous_extend_y_offset

        bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4 = previous_extend_x, previous_extend_y, previous_left_x, previous_left_y, next_left_x, next_left_y, next_extend_x, next_extend_y
        #print("check block:\nx,y1 = %d,%d\nx,y2 = %d,%d\nx,y3 = %d,%d\nx,y4 = %d,%d" % (bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4))
        inside_stroke_flag = self.is_inside_stroke(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4)
        #print("inside_stroke_flag:",inside_stroke_flag)

        return inside_stroke_flag

    def assign_config(self, config):
        self.config = config

    def assign_bmp(self, bmp, x_offset=0, y_offset=0):
        self.bmp_image = bmp
        self.bmp_x_offset = x_offset
        self.bmp_y_offset = y_offset

    
    def reset_first_point(self, format_dict_array, spline_dict):
        spline_x = spline_dict['dots'][0]['x']
        spline_y = spline_dict['dots'][0]['y']
        spline_t = 'm'
        spline_code = spline_dict['dots'][0]['code']

        nodes_length = len(format_dict_array)
        # [IMPORTANT] data in "format_dict_array" are not CLEAN! 
        # please compute data from code.
        old_code = format_dict_array[nodes_length-1]['code']
        old_code_array = old_code.split(' ')
        if ' c ' in old_code:
            last_x = int(float(old_code_array[5]))
            last_y = int(float(old_code_array[6]))
        else:
            last_x = int(float(old_code_array[1]))
            last_y = int(float(old_code_array[2]))

        #print("original x,y:", spline_x,"-",spline_y,", transformed last x,y=",last_x,"-",last_y)
        if not(spline_x==last_x and spline_y==last_y):
            #print("not match!")
            #print("m old_code_string:", spline_code)
            
            old_code_array = spline_code.split(' ')
            old_code_array[0] = str(last_x)
            old_code_array[1] = str(last_y)
            
            # keep extra infomation cause more error.
            #new_code = ' '.join(old_code_array)
            new_code = "%d %d m 1\n" % (last_x, last_y)

            spline_x = last_x
            spline_y = last_y
            spline_code = new_code
            #print("new code:", spline_code)

        #print("\n\nbefore:", format_dict_array)
        dot_dict={}
        dot_dict['x']=spline_x
        dot_dict['y']=spline_y
        dot_dict['t']=spline_t
        dot_dict['code']=spline_code
        format_dict_array.insert(0,dot_dict)
        #print("\n\nafter:", format_dict_array)
        spline_dict['dots'] = format_dict_array


    # purpose: apply new value to dict from code.
    #        : for only update specific index only.
    def apply_code(self, format_dict_array, idx):
        code = format_dict_array[idx]['code']
        # type
        t=''
        if ' m ' in code:
            t='m'
        if ' l ' in code:
            t='l'
        if ' c ' in code:
            t='c'

        old_code_array = code.split(' ')
        if t=='c':
            format_dict_array[idx]['x1']=int(float(old_code_array[1]))
            format_dict_array[idx]['y1']=int(float(old_code_array[2]))
            format_dict_array[idx]['x2']=int(float(old_code_array[3]))
            format_dict_array[idx]['y2']=int(float(old_code_array[4]))
            format_dict_array[idx]['x']=int(float(old_code_array[5]))
            format_dict_array[idx]['y']=int(float(old_code_array[6]))
        else:
            format_dict_array[idx]['x']=int(float(old_code_array[1]))
            format_dict_array[idx]['y']=int(float(old_code_array[2]))

    # purpose: get current index distance,
    #        : for only update specific index only.
    def current_distance(self, format_dict_array, idx):
        nodes_length = len(format_dict_array)
        next_index = (idx+1)%nodes_length
        current_x = format_dict_array[idx]['x']
        current_y = format_dict_array[idx]['y']
        next_x = format_dict_array[next_index]['x']
        next_y = format_dict_array[next_index]['y']
        distance = spline_util.get_distance(current_x,current_y,next_x,next_y)
        return distance

    def caculate_distance(self, format_dict_array):
        nodes_length = len(format_dict_array)
        for idx in range(nodes_length):
            next_index = (idx+1)%nodes_length

            # It's easy to forget to fill attrib!
            # restore value from code.
            self.apply_code(format_dict_array,idx)

            current_x = format_dict_array[idx]['x']
            current_y = format_dict_array[idx]['y']

            next_x = format_dict_array[next_index]['x']
            next_y = format_dict_array[next_index]['y']
            distance = spline_util.get_distance(current_x,current_y,next_x,next_y)
            format_dict_array[idx]['distance']=distance

            format_dict_array[idx]['match_stroke_width'] = False
            if distance >= self.config.STROKE_WIDTH_MIN and distance <= self.config.STROKE_WIDTH_MAX:
                format_dict_array[idx]['match_stroke_width'] = True

            format_dict_array[idx]['x_direction']=0
            if next_x > current_x:
                format_dict_array[idx]['x_direction']=1
            if next_x < current_x:
                format_dict_array[idx]['x_direction']=-1

            format_dict_array[idx]['y_direction']=0
            if next_y > current_y:
                format_dict_array[idx]['y_direction']=1
            if next_y < current_y:
                format_dict_array[idx]['y_direction']=-1

            # 有誤差地判斷，與下一個點是否為平行線。
            EQUAL_ACCURACY = self.config.EQUAL_ACCURACY_PERCENT * distance
            if EQUAL_ACCURACY <= self.config.EQUAL_ACCURACY_MIN:
                EQUAL_ACCURACY = self.config.EQUAL_ACCURACY_MIN
            format_dict_array[idx]['x_equal_fuzzy']=False
            if abs(next_x - current_x) <= EQUAL_ACCURACY:
                format_dict_array[idx]['x_equal_fuzzy']=True

            format_dict_array[idx]['y_equal_fuzzy']=False
            if abs(next_y - current_y) <= EQUAL_ACCURACY:
                format_dict_array[idx]['y_equal_fuzzy']=True

        return format_dict_array


    # for triangle version, ex: rule#5
    def make_coner_curve(self,round_offset,format_dict_array,idx,skip_coordinate_rule):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']

        # save orginal value
        orig_x0 = x0
        orig_y0 = y0
        orig_x2 = x2
        orig_y2 = y2

        # 這是較佳的長度，但是可能會「深入」筆畫裡。
        # 使用較短的邊。
        round_length_1 = round_offset
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_offset:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        round_length_2 = round_offset
        if format_dict_array[(idx+1)%nodes_length]['distance'] < round_offset:
            round_length_2 = format_dict_array[(idx+1)%nodes_length]['distance']

        #if True:
        if False:
            print("round_offset:",round_offset)
            print("round_length_1:",round_length_1)
            print("round_length_2:",round_length_2)

        # use more close coordinate.
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x0
            y_from = y0
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x1,y1,round_length_1)

        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+2)%nodes_length]['x1']
            y_center = format_dict_array[(idx+2)%nodes_length]['y1']
            x2,y2 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x1,y1,round_length_2)
        
        #if True:
        if False:
            print("orig x0,y0,x1,y1,x2,y2:", orig_x0,orig_y0,x1,y1,orig_x2,orig_y2)
            print("new x0,y0,x1,y1,x2,y2:", x0,y0,x1,y1,x2,y2)


        previous_x,previous_y=spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
        next_x,next_y=spline_util.two_point_extend(x2,y2,x1,y1,-1 * round_length_2)

        previous_x_offset = x1 - previous_x
        previous_y_offset = y1 - previous_y

        # stronge version
        curve_version = 1
        previous_recenter_x,previous_recenter_y=x1,y1
        next_recenter_x,next_recenter_y=x1,y1

        # make curve more "SOFT"
        #curve_version = 2
        if curve_version==2:
            previous_recenter_x = int((previous_x + x1)/2)
            previous_recenter_y = int((previous_y + y1)/2)

            next_recenter_x = int((next_x + x1)/2)
            next_recenter_y = int((next_y + y1)/2)

        # update 1
        format_dict_array[(idx+1)%nodes_length]['x']= previous_x
        format_dict_array[(idx+1)%nodes_length]['y']= previous_y

        old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
        old_code_array = old_code_string.split(' ')
        
        if format_dict_array[(idx+1)%nodes_length]['t']=="c":
            # 內縮，造成奇怪的曲線。
            #print("x,y:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'])
            #print("old distance:", format_dict_array[(idx+1)%nodes_length]['distance'])
            new_distance = spline_util.get_distance(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],previous_x,previous_y)
            #print("new distance:", new_distance)

            is_convert_to_l = False

            if new_distance <= 40:
                is_convert_to_l = True

            if is_convert_to_l:
                format_dict_array[(idx+1)%nodes_length]['t']="l"
                tmp_code_string = ' %d %d l 1\n' % (previous_x,previous_y)
                old_code_array = tmp_code_string.split(' ')
            else:
                # for case 「㐉」的丁.
                # 如果 x1,y1=x,y, 順便調整另一組。
                if old_code_array[1] == old_code_array[5] and old_code_array[2] == old_code_array[6]:
                    old_code_array[1] = str(previous_x)
                    old_code_array[2] = str(previous_y)

                is_virtual_dot_need_offset = False
                #is_virtual_dot_need_offset = True

                if is_virtual_dot_need_offset:
                    # 套用修改前，如果 x1,y1=x2,y2, 順便調整另一組。
                    if old_code_array[1] == old_code_array[3] and old_code_array[2] == old_code_array[4]:
                        #print("match x1,y1=x2,y2:", old_code_string)
                        old_code_array[1] = str(int(float(old_code_array[3]))-previous_x_offset)
                        old_code_array[2] = str(int(float(old_code_array[4]))-previous_y_offset)

                    old_code_array[3] = str(int(float(old_code_array[3]))-previous_x_offset)
                    old_code_array[4] = str(int(float(old_code_array[4]))-previous_y_offset)

                old_code_array[5] = str(previous_x)
                old_code_array[6] = str(previous_y)
        else:
            # l
            old_code_array[1] = str(previous_x)
            old_code_array[2] = str(previous_y)
        new_code = ' '.join(old_code_array)
        # only need update code, let formater to re-compute.
        format_dict_array[(idx+1)%nodes_length]['code'] = new_code
        self.apply_code(format_dict_array,(idx+1)%nodes_length)
        #print("old +1 code:", old_code_string)
        #print("update +1 code:", new_code)

        if old_code_string in skip_coordinate_rule:
            skip_coordinate_rule.append(new_code)


        # update [next next curve]
        if format_dict_array[(idx+2)%nodes_length]['t']=="c":
            old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
            old_code_array = old_code_string.split(' ')

            new_distance = spline_util.get_distance(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],next_x,next_y)
            distance_lost = format_dict_array[(idx+1)%nodes_length]['distance'] - new_distance

            is_convert_to_l = False

            if new_distance <= 40:
                is_convert_to_l = True

            #print("old distance:", format_dict_array[(idx+1)%nodes_length]['distance'])
            #print("new distance:", new_distance)
            #print("distance_lost:", distance_lost)
            #print("is_convert_to_l:",is_convert_to_l)
            
            if is_convert_to_l:
                format_dict_array[(idx+2)%nodes_length]['t']="l"
                tmp_code_string = ' %d %d l 1\n' % (format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                old_code_array = tmp_code_string.split(' ')
            else:
                # 為了和共用的 code 套用，使用相同的變數名稱。
                x2_offset = next_x - x1
                y2_offset = next_y - y1
                orig_x3 = orig_x2
                orig_y3 = orig_y2

                # 內縮，造成奇怪的曲線。
                # strong offset
                extend_offset_x = int(old_code_array[1])+ int(x2_offset/1)
                extend_offset_y = int(old_code_array[2])+ int(y2_offset/1)
                
                # soft offset
                #extend_offset_x = int(float(old_code_array[1]))+ int(x2_offset/2)
                #extend_offset_y = int(float(old_code_array[2]))+ int(y2_offset/2)

                #if True:
                if False:
                    print("orig xy3:", orig_x3, orig_y3)
                    print("xy2 offset:", x2_offset, y2_offset)

                virtal_distance = spline_util.get_distance(x1,y1,next_x,next_y)
                x1y1_distance = spline_util.get_distance(x1,y1,int(old_code_array[1]),int(old_code_array[2]))
                
                is_virtual_dot_need_offset = False
                #is_virtual_dot_need_offset = True
                if x1y1_distance <= int(virtal_distance * 1.0):
                    is_virtual_dot_need_offset = True

                #print("virtual distance:", virtal_distance)
                #print("x1y1 distance:", x1y1_distance)
                #print("is_virtual_dot_need_offset:",is_virtual_dot_need_offset)
                if is_virtual_dot_need_offset:
                    # 套用修改前，如果 x1,y1=x2,y2, 順便調整另一組。
                    if old_code_array[1] == old_code_array[3] and old_code_array[2] == old_code_array[4]:
                        #print("match x1,y1=x2,y2:", old_code_string)
                        old_code_array[3] = str(extend_offset_x)
                        old_code_array[4] = str(extend_offset_y)

                    old_code_array[1] = str(extend_offset_x)
                    old_code_array[2] = str(extend_offset_y)

            new_code = ' '.join(old_code_array)
            format_dict_array[(idx+2)%nodes_length]['code'] = new_code
            #print("old +2 code:", old_code_string)
            #print("update +2 code:", new_code)
            self.apply_code(format_dict_array,(idx+2)%nodes_length)

            if old_code_string in skip_coordinate_rule:
                skip_coordinate_rule.append(new_code)

        # append new #2
        # strong version
        #new_code = ' %d %d %d %d %d %d c 1\n' % (x1, y1, x1, y1, next_x, next_y)

        # soft version
        new_code = ' %d %d %d %d %d %d c 1\n' % (previous_recenter_x, previous_recenter_y, next_recenter_x, next_recenter_y, next_x, next_y)

        dot_dict={}
        dot_dict['x1']=previous_recenter_x
        dot_dict['y1']=previous_recenter_y
        dot_dict['x2']=next_recenter_x
        dot_dict['y2']=next_recenter_y
        dot_dict['x']=next_x
        dot_dict['y']=next_y
        dot_dict['t']='c'
        dot_dict['code']=new_code

        insert_idx = (idx+2)%nodes_length
        format_dict_array.insert(insert_idx, dot_dict)
        
        #print("insert to index:",insert_idx)
        #print("appdend +3 new_code:", new_code)

        #if True:
        if False:
            print("-" * 20)
            for debug_idx in range(6):
                print(debug_idx-2,": values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])

        return format_dict_array, previous_x, previous_y, next_x, next_y

    # for rectangel version. ex: rule#1,#2,#3
    def apply_round_transform(self,format_dict_array,idx):
        nodes_length = len(format_dict_array)

        center_x = int((format_dict_array[(idx+1)%nodes_length]['x']+format_dict_array[(idx+2)%nodes_length]['x'])/2)
        center_y = int((format_dict_array[(idx+1)%nodes_length]['y']+format_dict_array[(idx+2)%nodes_length]['y'])/2)
        
        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        round_length_1 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < self.config.ROUND_OFFSET:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < self.config.ROUND_OFFSET:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # use more close coordinate.
        #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x0
            y_from = y0
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x1,y1,round_length_1)
        
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x3
            y_from = y3
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x3,y3,round_length_2)
        #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

        new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
        new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2,-1 * round_length_2)

        # re-center again.
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            orig_new_x1, orig_new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * self.config.ROUND_OFFSET)
            new_x1, new_y1 = int((orig_new_x1+new_x1)/2) , int((orig_new_y1+new_y1)/2)
        # re-center again.
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            orig_new_x2, orig_new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * self.config.ROUND_OFFSET)
            new_x2, new_y2 = int((orig_new_x2+new_x2)/2) , int((orig_new_y2+new_y2)/2)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        #if True:
        if False:
            print("center x,y:", center_x, center_y)
            print("new x1,y1:", new_x1, new_y1)
            print("new x2,y2:", new_x2, new_y2)

        # for 辶部，的凹洞.
        # PS: 這是檢測水平線，還無法處理斜線型的凹洞。
        is_prefer_y1_straight = False
        #print("-1 y_equal_fuzzy:", format_dict_array[(idx-1+nodes_length)%nodes_length]['y_equal_fuzzy'])
        if format_dict_array[(idx-1+nodes_length)%nodes_length]['y_equal_fuzzy']:
            if format_dict_array[(idx-1+nodes_length)%nodes_length]['x_direction'] == format_dict_array[(idx+0+nodes_length)%nodes_length]['x_direction']:
                if format_dict_array[(idx+1+nodes_length)%nodes_length]['t']=='c':
                    if abs(format_dict_array[(idx+1+nodes_length)%nodes_length]['y2']-format_dict_array[(idx-1+nodes_length)%nodes_length]['y'])<=3:
                        is_prefer_y1_straight = True

        # re-center again
        # see alpha Y (id.319, it's not work!)
        #center_y = int((new_y1+new_y2)/2)

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if format_dict_array[(idx+3)%nodes_length]['t']=="c":
            old_code_string = format_dict_array[(idx+3)%nodes_length]['code']
            old_code_array = old_code_string.split(' ')

            # 內縮，造成奇怪的曲線。
            # strong offset
            #extend_offset_x = int(old_code_array[1])+ int(x2_offset/1)
            #extend_offset_y = int(old_code_array[2])+ int(y2_offset/1)
            
            # soft offset
            extend_offset_x = int(float(old_code_array[1]))+ int(x2_offset/2)
            extend_offset_y = int(float(old_code_array[2]))+ int(y2_offset/2)

            #if True:
            if False:
                print("xy2:", x2, y2)
                print("orig xy3:", orig_x3, orig_y3)
                print("xy2 offset:", x2_offset, y2_offset)

            # from top move to bottom, check overflow.
            if y2_offset < 0:
                if extend_offset_y < orig_y3:
                    extend_offset_y = orig_y3
            # bottom to top.
            if y2_offset > 0:
                if extend_offset_y > orig_y3:
                    extend_offset_y = orig_y3
            # from right move to left.
            if x2_offset < 0:
                if extend_offset_x < orig_x3:
                    extend_offset_x = orig_x3
            if x2_offset > 0:
                if extend_offset_x > orig_x3:
                    extend_offset_x = orig_x3

            old_code_array[1] = str(extend_offset_x)
            old_code_array[2] = str(extend_offset_y)

            format_dict_array[(idx+3)%nodes_length]['x1']=extend_offset_x
            format_dict_array[(idx+3)%nodes_length]['y1']=extend_offset_y

            # 如果 x1,y1=x2,y2, 順便調整另一組。
            if old_code_array[1] == old_code_array[3] and old_code_array[2] == old_code_array[4]:
                old_code_array[3] = str(extend_offset_x)
                old_code_array[4] = str(extend_offset_y)

            # 調整 +3 的 x2,y2

            # 內縮前 x2,y2 的長度
            before_distance = spline_util.get_distance(x2,y2,orig_x3,orig_y3)
            after_distance = spline_util.get_distance(new_x2,new_y2,orig_x3,orig_y3)
            diff_percent = 1.0
            if before_distance > 5 and after_distance > 5:
                diff_percent = after_distance / before_distance

            extend_offset_x = int(float(old_code_array[3]))
            extend_offset_y = int(float(old_code_array[4]))

            before_extend_distance = spline_util.get_distance(extend_offset_x,extend_offset_y,orig_x3,orig_y3)
            after_extend_distance = int(before_extend_distance * diff_percent)
            if after_extend_distance < before_extend_distance:
                # 調整強度的百分比。
                extend_offset_x,extend_offset_y = spline_util.two_point_extend(extend_offset_x,extend_offset_y,orig_x3,orig_y3,-1 * after_extend_distance)

            old_code_array[3] = str(extend_offset_x)
            old_code_array[4] = str(extend_offset_y)

            format_dict_array[(idx+3)%nodes_length]['x2']=extend_offset_x
            format_dict_array[(idx+3)%nodes_length]['y2']=extend_offset_y

            new_code = ' '.join(old_code_array)
            format_dict_array[(idx+3)%nodes_length]['code'] = new_code
            #print("before code:", old_code_string)
            #print("new_code code:", new_code)

        # update #1
        #print("self.config.PROCESS_MODE:", self.config.PROCESS_MODE)
        if self.config.PROCESS_MODE in ["GOTHIC","D"]:
            #print("self.config.PROCESS_MODE in [GOTHIC]")
            format_dict_array[(idx+1)%nodes_length]['x']= new_x1
            format_dict_array[(idx+1)%nodes_length]['y']= new_y1

            old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
            old_code_array = old_code_string.split(' ')

            # this should not happen in this rule, because dot-1 must match "l"
            if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                new_distance = spline_util.get_distance(new_x1,new_y1,format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'])

                is_convert_to_l = False

                if new_distance <= 40:
                    is_convert_to_l = True

                if is_convert_to_l:
                    format_dict_array[(idx+1)%nodes_length]['t']="l"
                    tmp_code_string = ' %d %d l 1\n' % (new_x1,new_y1)
                    old_code_array = tmp_code_string.split(' ')
                else:
                    # 內縮，造成奇怪的曲線。
                    # strong offset
                    #extend_offset_x = int(old_code_array[1])+ int(x2_offset/1)
                    #extend_offset_y = int(old_code_array[2])+ int(y2_offset/1)
                    
                    # soft offset
                    extend_offset_x = int(float(old_code_array[3]))+ int(x1_offset/2)
                    extend_offset_y = int(float(old_code_array[4]))+ int(y1_offset/2)

                    # 讓線變直，for 辶部。
                    if is_prefer_y1_straight:
                        extend_offset_y = int(float(old_code_array[4]))

                    # 如果 x1,y1=x,y, 順便調整另一組。
                    if old_code_array[1] == old_code_array[3] and old_code_array[2] == old_code_array[4]:
                        old_code_array[1] = str(extend_offset_x)
                        old_code_array[2] = str(extend_offset_y)

                    old_code_array[3] = str(extend_offset_x)
                    old_code_array[4] = str(extend_offset_y)

                    # 如果 x1,y1=x,y, 順便調整另一組。
                    if old_code_array[1] == old_code_array[5] and old_code_array[2] == old_code_array[6]:
                        old_code_array[1] = str(new_x1)
                        old_code_array[2] = str(new_y1)

                    old_code_array[5] = str(new_x1)
                    old_code_array[6] = str(new_y1)
            else:
                # not is 'c'
                old_code_array[1] = str(new_x1)
                old_code_array[2] = str(new_y1)
            new_code = ' '.join(old_code_array)
            target_index = (idx+1)%nodes_length
            format_dict_array[target_index]['code'] = new_code
            self.apply_code(format_dict_array,(idx+1)%nodes_length)
    
            #if True:
            if False:
                print("old_code_string:", old_code_string)
                print("is_prefer_y1_straight:", is_prefer_y1_straight)
                print("+1 idx:%d, code:%s" % (target_index, new_code))

            # update #2
            #new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1, new_y1, x1, y1, center_x, center_y)
            new_code = ' %d %d %d %d %d %d c 1\n' % (x1, y1, x1, y1, center_x, center_y)
            dot_dict={}
            dot_dict['x']=center_x
            dot_dict['y']=center_y
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=x1
            dot_dict['y1']=y1
            dot_dict['x2']=x1
            dot_dict['y2']=y1

            dot_dict['code']=new_code
            target_index = (idx+2)%nodes_length
            format_dict_array[target_index]=dot_dict
            self.apply_code(format_dict_array,(idx+2)%nodes_length)
            #print("+2 idx:%d, code:%s" % (target_index, new_code))


        if self.config.PROCESS_MODE in ["HALFMOON"]:
            #print("self.config.PROCESS_MODE in [HALFMOON]")
            # move to left
            center_x = x1
            center_y = y1
            
            # update #2
            new_code = ' %d %d l 1\n' % (center_x, center_y)
            dot_dict={}
            dot_dict['x']=center_x
            dot_dict['y']=center_y
            dot_dict['t']='l'
            dot_dict['code']=new_code
            format_dict_array[(idx+2)%nodes_length]=dot_dict
            #print("rule16 new_code:", new_code)

        # append new #3
        #new_code = ' %d %d %d %d %d %d c 1\n' % (center_x, center_y, x2, y2, new_x2, new_y2)
        new_code = ' %d %d %d %d %d %d c 1\n' % (x2, y2, x2, y2, new_x2, new_y2)
        dot_dict={}
        dot_dict['x']=new_x2
        dot_dict['y']=new_y2
        dot_dict['t']='c'
        dot_dict['code']=new_code
        target_index = (idx+3)%nodes_length
        format_dict_array.insert(target_index,dot_dict)
        #print("+3 idx:%d, code:%s" % (target_index, new_code))

        return center_x,center_y

    def rule_test(self,format_dict_array,idx,rule_no,inside_stroke_dict=None):
        # compare direction
        # start to compare.
        is_match_pattern = True
        nodes_length = len(format_dict_array)

        if rule_no == 16:
            # 這個參數，不要與其他參數共用，以避免其他參數一調整，這一個值就消失了。
            TAIL_LENGTH_MIN = 35

            # for case: .44730 「饞」
            #0 : values for rule16:  874 418 l 2 -( 43 )
            #1 : values for rule16:  891 418 895 423 898 454 c 1 -( 53 )
            #2 : values for rule16:  949 437 l 1 -( 92 )
            #3 : values for rule16:  945 388 927 373 882 373 c 2 -( 101 )
            if is_match_pattern:
                fail_code = 100
                is_match_pattern = False
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                            if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                                is_match_pattern = True

            # 2個邊不要太短
            if is_match_pattern:
                fail_code = 220
                is_match_pattern = False
                if format_dict_array[(idx+0)%nodes_length]['distance'] > TAIL_LENGTH_MIN:
                    if format_dict_array[(idx+2)%nodes_length]['distance'] > TAIL_LENGTH_MIN:
                        is_match_pattern = True

            # compare direction
            if is_match_pattern:
                fail_code = 300
                #print(idx,"debug rule3:",format_dict_array[idx]['code'])
                is_match_pattern = False
                if format_dict_array[(idx+0)%nodes_length]['y_direction'] != 0:
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['y_direction']:
                        if format_dict_array[(idx+0)%nodes_length]['x_direction'] != 0:
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                                is_match_pattern = True

            # compare direction
            # for case: .31845. 「糸」系列都會遇到，暫時畫的很醜，日後再想想如何處理。
            if is_match_pattern:
                fail_code = 310
                if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                    is_match_pattern = False

            # check from bmp file.
            if is_match_pattern:
                is_match_pattern = False
                fail_code = 500

                if not inside_stroke_dict is None:
                    bmp_x1 = format_dict_array[(idx+0)%nodes_length]['x']
                    bmp_y1 = format_dict_array[(idx+0)%nodes_length]['y']
                    bmp_x2 = format_dict_array[(idx+1)%nodes_length]['x']
                    bmp_y2 = format_dict_array[(idx+1)%nodes_length]['y']
                    bmp_x3 = format_dict_array[(idx+2)%nodes_length]['x']
                    bmp_y3 = format_dict_array[(idx+2)%nodes_length]['y']
                    bmp_x4 = format_dict_array[(idx+3)%nodes_length]['x']
                    bmp_y4 = format_dict_array[(idx+3)%nodes_length]['y']
                    
                    # 精簡的比對，會出錯，例如「緫」、「縃」、「繳」的方。「解」的刀。「繫」的山。
                    #bmp_x2 = bmp_x1 + (5 * format_dict_array[(idx+0)%nodes_length]['x_direction'])
                    #bmp_x3 = bmp_x4 + (5 * format_dict_array[(idx+0)%nodes_length]['x_direction'])
                    #bmp_y2 = bmp_y1 + (5 * format_dict_array[(idx+0)%nodes_length]['y_direction'])
                    #bmp_y3 = bmp_y4 + (5 * format_dict_array[(idx+0)%nodes_length]['y_direction'])
                    
                    # full rectangle compare.
                    #inside_stroke_flag = self.is_inside_stroke(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4)

                    # compact triangle compare, 
                    # allow one coner match to continue
                    inside_stroke_flag2 = False
                    inside_stroke_flag1,inside_stroke_dict = self.test_inside_coner(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, self.config.STROKE_MIN, inside_stroke_dict)
                    if not inside_stroke_flag1:
                        # test next coner
                        inside_stroke_flag2,inside_stroke_dict = self.test_inside_coner(bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4, self.config.STROKE_MIN, inside_stroke_dict)

                    if inside_stroke_flag1 or inside_stroke_flag2:
                        is_match_pattern = True

        return is_match_pattern, fail_code

    # 角度的影響，修改為取決於距離長度。
    def compute_curve_new_xy(self,x_from,y_from,x_center,y_center,x1,y1,round_offset):
        distance_full = spline_util.get_distance(x_from,y_from,x1,y1)
        
        x_middle = (x_from + x1) / 2
        y_middle = (y_from + y1) / 2

        new_x_center = int((x_middle + x_center) / 2)
        new_y_center = int((y_middle + y_center) / 2)

        previous_x,previous_y = new_x_center,new_y_center

        # PS: distance_head and distance_tail maybe equal 0.
        distance_head = spline_util.get_distance(x_from,y_from,x_center,y_center)
        distance_tail = spline_util.get_distance(x_center,y_center,x1,y1)
        if distance_head > 0 and distance_tail > 0:
            distance_middle = distance_full * (distance_head/(distance_head+distance_tail))

            # default: use tail part.
            use_head_part = False
            if round_offset > distance_middle:
                use_head_part = True
            round_offset_tail = distance_full - round_offset

            if not use_head_part:
                previous_x,previous_y=spline_util.two_point_extend(new_x_center,new_y_center,x1,y1,-1 * round_offset)
            else:
                previous_x,previous_y=spline_util.two_point_extend(new_x_center,new_y_center,x_from,y_from,-1 * round_offset_tail)

        #if True:
        if False:
            print("use_head_part:",use_head_part)
            print("x_from,y_from:",x_from,y_from)
            print("x1,y1:",x1,y1)
            print("x_center,y_center:",x_center,y_center)
            print("x_middle,y_middle:",x_middle,y_middle)
            print("new_x_center,new_y_center:",new_x_center,new_y_center)
            print("distance_full:", distance_full)
            print("distance_middle:",distance_middle)
            print("round_offset_tail:",round_offset_tail)
            print("previous_x,previous_y:",previous_x,previous_y)
        return previous_x,previous_y


    # purpose: check for D.Lucy base rule.
    # return:
    #   True: match, path going right.
    #   False: not match, path going left.
    def going_d_right(self, format_dict_array, idx):
        going_right = True
        is_match_pattern = False
        fail_code = 0

        nodes_length = len(format_dict_array)

        if not is_match_pattern:
            # - sharp.
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                    fail_code = 2201
                    is_match_pattern = True
                    going_right = False

        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                    fail_code = 2202
                    is_match_pattern = True
                    going_right = False

        if not is_match_pattern:
            # \ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                fail_code = 2203
                is_match_pattern = True
                going_right = False


        return going_right, fail_code
