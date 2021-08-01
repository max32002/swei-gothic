#!/usr/bin/env python3
#encoding=utf-8

import bezier
import numpy as np
from . import spline_util

import os

#import cv2
#import numpy as np

class Rule():
    config = None
    unicode_int = -1
    is_Latin_Flag = False
    is_Hangul_Flag = False
    is_Before_CJK_Flag = False

    bmp_image = None
    bmp_x_offset = 0
    bmp_y_offset = 0

    def __init__(self):
        pass

    def assign_unicode(self, val):
        self.unicode_int = val
        self.is_Latin_Flag = self.is_Latin()
        self.is_Hangul_Flag = self.is_Hangul()
        self.is_Before_CJK_Flag = self.is_Before_CJK()

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

    # 0-2E7F, before "CJK Radicals Supplement"
    def is_Before_CJK(self):
        ret = False
        if self.unicode_int > 0:
            if self.unicode_int <= 11903:
                ret = True
        return ret

    # PS: not used now.
    def assign_x_offset(self, offset):
        #print("assign assign_x_offset:", offset)
        self.bmp_x_offset = offset

    # PS: not used now.
    def assign_y_offset(self, offset):
        #print("assign bmp_y_offset:", offset)
        self.bmp_y_offset = offset

    def ff_x_to_bmp_x(self, x):
        return x + self.bmp_x_offset

    def ff_y_to_bmp_y(self, y):
        FF_TOP = 900
        top = FF_TOP - self.bmp_y_offset
        return top + (y * -1)

    # PS: opencv solution.
    # PS: not used now.
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
            inside_stroke_flag = not self.is_inside_triangle(previous_x,previous_y,x2,y2,next_x,next_y, debug_mode=debug_mode)
            inside_stroke_dict[inside_stroke_key] = inside_stroke_flag
        return inside_stroke_flag,inside_stroke_dict

    # for triangle
    # only test center point.
    # return:
    #   True: white dot.
    #   False: black dot.
    def is_inside_triangle(self, x1, y1, x2, y2, x3, y3, debug_mode=False):
        ret = True

        # force switch to debug mode.
        #debug_mode = True
        if debug_mode:
            print("test FF dots:", x1, y1, x2, y2, x3, y3)

        if not self.bmp_image is None:
            # for PIL
            #h,w = self.bmp_image.height,self.bmp_image.width
            h,w = self.bmp_image.shape

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

            #for PIL
            #data=self.bmp_image.getpixel((bmp_x, bmp_y))
            
            # for 8bit
            #if data>=128:
                #ret=False

            ret = self.bmp_image[bmp_y, bmp_x]

            if debug_mode:
                print("center_x,y:",center_x,center_y)
                print("bmp_x,y:",bmp_x,bmp_y)
                print("bmp x_offset:", self.bmp_x_offset)
                print("bmp y_offset:", self.bmp_y_offset)
                #print("data:", data)

        else:
            #print("bmp is None!")
            pass
        return ret

    # for triangle
    # PS: opencv solution.
    # PS: not used now.
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
    # PS: opencv solution.
    # PS: not used now.
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
            # for PIL
            #h,w = self.bmp_image.height,self.bmp_image.width
            # for numpy
            h,w = self.bmp_image.shape

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
                
                # for PIL.
                #data=self.bmp_image.getpixel((bmp_x, bmp_y))
                data=self.bmp_image[bmp_y,bmp_x]

                if debug_mode:
                    print("data:", data)
                    pass
                
                #if data >=128:
                if data:
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
            # for PIL
            #h,w = self.bmp_image.height, self.bmp_image.width
            # for numpy
            h,w = self.bmp_image.shape

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

                # for PIL
                #data=self.bmp_image.getpixel((bmp_x, bmp_y))
                data=self.bmp_image[bmp_y,bmp_x]

                #print("data:", data)
                #if data <=128:
                if not data:
                    black_dot_count +=1

                # 功成身退了，感謝你的努力。
                #if black_dot_count >= STROKE_MATCH_MIN and data >=128:
                if black_dot_count >= STROKE_MATCH_MIN and data:
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

        nodes_length = len(format_dict_array)
        next_index = (idx+1)%nodes_length
        current_x = format_dict_array[idx]['x']
        current_y = format_dict_array[idx]['y']

        next_x = format_dict_array[next_index]['x']
        next_y = format_dict_array[next_index]['y']
        distance = spline_util.get_distance(current_x,current_y,next_x,next_y)
        format_dict_array[idx]['distance']=distance

        match_stroke_width_flag = False
        if distance >= self.config.STROKE_WIDTH_MIN:
            allowed_max_width = self.config.STROKE_WIDTH_MAX

            # for _Kappa, Greek Small Letter Kappa
            # under Unicode Block “CJK Radicals Supplement”
            if self.is_Before_CJK_Flag:
                # allow more 1.10(default) * 1.15(extra) for non-chinese glyph.
                allowed_max_width *= 1.15
                #print("allowed_max_width:", allowed_max_width)

            if distance <= allowed_max_width:
                match_stroke_width_flag = True
        format_dict_array[idx]['match_stroke_width'] = match_stroke_width_flag

        x_direction_value = 0
        if next_x > current_x:
            x_direction_value=1
        if next_x < current_x:
            x_direction_value=-1
        format_dict_array[idx]['x_direction']=x_direction_value

        y_direction_value=0
        if next_y > current_y:
            y_direction_value=1
        if next_y < current_y:
            y_direction_value=-1
        format_dict_array[idx]['y_direction']=y_direction_value

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

        return format_dict_array

    def check_clockwise(self, spline_array):
        clockwise = True
        area_total=0
        poly_lengh = len(spline_array)
        if poly_lengh >=  3:
            for idx in range(poly_lengh):
                item_sum = ((spline_array[(idx+0)%poly_lengh][0] * spline_array[(idx+1)%poly_lengh][1]) - (spline_array[(idx+1)%poly_lengh][0] * spline_array[(idx+0)%poly_lengh][1]))
                area_total += item_sum
            if area_total >= 0:
                clockwise = not clockwise
        return clockwise

    # for triangle version, ex: rule#5
    def make_coner_curve(self,round_offset,format_dict_array,idx,apply_rule_log,generate_rule_log,stroke_dict,key,coner_mode="CURVE"):
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
        previous_x,previous_y=0,0
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            previous_x,previous_y=self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x0,y0,round_length_1)
        else:
            previous_x,previous_y=spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)

        next_x,next_y=0,0
        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+2)%nodes_length]['x1']
            y_center = format_dict_array[(idx+2)%nodes_length]['y1']
            next_x,next_y= self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x2,y2,round_length_2)
        else:
            next_x,next_y=spline_util.two_point_extend(x2,y2,x1,y1,-1 * round_length_2)

        #if True:
        if False:
            print("orig x0,y0,x1,y1,x2,y2:", orig_x0,orig_y0,x1,y1,orig_x2,orig_y2)
            print("new x0,y0,x1,y1,x2,y2:", x0,y0,x1,y1,x2,y2)

        previous_x_offset = x1 - previous_x
        previous_y_offset = y1 - previous_y

        # stronge version
        curve_version = 1
        previous_recenter_x,previous_recenter_y=x1,y1
        next_recenter_x,next_recenter_y=x1,y1

        # make curve more "SOFT"
        #curve_version = 2
        if self.config.PROCESS_MODE in ["B4"]:
            curve_version = 2
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

        #PS: 好像是可以直接加入。
        #    因為 previous x,y 是新產生出來的點。
        #print("previous x,y 是新產生出來的點, code:", new_code)
        apply_rule_log.append(new_code)

        # purpose: 原本的 middle dot 是否在 skip rule 裡。
        is_middle_dot_in_skip_rule = False

        if old_code_string in apply_rule_log:
            is_middle_dot_in_skip_rule = True


        # update [next next curve]
        # PS: 目前使用的解法問題多多，應該有更好的解法。
        # PS: 目前使用work around 解法1.
        # PS: [TODO]: 連續套用，並產生奇怪曲線的問題，還是可能會發生，而且目前還沒有去檢查和解決。
        if format_dict_array[(idx+2)%nodes_length]['t']=="c":
            old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
            old_code_array = old_code_string.split(' ')

            new_distance = spline_util.get_distance(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],next_x,next_y)
            distance_lost = format_dict_array[(idx+1)%nodes_length]['distance'] - new_distance

            is_convert_to_l = False

            if new_distance <= 40:
                is_convert_to_l = True
            else:
                if new_distance <= 200:
                    # PS: 把太長的曲線變直線，會變超級怪。
                    # PS: uni9773 的斤，會剛好被變成直線，筆畫會變粗。

                    # for fix uni7729 的幺內縮。
                    # PS: 應該有其他更好解法，暫時先用 workaround.
                    slide_percent_next = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    #print("slide_percent_next:", slide_percent_next)
                    #print("slide_percent_next data:", slide_percent_next)
                    if slide_percent_next >= 1.990:
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

                offset_distance = spline_util.get_distance(x1,y1,next_x,next_y)
                virtual_x1y1_distance = spline_util.get_distance(x1,y1,int(old_code_array[1]),int(old_code_array[2]))

                is_virtual_dot_need_offset = False
                #is_virtual_dot_need_offset = True
                # for uni7D93 經的幺，要不要offset.
                # (regular) offset_distance = 29
                # (regular) virtual_x1y1_distance = 35
                # (medium) offset_distance = 29
                # (medium) virtual_x1y1_distance = 39
                if virtual_x1y1_distance <= int(offset_distance * 1.0):
                    is_virtual_dot_need_offset = True
                else:
                    if virtual_x1y1_distance <= int(offset_distance * 2.0):
                        # 不確定這個解法，會不會造成再下一個點造成內凹。
                        # virtual_x1y1_distance_remain: virtual 點到下一個實體點的長度
                        virtual_x1y1_distance_remain = spline_util.get_distance(orig_x2,orig_y2,int(old_code_array[1]),int(old_code_array[2]))
                        #print("orig_x2,orig_y2:",orig_x2,orig_y2)
                        #print("virtual_x1y1_distance_remain:",virtual_x1y1_distance_remain)

                        # 需要夠長的空間，都做 offset
                        # PS: 如果 virtual_x1y1_distance_remain 夠長都offset, 會造成筆畫變細。
                        #     參考看看 uni9773,靳的斤.
                        if virtual_x1y1_distance_remain >= offset_distance * 3:
                            is_virtual_dot_need_offset = True

                #print("virtual distance:", offset_distance)
                #print("x1y1 distance:", virtual_x1y1_distance)
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

            if old_code_string in apply_rule_log:
                #print("+2 old code in rule:", old_code_string)
                #print("+2 update as new code in rule:", new_code)
                apply_rule_log.append(new_code)

        # append new #2
        # strong version
        #new_code = ' %d %d %d %d %d %d c 1\n' % (x1, y1, x1, y1, next_x, next_y)

        # coner_mode == "CURVE"
        new_code = ' %d %d %d %d %d %d c 1\n' % (previous_recenter_x, previous_recenter_y, next_recenter_x, next_recenter_y, next_x, next_y)
        if coner_mode in ["STRAIGHT","ALIAS","SPIKE"]:
            new_code = ' %d %d l 1\n' % (next_x, next_y)

        dot_dict={}
        dot_dict['t']='l'
        if coner_mode == "CURVE":
            dot_dict['t']='c'
            dot_dict['x1']=previous_recenter_x
            dot_dict['y1']=previous_recenter_y
            dot_dict['x2']=next_recenter_x
            dot_dict['y2']=next_recenter_y
        dot_dict['x']=next_x
        dot_dict['y']=next_y
        dot_dict['code']=new_code
        #print("idx+2 new_code:", new_code)

        insert_idx = (idx+2)%nodes_length
        format_dict_array.insert(insert_idx, dot_dict)
        nodes_length = len(format_dict_array)
        if idx >= insert_idx:
            idx += 1
        self.apply_code(format_dict_array,(idx+2)%nodes_length)

        # middle dot in skip rule list.
        if is_middle_dot_in_skip_rule:
            # 由於middle dot 從一個 dot 變成多個，所以新產生出來的dot 也算是 skip rule.
            apply_rule_log.append(new_code)

        # new dot for SPIKE
        if coner_mode in ["SPIKE"]:
            near_middle_x = int((previous_x + next_x) / 2)
            near_middle_y = int((previous_y + next_y) / 2)

            distance_to_middle = spline_util.get_distance(x1,y1,near_middle_x,near_middle_y)
            
            #default_near_x, default_near_y = x1,y1
            #default_near_x, default_near_y = near_middle_x, near_middle_y
            default_near_x, default_near_y = spline_util.two_point_extend(near_middle_x,near_middle_y,x1,y1,distance_to_middle)

            near_x = default_near_x
            near_y = default_near_y

            new_code = ' %d %d l 1\n' % (near_x, near_y)

            dot_dict={}
            dot_dict['t']='l'
            dot_dict['x']=near_x
            dot_dict['y']=near_y
            dot_dict['code']=new_code

            # [IMPORTANT]: new node 千萬不要加入 apply_rule_log, 會造成最後一個點無法apply rule.
            # PS: 但由於是多餘的點，所以可以直接略過新增加。
            apply_rule_log.append(new_code)

            insert_idx = (idx+2)%nodes_length
            format_dict_array.insert(insert_idx, dot_dict)
            nodes_length = len(format_dict_array)
            if idx >= insert_idx:
                idx += 1
            self.apply_code(format_dict_array,(idx+2)%nodes_length)


        # new dot for ALIAS
        if coner_mode in ["ALIAS"]:
            near_middle_x = int((previous_x + next_x) / 2)
            near_middle_y = int((previous_y + next_y) / 2)

            #distance_to_middle = spline_util.get_distance(x1,y1,near_middle_x,near_middle_y)
            
            #default_near_x, default_near_y = x1,y1
            #default_near_x, default_near_y = near_middle_x, near_middle_y

            # PS: 下面副程式沒寫好，會有問題...。
            #default_near_x, default_near_y = spline_util.two_point_extend(x1,y1,near_middle_x,near_middle_y,distance_to_middle)
            # 使用替代寫法.
            near_x_offset = x1 - near_middle_x
            near_y_offset = y1 - near_middle_y
            
            default_near_x = near_middle_x - near_x_offset
            default_near_y = near_middle_y - near_y_offset

            near_x = default_near_x
            near_y = default_near_y

            default_near_pos = [default_near_x,default_near_y]
            exclude_list = [[x1,y1],[previous_x,previous_y],[next_x,next_y],[orig_x0,orig_y0],[orig_x2,orig_y2]]
            near_x,near_y = self.find_best_alias_xy(default_near_pos,exclude_list,stroke_dict)

            # fix while block disappear.
            near_x,near_y = spline_util.two_point_extend(x1,y1,near_x,near_y,-2)

            # let alias more sharp.
            # for -
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                old_code_array = old_code_string.split(' ')
                if format_dict_array[(idx+1)%nodes_length]['t']=="c":
                    old_code_array[5] = str(near_x)
                else:
                    # l
                    old_code_array[1] = str(near_x)
                new_code = ' '.join(old_code_array)
                format_dict_array[(idx+1)%nodes_length]['code'] = new_code
                self.apply_code(format_dict_array,(idx+1)%nodes_length)

                if old_code_string in apply_rule_log:
                    apply_rule_log.append(new_code)

            # for |
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                old_code_array = old_code_string.split(' ')
                if format_dict_array[(idx+1)%nodes_length]['t']=="c":
                    old_code_array[6] = str(near_y)
                else:
                    # l
                    old_code_array[2] = str(near_y)
                new_code = ' '.join(old_code_array)
                format_dict_array[(idx+1)%nodes_length]['code'] = new_code
                self.apply_code(format_dict_array,(idx+1)%nodes_length)

                if old_code_string in apply_rule_log:
                    apply_rule_log.append(new_code)

            # for -
            if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
                old_code_array = old_code_string.split(' ')
                if format_dict_array[(idx+2)%nodes_length]['t']=="c":
                    old_code_array[5] = str(near_x)
                else:
                    # l
                    old_code_array[1] = str(near_x)
                new_code = ' '.join(old_code_array)
                format_dict_array[(idx+2)%nodes_length]['code'] = new_code
                self.apply_code(format_dict_array,(idx+2)%nodes_length)

                if old_code_string in apply_rule_log:
                    apply_rule_log.append(new_code)

            # for |
            if format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
                old_code_array = old_code_string.split(' ')
                if format_dict_array[(idx+2)%nodes_length]['t']=="c":
                    old_code_array[6] = str(near_y)
                else:
                    # l
                    old_code_array[2] = str(near_y)
                new_code = ' '.join(old_code_array)
                format_dict_array[(idx+2)%nodes_length]['code'] = new_code
                self.apply_code(format_dict_array,(idx+2)%nodes_length)

                if old_code_string in apply_rule_log:
                    apply_rule_log.append(new_code)


            new_code = ' %d %d l 1\n' % (near_x, near_y)

            dot_dict={}
            dot_dict['t']='l'
            dot_dict['x']=near_x
            dot_dict['y']=near_y
            dot_dict['code']=new_code

            # [IMPORTANT]: new node 千萬不要加入 apply_rule_log, 會造成最後一個點無法apply rule.
            # PS: 但由於是多餘的點，所以可以直接略過新增加。
            apply_rule_log.append(new_code)

            insert_idx = (idx+2)%nodes_length
            format_dict_array.insert(insert_idx, dot_dict)
            nodes_length = len(format_dict_array)
            if idx >= insert_idx:
                idx += 1
            self.apply_code(format_dict_array,(idx+2)%nodes_length)

        # 因為較短邊 <= round_offset, 需要合併節點。
        # PS: 已忘記是那一個字，會用到下面合併節點的 code, 似乎大部份的字應該不會需要用到。
        is_merge_short_edge = True
        MIN_DISTANCE_TO_MERGE = 10

        if coner_mode in ["STRAIGHT","ALIAS","SPIKE"]:
            is_merge_short_edge = False

        if is_merge_short_edge:
            if format_dict_array[(idx+2)%nodes_length]['distance'] <= 0:
                del format_dict_array[(idx+3)%nodes_length]

                if idx >= (idx+3)%nodes_length:
                    idx -= 1
                nodes_length = len(format_dict_array)
                #print("match is_need_redo_current_dot:", format_dict_array[(idx+0)%nodes_length]['code'])
            else:

                # merge short edge.
                if format_dict_array[(idx+2)%nodes_length]['distance'] <= MIN_DISTANCE_TO_MERGE:
                    #print("extend +2 to +3.")
                    #print("old +2 code:", format_dict_array[(idx+2)%nodes_length]['code'])
                    #print("old +3 code:", format_dict_array[(idx+3)%nodes_length]['code'])
                    old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
                    old_code_array = old_code_string.split(' ')
                    new_x = str(format_dict_array[(idx+3)%nodes_length]['x'])
                    new_y = str(format_dict_array[(idx+3)%nodes_length]['y'])
                    if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                        old_code_array[5] = new_x
                        old_code_array[6] = new_y
                    else:
                        # l
                        old_code_array[1] = new_x
                        old_code_array[2] = new_y
                    new_code = ' '.join(old_code_array)
                    # only need update code, let formater to re-compute.
                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code
                    #print("new +2 code:", format_dict_array[(idx+2)%nodes_length]['code'])

                    del format_dict_array[(idx+3)%nodes_length]

                    if idx > (idx+3)%nodes_length:
                        idx -=1
                    nodes_length = len(format_dict_array)
                    self.apply_code(format_dict_array,(idx+2)%nodes_length)

            self.apply_code(format_dict_array,(idx+0)%nodes_length)
            if format_dict_array[(idx+0)%nodes_length]['distance'] <= 0:
                del format_dict_array[(idx+1)%nodes_length]

                if idx >= (idx+1)%nodes_length:
                    idx -= 1
                nodes_length = len(format_dict_array)
            else:
                # dot+1 is our generated position. skip to transform.
                # to avoid same code apply twice.

                # merge short edge.
                if format_dict_array[(idx+0)%nodes_length]['distance'] <= MIN_DISTANCE_TO_MERGE:
                    #print("extend +1 to +0.")
                    #print("old +0 code:", format_dict_array[(idx+0)%nodes_length]['code'])
                    #print("old +1 code:", format_dict_array[(idx+1)%nodes_length]['code'])

                    del format_dict_array[(idx+1)%nodes_length]

                    if idx >= (idx+1)%nodes_length:
                        idx -= 1
                    nodes_length = len(format_dict_array)

                # 己忘記什麼情況下需要使用到這一段code,
                # 但加了之後，會讓 uni7345 獅的帀裡的一個轉角沒套用到效果.
                # 目前先設為False不跑，不跑也有問題，就會可能會多套用效果。

                # [TODO]:找到為什麼加這段code,是 uni7D93 經的幺，
                # 在「沒有」做 offset 的情況下，會發生一連串的重覆套用，

                # 因為第一點產生完是 clockwise, 第二點原本是 counter clockwise,
                # Rule5/Rule99, 會先用 virtual dot 做比對，會變成銳角。

                # 解法，是遇到第二段edge=='c'時，clockwise + counter clockwise,
                # 這個情況下，做apply_rule_log.append()
                if False:
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+1)%nodes_length]['code']
                    #print("generated_code+1 to rule:", generated_code)
                    apply_rule_log.append(generated_code)


        return format_dict_array, previous_x, previous_y, next_x, next_y

    def find_best_alias_xy(self, default_near_pos, exclude_list, stroke_dict):
        default_near_x = default_near_pos[0]
        default_near_y = default_near_pos[1]

        shortest_x = default_near_x
        shortest_y = default_near_y

        # 在 black style 效果很慘烈。
        #ALLOW_ALIAS_RANGE = self.config.STROKE_WIDTH_MAX * 0.8
        ALLOW_ALIAS_RANGE = 40
        last_distance = 100
        for key in stroke_dict.keys():
            tmp_spline_dict = stroke_dict[key]
            
            tmp_format_dict_array=[]
            tmp_format_dict_array = tmp_spline_dict['dots'][1:]

            nodes_length = len(tmp_format_dict_array)
            
            # 只有 3個點也是夠的，因為會跨 spline
            rule_need_lines = 3
            fail_code = -1
            if nodes_length >= rule_need_lines:
                for idx in range(nodes_length):
                    current_x = tmp_format_dict_array[idx]['x']
                    current_y = tmp_format_dict_array[idx]['y']
                    if [current_x,current_y] in exclude_list:
                        continue
                    if abs(default_near_x - current_x) <= ALLOW_ALIAS_RANGE:
                        if abs(default_near_y - current_y) <= ALLOW_ALIAS_RANGE:
                            current_distance = spline_util.get_distance(default_near_x,default_near_y,current_x,current_y)
                            if current_distance < last_distance:
                                last_distance = current_distance
                                shortest_x = current_x
                                shortest_y = current_y

        return shortest_x, shortest_y

    #purpose: 針對 apply round 的 idx+3 == 'curve' 做調整。
    def adjust_round_idx_3_curve(self,new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)
        if format_dict_array[(idx+3)%nodes_length]['t']=="c":
            old_code_string = format_dict_array[(idx+3)%nodes_length]['code']
            old_code_array = old_code_string.split(' ')

            new_distance = spline_util.get_distance(new_x2,new_y2,format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

            is_convert_to_l = False

            if new_distance <= 35:
                is_convert_to_l = True

            if is_convert_to_l:
                format_dict_array[(idx+3)%nodes_length]['t']="l"
                tmp_code_string = ' %d %d l 1\n' % (format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                old_code_array = tmp_code_string.split(' ')
            else:
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

                is_virtual_dot_need_offset = False
                #is_virtual_dot_need_offset = True

                # 下面的  code 已完全不知道在解決那一個字的那一個問題，直接註解掉。
                if is_virtual_dot_need_offset:
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
            self.apply_code(format_dict_array,(idx+3)%nodes_length)
            #print("before code:", old_code_string)
            #print("new_code code:", new_code)
    
    #purpose: 移動 round 的 idx+1 x,y 坐標。
    def move_round_idx_1_position(self, is_apply_inside_direction, new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
        old_code_array = old_code_string.split(' ')

        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            # for 辶部，的凹洞.
            # PS: 這是檢測水平線，還無法處理斜線型的凹洞。
            is_prefer_y1_straight = False

            if is_apply_inside_direction:
                #print("-1 y_equal_fuzzy:", format_dict_array[(idx-1+nodes_length)%nodes_length]['y_equal_fuzzy'])
                if format_dict_array[(idx-1+nodes_length)%nodes_length]['y_equal_fuzzy']:
                    if format_dict_array[(idx-1+nodes_length)%nodes_length]['x_direction'] == format_dict_array[(idx+0+nodes_length)%nodes_length]['x_direction']:
                        if abs(format_dict_array[(idx+1+nodes_length)%nodes_length]['y2']-format_dict_array[(idx-1+nodes_length)%nodes_length]['y'])<=3:
                            is_prefer_y1_straight = True

            new_distance = spline_util.get_distance(new_x1,new_y1,format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'])

            is_convert_to_l = False

            if new_distance <= 35:
                is_convert_to_l = True

            #print("is_convert_to_l:", is_convert_to_l)
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

                is_virtual_dot_need_offset = False
                #is_virtual_dot_need_offset = True

                if is_virtual_dot_need_offset:
                    # 如果 x1,y1=x2,y2, 順便調整另一組。
                    if old_code_array[1] == old_code_array[3] and old_code_array[2] == old_code_array[4]:
                        old_code_array[1] = str(extend_offset_x)
                        old_code_array[2] = str(extend_offset_y)

                    old_code_array[3] = str(extend_offset_x)
                    old_code_array[4] = str(extend_offset_y)

                # 如果 x1,y1=x,y, 順便調整另一組。
                if old_code_array[1] == old_code_array[5] and old_code_array[2] == old_code_array[6]:
                    old_code_array[1] = str(new_x1)
                    old_code_array[2] = str(new_y1)

                # 如果 x2,y2=x,y, 順便調整另一組。
                if old_code_array[3] == old_code_array[5] and old_code_array[4] == old_code_array[6]:
                    old_code_array[3] = str(new_x1)
                    old_code_array[4] = str(new_y1)

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

        # 增加內縮後的點，為不處理的項目。
        apply_rule_log.append(new_code)
        #print("append code to apply_rule_log:",new_code)
        
        # PS: 千萬不可以把這個 idx+1 內縮後的點列為 generate rule log 裡，會造成 rule#5 fail.
        #generate_rule_log.append(new_code)

        #if True:
        if False:
            print("old_code_string:", old_code_string)
            print("is_prefer_y1_straight:", is_prefer_y1_straight)
            print("+1 idx:%d, code:%s" % (target_index, new_code))

    #purpose: 移動 round 的 idx+2 x,y 坐標。
    def move_round_idx_2_position(self,new_x2,new_y2,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            new_distance = spline_util.get_distance(new_x2,new_y2,format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

            is_convert_to_l = False

            if new_distance <= 35:
                is_convert_to_l = True

            if is_convert_to_l:
                # change type.
                format_dict_array[(idx+3)%nodes_length]['t']="l"
                # change code.
                tmp_code_string = ' %d %d l 1\n' % (format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                format_dict_array[(idx+3)%nodes_length]['code'] = tmp_code_string
                self.apply_code(format_dict_array,(idx+3)%nodes_length)

        old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
        old_code_array = old_code_string.split(' ')

        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
            old_code_array[5] = str(new_x2)
            old_code_array[6] = str(new_y2)
        else:
            # not is 'c'
            old_code_array[1] = str(new_x2)
            old_code_array[2] = str(new_y2)
        new_code = ' '.join(old_code_array)
        format_dict_array[(idx+2)%nodes_length]['code'] = new_code
        self.apply_code(format_dict_array,(idx+2)%nodes_length)

        # 增加內縮後的點，為不處理的項目。
        # PS: idx+2 是共用點，不能直接加入為不處理節點！
        if old_code_string in apply_rule_log:
            apply_rule_log.append(new_code)

        if old_code_string in generate_rule_log:
            # PS: 千萬不可以把這個 idx+2 內縮後的點「直接」列為 generate rule log 裡
            generate_rule_log.append(new_code)

        #if True:
        if False:
            print("old_code_string:", old_code_string)
            print("is_prefer_y1_straight:", is_prefer_y1_straight)
            print("+1 idx:%d, code:%s" % (target_index, new_code))

    # for rectangel version. ex: rule#1,#2,#3
    # for common round transform.
    def apply_round_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        round_length_1 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # default apply inside direction.
        is_apply_inside_direction = True
        if self.config.PROCESS_MODE in ["BAT"]:
            is_apply_inside_direction = False

        # use more close coordinate.
        new_x1, new_y1 = 0,0
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)

        new_x2, new_y2 = 0,0
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x3,y3,round_length_2)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x3,y3才對。
                new_x2, new_y2 = x3, y3
            else:
                new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2, round_length_2)
        else:
            if is_apply_inside_direction:
                new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2,-1 * round_length_2)
            else:
                new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2, round_length_2)

        # compute edge 1 prefer.
        prefer_orig_1 = False
        if False:
            clockwise1 = self.check_clockwise([[orig_x0,orig_y0],[x1,y1],[x2,y2]])
            clockwise1V = None
            if format_dict_array[(idx+1)%nodes_length]['t']=='l':
                clockwise1V = clockwise1
            else:
                x_center = format_dict_array[(idx+1)%nodes_length]['x2']
                y_center = format_dict_array[(idx+1)%nodes_length]['y2']
                clockwise1V = self.check_clockwise([[orig_x0,orig_y0],[x1,y1],[x_center,y_center]])
            if clockwise1V == clockwise1:
                prefer_orig_1 = True

            if False:
                print("clockwise1:", clockwise1)
                print("clockwise1V:", clockwise1V)

        # compute edge 3 prefer.
        prefer_orig_3 = False
        if False:
            clockwise3 = self.check_clockwise([[x1,y1],[x2,y2],[orig_x3,orig_y3]])
            clockwise3V = None
            if format_dict_array[(idx+3)%nodes_length]['t']=='l':
                clockwise3V = clockwise3
            else:
                x_center = format_dict_array[(idx+3)%nodes_length]['x1']
                y_center = format_dict_array[(idx+3)%nodes_length]['y1']
                clockwise3V = self.check_clockwise([[x2,y2],[orig_x3,orig_y3],[x_center,y_center]])
            if clockwise3V == clockwise3:
                prefer_orig_3 = True

            if False:
                print("clockwise3:", clockwise3)
                print("clockwise3V:", clockwise3V)

        #if True:
        if False:
            print("center x,y:", center_x, center_y)

            print("orig orig_x0,orig_y0:", orig_x0,orig_y0)
            print("new x0,y0 goto x1,y1:", x0,y0, x1,y1)
            print("compute new_x1, new_y1:", new_x1, new_y1)

            print("orig_x3,orig_y3:",orig_x3,orig_y3)
            print("x2,y2 goto x3,y3:",x2,y2, x3,y3)
            print("compute new_x2, new_y2:", new_x2, new_y2)

            #print("prefer_orig_1:",prefer_orig_1)
            #print("prefer_orig_3:",prefer_orig_3)

        # re-center again.
        if False:
            if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                x_center = format_dict_array[(idx+1)%nodes_length]['x2']
                y_center = format_dict_array[(idx+1)%nodes_length]['y2']
                if prefer_orig_1:
                    x_center = (orig_x0 + x1)/2
                    y_center = (orig_y0 + y1)/2
                new_x_center, new_y_center = spline_util.two_point_extend(x_center,y_center,x1,y1,-1 * round_length_1)
                new_x1, new_y1 = int((new_x_center+new_x1)/2) , int((new_y_center+new_y1)/2)

        # re-center again.
        if False:
            if format_dict_array[(idx+3)%nodes_length]['t']=='c':
                x_center = format_dict_array[(idx+3)%nodes_length]['x1']
                y_center = format_dict_array[(idx+3)%nodes_length]['y1']
                #print("dot+3:x1,y1:", x_center, y_center)
                if prefer_orig_3:
                    x_center = (orig_x3 + x2)/2
                    y_center = (orig_y3 + y2)/2
                    #print("dot+3 middle:x1,y1:", x_center, y_center)
                new_x_center, new_y_center = spline_util.two_point_extend(x_center,y_center,x2,y2,-1 * round_length_2)
                #print("x2,y2:",x2,y2)
                #print("new_x_center, new_y_center:",new_x_center, new_y_center)
                new_x2, new_y2 = int((new_x_center+new_x2)/2) , int((new_y_center+new_y2)/2)
                #print("new_x2, new_y2(after):",new_x2, new_y2)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        #if True:
        if False:
            print("new x1,y1:", new_x1, new_y1)
            print("new x2,y2:", new_x2, new_y2)

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if is_apply_inside_direction:
            # PS: 目前 round idx+3 和 idx+1 的處理方式不太一樣，但理論上應該要一樣。
            self.adjust_round_idx_3_curve(new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log)

        is_halfmoon_sharp = False
        if self.config.PROCESS_MODE in ["HALFMOON","TOOTHPASTE"]:
            is_halfmoon_sharp = True

        if not is_halfmoon_sharp:
            # PS: 由於 halfmoon + toothpaste 沒有動 idx+1 curver.
            self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

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
            old_code = format_dict_array[target_index]['code']
            format_dict_array[target_index]=dot_dict
            self.apply_code(format_dict_array,target_index)

            #print("update +2 old_code:", old_code)
            #print("update +2 idx:%d, code:%s" % (target_index, new_code))
            apply_rule_log.append(new_code)
            generate_rule_log.append(new_code)

        if is_halfmoon_sharp:
            #print("self.config.PROCESS_MODE in [HALFMOON]")
            # move to left
            #center_x, center_y = spline_util.two_point_extend(x1,y1,orig_x0,orig_y0,-2)
            #center_x, center_y = spline_util.two_point_extend_next(orig_x0,orig_y0,x1,y1)
            center_x, center_y = x1,y1

            # update #2
            new_code = ' %d %d l 1\n' % (center_x, center_y)
            dot_dict={}
            dot_dict['x']=center_x
            dot_dict['y']=center_y
            dot_dict['t']='l'
            dot_dict['code']=new_code
            format_dict_array[(idx+2)%nodes_length]=dot_dict
            self.apply_code(format_dict_array,(idx+2)%nodes_length)
            #print("rule16 new_code:", new_code)
            apply_rule_log.append(new_code)
            generate_rule_log.append(new_code)

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
        #print("insert +3 idx:%d, code:%s" % (target_index, new_code))
        # PS: alought we add new node, but please don't add idx+3 to generat_rule_log or apply_rule_log!

        return center_x,center_y

    # for 3t transform
    def apply_3t_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']

        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']

        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']

        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        round_length_1 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # use more close coordinate.
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)

        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x3,y3,round_length_2)
            #print("x3,y3:",x3,y3)

        new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
        new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2,-1 * round_length_2)


        new_center_x = int((new_x1 + new_x2) / 2)
        new_center_y = int((new_y1 + new_y2) / 2)

        dot1_x = int((new_center_x+new_x1) / 2)
        dot1_y = int((new_center_y+new_y1) / 2)

        dot3_x = int((new_center_x+new_x2) / 2)
        dot3_y = int((new_center_y+new_y2) / 2)

        # convert to l
        new_code = ' %d %d l 1\n' % (x2, y2)
        dot_dict={}
        dot_dict['t']='l'
        dot_dict['code']=new_code
        format_dict_array[(idx+2)%nodes_length]=dot_dict
        self.apply_code(format_dict_array,(idx+2)%nodes_length)

        # append new #1
        new_code = ' %d %d l 1\n' % (dot3_x, dot3_y)
        dot_dict={}
        dot_dict['x']=dot3_x
        dot_dict['y']=dot3_y
        dot_dict['t']='l'
        dot_dict['code']=new_code
        target_index = (idx+2)%nodes_length
        format_dict_array.insert(target_index,dot_dict)
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #2
        new_code = ' %d %d l 1\n' % (center_x, center_y)
        dot_dict={}
        dot_dict['x']=center_x
        dot_dict['y']=center_y
        dot_dict['t']='l'
        dot_dict['code']=new_code
        target_index = (idx+2)%nodes_length
        format_dict_array.insert(target_index,dot_dict)
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #3
        new_code = ' %d %d l 1\n' % (dot1_x, dot1_y)
        dot_dict={}
        dot_dict['x']=dot1_x
        dot_dict['y']=dot1_y
        dot_dict['t']='l'
        dot_dict['code']=new_code
        target_index = (idx+2)%nodes_length
        format_dict_array.insert(target_index,dot_dict)
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        return center_x,center_y

    # for gospel transform
    def apply_gospel_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        # PS: 目前 GOSPEL 不會使用到 BAT 的效果。
        #     但由於code 想要共用，所以暫時以常數來解決code共用問題.
        is_apply_inside_direction = True

        if self.config.PROCESS_MODE in ["SHEAR"]:
            is_apply_inside_direction = False

        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']

        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']

        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']

        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        round_length_1 = self.config.INSIDE_ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']

        # use more close coordinate.
        new_x1, new_y1 = 0,0
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1

        self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

        gospel_x, gospel_y = spline_util.two_point_extend(x2,y2,x1,y1, self.config.INSIDE_ROUND_OFFSET)

        # update #2
        is_append_node = True
        if self.config.PROCESS_MODE in ["SHEAR"]:
            is_append_node = False

        is_move_idx_2_position = False
        if self.config.PROCESS_MODE in ["SHEAR"]:
            is_move_idx_2_position = True

        if is_move_idx_2_position:
            round_length_2 = self.config.INSIDE_ROUND_OFFSET
            if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
                round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

            new_x2, new_y2 = 0,0
            if format_dict_array[(idx+3)%nodes_length]['t']=='c':
                x_from = x2
                y_from = y2
                x_center = format_dict_array[(idx+3)%nodes_length]['x1']
                y_center = format_dict_array[(idx+3)%nodes_length]['y1']
                #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
                x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,x3,y3,round_length_2)
                #print("x3,y3:",x3,y3)
                # 應該是可以直接使用 x3,y3才對，但目前還有問題。
                #new_x2, new_y2 = x3, y3

                #if is_apply_inside_direction:
                # always move to inside.
                if True:
                    new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2,-1 * round_length_2)
                else:
                    new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2, round_length_2)
            else:
                #if is_apply_inside_direction:
                # always move to inside.
                if True:
                    new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2,-1 * round_length_2)
                else:
                    new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2, round_length_2)

            #print("new_x2, new_y2:", new_x2, new_y2)
            self.move_round_idx_2_position(new_x2,new_y2,format_dict_array,idx,apply_rule_log,generate_rule_log)

        if is_append_node:
            new_code = ' %d %d l 1\n' % (gospel_x, gospel_y)
            dot_dict={}
            dot_dict['x']=gospel_x
            dot_dict['y']=gospel_y
            dot_dict['t']='l'
            dot_dict['code']=new_code
            format_dict_array.insert((idx+2)%nodes_length,dot_dict)
            #format_dict_array[(idx+2)%nodes_length]=dot_dict
            self.apply_code(format_dict_array,(idx+2)%nodes_length)
            apply_rule_log.append(new_code)
            generate_rule_log.append(new_code)

        return center_x,center_y

    # for fist transform
    def apply_fist_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        round_length_1 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # 理論上應該不會遇到.
        # avoid error.
        if round_length_1 <2:
            round_length_1 =2
        if round_length_2 <2:
            round_length_2 =2

        # default apply inside direction.
        is_apply_inside_direction = True

        # use more close coordinate.
        new_x1, new_y1 = 0,0
        fist_idx_1_center_x,fist_idx_1_center_y = 0,0
        fist_idx_1_end_x,fist_idx_1_end_y = 0,0

        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
                fist_idx_1_center_x, fist_idx_1_center_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,int(round_length_1 * 0.5))
                fist_idx_1_end_x, fist_idx_1_end_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,int(round_length_1 * 0.85))
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * round_length_1)
                fist_idx_1_center_x, fist_idx_1_center_y = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * int(round_length_1 * 0.5))
                fist_idx_1_end_x, fist_idx_1_end_y = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * int(round_length_1 * 0.85))
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)

        new_x2, new_y2 = 0,0
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,round_length_2)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x3,y3才對。
                new_x2, new_y2 = x3, y3
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)
        else:
            if is_apply_inside_direction:
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * round_length_2)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if is_apply_inside_direction:
            # PS: 目前 round idx+3 和 idx+1 的處理方式不太一樣，但理論上應該要一樣。
            self.adjust_round_idx_3_curve(new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log)

        # PS: 由於 halfmoon + toothpaste 沒有動 idx+1 curver.
        self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

        gospel_1_x, gospel_1_y = spline_util.two_point_extend(x2,y2,x1,y1, self.config.INSIDE_ROUND_OFFSET)
        fist_1_end_x_offset = fist_idx_1_end_x - x1
        fist_1_end_y_offset = fist_idx_1_end_y - y1
        fist_1_x = gospel_1_x +fist_1_end_x_offset
        fist_1_y = gospel_1_y +fist_1_end_y_offset

        # update #2
        tail_mode = "CURVE"
        #tail_mode = "LINE"

        new_code = ' %d %d %d %d %d %d c 1\n' % (fist_idx_1_center_x, fist_idx_1_center_y, fist_idx_1_center_x, fist_idx_1_center_y, fist_1_x, fist_1_y)
        dot_dict={}
        dot_dict['x']=fist_1_x
        dot_dict['y']=fist_1_y
        dot_dict['t']='c'

        if tail_mode == "LINE":
            new_code = ' %d %d l 1\n' % (fist_1_x, fist_1_y)
            dot_dict['t']='l'

        # extra attrib for curve.
        #dot_dict['x1']=new_x1
        #dot_dict['y1']=new_y1
        dot_dict['x1']=fist_idx_1_center_x
        dot_dict['y1']=fist_idx_1_center_y
        dot_dict['x2']=fist_idx_1_center_x
        dot_dict['y2']=fist_idx_1_center_y

        dot_dict['code']=new_code

        target_index = (idx+2)%nodes_length
        old_code = format_dict_array[target_index]['code']
        format_dict_array[target_index]=dot_dict
        self.apply_code(format_dict_array,target_index)
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # insert #3
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

        target_index = (idx+3)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+3)%nodes_length
        self.apply_code(format_dict_array,target_index)

        #print("update +2 old_code:", old_code)
        #print("update +2 idx:%d, code:%s" % (target_index, new_code))
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #4
        #new_code = ' %d %d %d %d %d %d c 1\n' % (center_x, center_y, x2, y2, new_x2, new_y2)
        new_code = ' %d %d %d %d %d %d c 1\n' % (x2, y2, x2, y2, new_x2, new_y2)
        dot_dict={}
        dot_dict['x']=new_x2
        dot_dict['y']=new_y2
        dot_dict['t']='c'

        dot_dict['x1']=x2
        dot_dict['y1']=y2
        dot_dict['x2']=x2
        dot_dict['y2']=y2

        dot_dict['code']=new_code
        target_index = (idx+4)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        apply_rule_log.append(new_code)
        #generate_rule_log.append(new_code)

        return center_x,center_y

    # for marker transform
    def apply_marker_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)
        marker_border_default = int(self.config.INSIDE_ROUND_OFFSET * 0.8)

        center_x,center_y = 0,0

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
        round_length_1 = marker_border_default
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        
        round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        round_length_2_short = round_length_2 - marker_border_default
        if round_length_2_short <2:
            round_length_2_short = 2

        # 理論上應該不會遇到.
        # avoid error.
        if round_length_1 <2:
            round_length_1 =2
        if round_length_2 <2:
            round_length_2 =2

        # default apply inside direction.
        is_apply_inside_direction = True


        # use more close coordinate.
        new_x1, new_y1 = 0,0
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1,-1 * round_length_1)
            else:
                new_x1, new_y1 = spline_util.two_point_extend(x0,y0,x1,y1, round_length_1)

        new_x2, new_y2 = 0,0
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,round_length_2)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x3,y3才對。
                new_x2, new_y2 = x3, y3
            else:
                new_x2, new_y2 = spline_util.two_point_extend(x3,y3,x2,y2, round_length_2)
        else:
            if is_apply_inside_direction:
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * round_length_2)
            else:
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)

        new_x2_short, new_y2_short = 0,0
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            new_x2_short, new_y2_short = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,round_length_2_short)
        else:
            if is_apply_inside_direction:
                new_x2_short, new_y2_short = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * round_length_2_short)
            else:
                new_x2_short, new_y2_short = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2_short)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if is_apply_inside_direction:
            # PS: 目前 round idx+3 和 idx+1 的處理方式不太一樣，但理論上應該要一樣。
            self.adjust_round_idx_3_curve(new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log)

        self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

        round_length = marker_border_default
        marker_begin_x, marker_begin_y = spline_util.two_point_extend(new_x2_short,new_y2_short,x1,y1,-1 * round_length)
        marker_end_x, marker_end_y = spline_util.two_point_extend(x1,y1,new_x2_short,new_y2_short,-1 * round_length)

        # update #2
        #new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1, new_y1, x1, y1, center_x, center_y)
        new_code = ' %d %d %d %d %d %d c 1\n' % (x1, y1, x1, y1, marker_begin_x, marker_begin_y)
        dot_dict={}
        dot_dict['x']=marker_begin_x
        dot_dict['y']=marker_begin_y
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
        old_code = format_dict_array[target_index]['code']
        format_dict_array[target_index]=dot_dict
        self.apply_code(format_dict_array,target_index)

        #print("update +2 old_code:", old_code)
        #print("update +2 idx:%d, code:%s" % (target_index, new_code))
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)


        # update #1, convert to l.
        new_code = ' %d %d l 1\n' % (marker_end_x,marker_end_y)
        dot_dict={}
        dot_dict['x']=marker_end_x
        dot_dict['y']=marker_end_y
        dot_dict['t']='l'

        dot_dict['code']=new_code

        target_index = (idx+3)%nodes_length
        #old_code = format_dict_array[target_index]['code']
        #format_dict_array[target_index]=dot_dict
        format_dict_array.insert(target_index,dot_dict)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+3)%nodes_length
        self.apply_code(format_dict_array,target_index)

        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #4
        #new_code = ' %d %d %d %d %d %d c 1\n' % (center_x, center_y, x2, y2, new_x2, new_y2)
        new_code = ' %d %d %d %d %d %d c 1\n' % (new_x2_short, new_y2_short, new_x2_short, new_y2_short, new_x2, new_y2)
        dot_dict={}
        dot_dict['x']=new_x2
        dot_dict['y']=new_y2
        dot_dict['t']='c'

        dot_dict['x1']=new_x2_short
        dot_dict['y1']=new_y2_short
        dot_dict['x2']=new_x2_short
        dot_dict['y2']=new_y2_short

        dot_dict['code']=new_code
        target_index = (idx+4)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        #apply_rule_log.append(new_code)
        #generate_rule_log.append(new_code)

        return center_x,center_y

    # for devil transform
    # for mode: "DEVIL","BELL","AX"
    def apply_devil_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        # PS:在BELL mode,「湖」字的第一點的曲線，會造成S型，所以不能設太長。
        round_length_1 = self.config.ROUND_OFFSET * 1.1
        if self.config.PROCESS_MODE in ["DEVIL"]:
            round_length_1 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        
        round_length_2 = self.config.ROUND_OFFSET * 1.1
        if self.config.PROCESS_MODE in ["DEVIL"]:
            round_length_2 = self.config.ROUND_OFFSET
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # 理論上應該不會遇到.
        # avoid error.
        is_error_occure = False
        if round_length_1 <= 5:
            is_error_occure = True
        if round_length_2 <= 5:
            is_error_occure = True
        if is_error_occure:
            # directly exit function.
            return center_x,center_y

        # default apply inside direction.
        is_apply_inside_direction = True

        # use more close coordinate.
        new_x1, new_y1 = x1,y1
        fist_idx_1_center_x,fist_idx_1_center_y = x1,y1
        fist_idx_1_end_x, fist_idx_1_end_y = x1,y1

        middle_offset_rate = 0.5
        sharp_offset_rate = 0
        if self.config.PROCESS_MODE in ["DEVIL"]:
            sharp_offset_rate = 0.85
        if self.config.PROCESS_MODE in ["AX"]:
            middle_offset_rate = 0.666
            sharp_offset_rate = 0.333
        if self.config.PROCESS_MODE in ["BONE"]:
            middle_offset_rate = 0.5
            #sharp_offset_rate = 0.2

        middle_offset_1_length = int(round_length_1 * middle_offset_rate)
        sharp_offset_1_length = int(round_length_1 * sharp_offset_rate)

        middle_offset_2_length = int(round_length_2 * middle_offset_rate)
        sharp_offset_2_length = int(round_length_2 * sharp_offset_rate)

        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
                
                fist_idx_1_center_x, fist_idx_1_center_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,middle_offset_1_length)
                if sharp_offset_1_length > 0:
                    fist_idx_1_end_x, fist_idx_1_end_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,sharp_offset_1_length)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * round_length_1)
                
                fist_idx_1_center_x, fist_idx_1_center_y = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * middle_offset_1_length)
                if sharp_offset_1_length > 0:
                    fist_idx_1_end_x, fist_idx_1_end_y = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * sharp_offset_1_length)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)

        new_x2, new_y2 = x2,y2
        fist_idx_3_center_x,fist_idx_3_center_y = x2,y2
        fist_idx_3_end_x,fist_idx_3_end_y = x2,y2

        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,round_length_2)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x3,y3才對。
                new_x2, new_y2 = x3, y3

                fist_idx_3_center_x, fist_idx_3_center_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,middle_offset_2_length)
                if sharp_offset_2_length > 0:
                    fist_idx_3_end_x, fist_idx_3_end_y = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,sharp_offset_2_length)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)
        else:
            if is_apply_inside_direction:
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * round_length_2)

                fist_idx_3_center_x, fist_idx_3_center_y = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * middle_offset_2_length)
                if sharp_offset_2_length > 0:
                    fist_idx_3_end_x, fist_idx_3_end_y = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * sharp_offset_2_length)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if is_apply_inside_direction:
            # PS: 目前 round idx+3 和 idx+1 的處理方式不太一樣，但理論上應該要一樣。
            self.adjust_round_idx_3_curve(new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log)

        # 下面的副程式會順便加入 idx+1 進 apply_rule_log.
        self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

        # PS:「湖」字的第一點的曲線，會造成S型，所以不能設太長。
        # PS: 低於或等於 1.0 效果不太顯著，會無感。
        gospel_offset_length = int(format_dict_array[(idx+1)%nodes_length]['distance'] * 0.12)
        if self.config.PROCESS_MODE in ["DEVIL","AX","BONE"]:
            gospel_offset_length = self.config.INSIDE_ROUND_OFFSET

        gospel_1_x, gospel_1_y = spline_util.two_point_extend(x2,y2,x1,y1, gospel_offset_length)
        fist_1_end_x_offset = fist_idx_1_end_x - x1
        fist_1_end_y_offset = fist_idx_1_end_y - y1
        fist_1_x = gospel_1_x + fist_1_end_x_offset
        fist_1_y = gospel_1_y + fist_1_end_y_offset

        gospel_3_x, gospel_3_y = spline_util.two_point_extend(x1,y1,x2,y2, gospel_offset_length)
        fist_3_end_x_offset = fist_idx_3_end_x - x2
        fist_3_end_y_offset = fist_idx_3_end_y - y2
        fist_3_x = gospel_3_x + fist_3_end_x_offset
        fist_3_y = gospel_3_y + fist_3_end_y_offset

        # for bone.
        gospel_1_x_offset = gospel_1_x - x1
        gospel_1_y_offset = gospel_1_y - y1
        gospel_3_x_offset = gospel_3_x - x2
        gospel_3_y_offset = gospel_3_y - y2

        bone_ass_1_inside_x = int((x1+center_x)/2)
        bone_ass_1_inside_y = int((y1+center_y)/2)

        bone_ass_1_outside_x = int((x1+gospel_1_x)/2)
        bone_ass_1_outside_y = int((y1+gospel_1_y)/2)

        bone_ass_2_inside_x = int((x2+center_x)/2)
        bone_ass_2_inside_y = int((y2+center_y)/2)

        bone_ass_2_outside_x = int((x2+gospel_3_x)/2)
        bone_ass_2_outside_y = int((y2+gospel_3_y)/2)

        #bone_ass_1_x1 = bone_ass_1_inside_x - fist_1_end_x_offset
        #bone_ass_1_x1 = x1 - fist_1_end_x_offset
        bone_ass_1_x1 = x1 - int(x1_offset/2)
        bone_ass_1_x2 = bone_ass_1_x1

        #bone_ass_1_y1 = bone_ass_1_inside_y - fist_1_end_y_offset
        #bone_ass_1_y1 = y1 - fist_1_end_y_offset
        bone_ass_1_y1 = y1 - int(y1_offset/2)
        bone_ass_1_y2 = bone_ass_1_y1

        #bone_ass_2_x1 = bone_ass_2_inside_x - fist_3_end_x_offset
        #bone_ass_2_x1 = x2 - fist_3_end_x_offset
        bone_ass_2_x1 = x2 - int(x2_offset/2)
        bone_ass_2_x2 = bone_ass_2_x1

        #bone_ass_2_y1 = bone_ass_2_inside_y - fist_3_end_y_offset
        #bone_ass_2_y1 = y2 - fist_3_end_y_offset
        bone_ass_2_y1 = y2 - int(y2_offset/2)
        bone_ass_2_y2 = bone_ass_2_y1

        # for BONE mode.
        bone_extra_node_1_x = fist_idx_1_center_x + gospel_1_x_offset
        bone_extra_node_1_y = fist_idx_1_center_y + gospel_1_y_offset
        if self.config.PROCESS_MODE in ["BONE"]:
            # shift fist_idx_1_center_x/fist_idx_1_center_y
            orig_fist_idx_1_center_x = (fist_idx_1_center_x + new_x1)/2
            orig_fist_idx_1_center_y = (fist_idx_1_center_y + new_y1)/2

            new_fist_idx_1_center_x = (fist_idx_1_center_x + bone_extra_node_1_x)/2
            new_fist_idx_1_center_y = (fist_idx_1_center_y + bone_extra_node_1_y)/2

            new_fist_idx_1_center_x = (new_fist_idx_1_center_x + orig_fist_idx_1_center_x)/2
            new_fist_idx_1_center_y = (new_fist_idx_1_center_y + orig_fist_idx_1_center_y)/2

            fist_idx_1_center_x = int(new_fist_idx_1_center_x)
            fist_idx_1_center_y = int(new_fist_idx_1_center_y)


        # update #2
        # curve mode for AX,BELL mode.
        tail_short_mode = "CURVE"
        if self.config.PROCESS_MODE in ["DEVIL"]:
            tail_short_mode = "LINE"
        
        # curve mode for AX,BELL mode.
        tail_long_mode = "CURVE"
        if self.config.PROCESS_MODE in ["DEVIL","BELL"]:
            tail_long_mode = "LINE"

        # round mode.
        new_code = ' %d %d %d %d %d %d c 1\n' % (fist_idx_1_center_x, fist_idx_1_center_y, fist_idx_1_center_x, fist_idx_1_center_y, fist_1_x, fist_1_y)
        dot_dict={}
        dot_dict['x']=fist_1_x
        dot_dict['y']=fist_1_y

        # insert new internal node.
        if self.config.PROCESS_MODE in ["BONE"]:
            new_code = ' %d %d %d %d %d %d c 1\n' % (fist_idx_1_center_x, fist_idx_1_center_y, fist_idx_1_center_x, fist_idx_1_center_y, bone_extra_node_1_x, bone_extra_node_1_y)
            dot_dict['x']=bone_extra_node_1_x
            dot_dict['y']=bone_extra_node_1_y

        if tail_short_mode == "LINE":
            # line mode.
            new_code = ' %d %d l 1\n' % (fist_1_x, fist_1_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=fist_idx_1_center_x
            dot_dict['y1']=fist_idx_1_center_y
            dot_dict['x2']=fist_idx_1_center_x
            dot_dict['y2']=fist_idx_1_center_y

        dot_dict['code']=new_code

        target_index = (idx+2)%nodes_length
        old_code = format_dict_array[target_index]['code']
        format_dict_array[target_index]=dot_dict
        self.apply_code(format_dict_array,target_index)

        #print("view idx+1 new code:", format_dict_array[(idx+1)%nodes_length]['code'])
        #print("assign idx+2 new code:", new_code)
        
        apply_rule_log.append(new_code)
        # PS: TODO: uni970B 的妻，還有一個地方沒套到效果。
        #   : 似乎與下一行無關。
        generate_rule_log.append(new_code)


        # for BONE mode. #2.5
        # extra #2.5 for BONE mode.
        if self.config.PROCESS_MODE in ["BONE"]:
            bone_fat_center_x = int((fist_1_x + bone_extra_node_1_x)/2)
            bone_fat_center_y = int((fist_1_y + bone_extra_node_1_y)/2)

            bone_fat_outside_x = bone_fat_center_x + int(gospel_1_x_offset/2)
            bone_fat_outside_y = bone_fat_center_y + int(gospel_1_y_offset/2)

            new_code = ' %d %d %d %d %d %d c 1\n' % (bone_fat_outside_x, bone_fat_outside_y, bone_fat_outside_x, bone_fat_outside_y, fist_1_x, fist_1_y)
            dot_dict={}
            dot_dict['x']=fist_1_x
            dot_dict['y']=fist_1_y
            
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=bone_fat_outside_x
            dot_dict['y1']=bone_fat_outside_y
            dot_dict['x2']=bone_fat_outside_x
            dot_dict['y2']=bone_fat_outside_y

            dot_dict['code']=new_code
            target_index = (idx+3)%nodes_length
            format_dict_array.insert(target_index,dot_dict)

            apply_rule_log.append(new_code)
            generate_rule_log.append(new_code)

            nodes_length = len(format_dict_array)
            if idx >= target_index:
                idx += 1

            target_index = (idx+3)%nodes_length
            self.apply_code(format_dict_array,target_index)

        # insert #3
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (x1, y1, x1, y1, center_x, center_y)
        
        if self.config.PROCESS_MODE in ["BONE"]:
            new_code = ' %d %d %d %d %d %d c 1\n' % (bone_ass_1_x1, bone_ass_1_y1, bone_ass_1_x2, bone_ass_1_y2, center_x, center_y)

        dot_dict={}
        dot_dict['x']=center_x
        dot_dict['y']=center_y
        
        if tail_long_mode == "LINE":
            # line
            new_code = ' %d %d l 1\n' % (center_x, center_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=x1
            dot_dict['y1']=y1
            dot_dict['x2']=x1
            dot_dict['y2']=y1
            if self.config.PROCESS_MODE in ["BONE"]:
                dot_dict['x1']=bone_ass_1_x1
                dot_dict['y1']=bone_ass_1_y1
                dot_dict['x2']=bone_ass_1_x2
                dot_dict['y2']=bone_ass_1_y2

        dot_dict['code']=new_code

        target_index = (idx+3)%nodes_length
        if self.config.PROCESS_MODE in ["BONE"]:
            target_index = (idx+4)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+3)%nodes_length
        if self.config.PROCESS_MODE in ["BONE"]:
            target_index = (idx+4)%nodes_length
        self.apply_code(format_dict_array,target_index)

        #print("update +2 old_code:", old_code)
        #print("update +2 idx:%d, code:%s" % (target_index, new_code))
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #4
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (x2, y2, x2, y2, fist_3_x, fist_3_y)

        if self.config.PROCESS_MODE in ["BONE"]:
            new_code = ' %d %d %d %d %d %d c 1\n' % (bone_ass_2_x1, bone_ass_2_y1, bone_ass_2_x2, bone_ass_2_y2, fist_3_x, fist_3_y)

        dot_dict={}
        dot_dict['x']=fist_3_x
        dot_dict['y']=fist_3_y

        if tail_long_mode == "LINE":
            # line
            new_code = ' %d %d l 1\n' % (fist_3_x, fist_3_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            dot_dict['x1']=x2
            dot_dict['y1']=y2
            dot_dict['x2']=x2
            dot_dict['y2']=y2
            if self.config.PROCESS_MODE in ["BONE"]:
                dot_dict['x1']=bone_ass_2_x1
                dot_dict['y1']=bone_ass_2_y1
                dot_dict['x2']=bone_ass_2_x2
                dot_dict['y2']=bone_ass_2_y2

        dot_dict['code']=new_code
        target_index = (idx+4)%nodes_length
        if self.config.PROCESS_MODE in ["BONE"]:
            target_index = (idx+5)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+4)%nodes_length
        if self.config.PROCESS_MODE in ["BONE"]:
            target_index = (idx+5)%nodes_length
        self.apply_code(format_dict_array,target_index)

        
        # extra #4.5 for BONE mode.
        if self.config.PROCESS_MODE in ["BONE"]:
            bone_extra_node_3_x = fist_idx_3_center_x + gospel_3_x_offset
            bone_extra_node_3_y = fist_idx_3_center_y + gospel_3_y_offset

            bone_fat_center_x = int((fist_3_x + bone_extra_node_3_x)/2)
            bone_fat_center_y = int((fist_3_y + bone_extra_node_3_y)/2)

            bone_fat_outside_x = bone_fat_center_x + int(gospel_3_x_offset/2)
            bone_fat_outside_y = bone_fat_center_y + int(gospel_3_y_offset/2)

            new_code = ' %d %d %d %d %d %d c 1\n' % (bone_fat_outside_x, bone_fat_outside_y, bone_fat_outside_x, bone_fat_outside_y, bone_extra_node_3_x, bone_extra_node_3_y)
            dot_dict={}
            dot_dict['x']=bone_extra_node_3_x
            dot_dict['y']=bone_extra_node_3_y
            
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=bone_fat_outside_x
            dot_dict['y1']=bone_fat_outside_y
            dot_dict['x2']=bone_fat_outside_x
            dot_dict['y2']=bone_fat_outside_y

            dot_dict['code']=new_code
            target_index = (idx+6)%nodes_length
            format_dict_array.insert(target_index,dot_dict)

            apply_rule_log.append(new_code)
            generate_rule_log.append(new_code)

            nodes_length = len(format_dict_array)
            if idx >= target_index:
                idx += 1

            target_index = (idx+6)%nodes_length
            self.apply_code(format_dict_array,target_index)

            # shift fist_idx_3_center_x/fist_idx_3_center_y
            orig_fist_idx_3_center_x = (fist_idx_3_center_x + new_x2)/2
            orig_fist_idx_3_center_y = (fist_idx_3_center_y + new_y2)/2

            new_fist_idx_3_center_x = (fist_idx_3_center_x + bone_extra_node_3_x)/2
            new_fist_idx_3_center_y = (fist_idx_3_center_y + bone_extra_node_3_y)/2

            new_fist_idx_3_center_x = (new_fist_idx_3_center_x + orig_fist_idx_3_center_x)/2
            new_fist_idx_3_center_y = (new_fist_idx_3_center_y + orig_fist_idx_3_center_y)/2

            fist_idx_3_center_x = int(new_fist_idx_3_center_x)
            fist_idx_3_center_y = int(new_fist_idx_3_center_y)

        # append new #5
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (fist_idx_3_center_x, fist_idx_3_center_y, fist_idx_3_center_x, fist_idx_3_center_y, new_x2, new_y2)
        dot_dict={}
        dot_dict['x']=new_x2
        dot_dict['y']=new_y2

        if tail_short_mode == "LINE":
            # line mode.
            new_code = ' %d %d l 1\n' % (new_x2, new_y2)
            dot_dict['t']='l'
        else:
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=fist_idx_3_center_x
            dot_dict['y1']=fist_idx_3_center_y
            dot_dict['x2']=fist_idx_3_center_x
            dot_dict['y2']=fist_idx_3_center_y

        dot_dict['code']=new_code
        target_index = (idx+5)%nodes_length
        if self.config.PROCESS_MODE in ["BONE"]:
            target_index = (idx+7)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        # PS: (idx+5) don't add to rule_log, it cause next dot lose change to transform.
        #apply_rule_log.append(new_code)
        #generate_rule_log.append(new_code)

        return center_x,center_y

    # for matchstick transform
    def apply_matchstick_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        # keep original value.
        orig_x0 = x0
        orig_y0 = y0
        orig_x3 = x3
        orig_y3 = y3

        # 使用較短的邊。
        # PS:在BELL mode,「湖」字的第一點的曲線，會造成S型，所以不能設太長。
        # PS:在MATCH mode,「南」字的羊上的點，round_length_1 設太大會產生出新的side effect.
        # PS:在MATCH mode,「國」字的裡的一，有問題尚未解決.
        round_length_1 = self.config.ROUND_OFFSET * 1.2
        #round_length_1 = self.config.ROUND_OFFSET
        if self.config.PROCESS_MODE in [""]:
            #round_length_1 = self.config.ROUND_OFFSET
            pass
        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_length_1:
            round_length_1 = format_dict_array[(idx+0)%nodes_length]['distance']
        
        round_length_2 = self.config.ROUND_OFFSET * 1.2
        #round_length_2 = self.config.ROUND_OFFSET
        if self.config.PROCESS_MODE in [""]:
            #round_length_2 = self.config.ROUND_OFFSET
            pass
        if format_dict_array[(idx+2)%nodes_length]['distance'] < round_length_2:
            round_length_2 = format_dict_array[(idx+2)%nodes_length]['distance']

        # 理論上應該不會遇到.
        # avoid error.
        is_error_occure = False
        if round_length_1 <= 5:
            is_error_occure = True
        if round_length_2 <= 5:
            is_error_occure = True
        if is_error_occure:
            # directly exit function.
            return center_x,center_y

        # default apply inside direction.
        is_apply_inside_direction = True

        # use more close coordinate.
        new_x1, new_y1 = x1,y1
        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
            x_from = x1
            y_from = y1
            x_center = format_dict_array[(idx+1)%nodes_length]['x2']
            y_center = format_dict_array[(idx+1)%nodes_length]['y2']
            x0,y0 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x0,orig_y0,round_length_1)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x0,y0才對。
                new_x1, new_y1 = x0, y0
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)
        else:
            if is_apply_inside_direction:
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1,-1 * round_length_1)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x1, new_y1 = spline_util.two_point_extend(orig_x0,orig_y0,x1,y1, round_length_1)

        new_x2, new_y2 = x2,y2
        if format_dict_array[(idx+3)%nodes_length]['t']=='c':
            x_from = x2
            y_from = y2
            x_center = format_dict_array[(idx+3)%nodes_length]['x1']
            y_center = format_dict_array[(idx+3)%nodes_length]['y1']
            #print("x_from,y_from,x_center,y_center,x2,y2,round_length_2:",x_from,y_from,x_center,y_center,x2,y2,round_length_2)
            x3,y3 = self.compute_curve_new_xy(x_from,y_from,x_center,y_center,orig_x3,orig_y3,round_length_2)
            if is_apply_inside_direction:
                # 應該是可以直接使用 x3,y3才對。
                new_x2, new_y2 = x3, y3
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)
        else:
            if is_apply_inside_direction:
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2,-1 * round_length_2)
            else:
                # PS: 目前還沒有實作這個情況。
                new_x2, new_y2 = spline_util.two_point_extend(orig_x3,orig_y3,x2,y2, round_length_2)

        x1_offset = new_x1 - x1
        y1_offset = new_y1 - y1
        x2_offset = new_x2 - x2
        y2_offset = new_y2 - y2

        # offset the center_x,y.
        if False:
            new_center_x = int((new_x1 + new_x2) /2)
            new_center_y = int((new_y1 + new_y2) /2)
            center_x_offset = center_x - new_center_x
            center_y_offset = center_y - new_center_y

            match_ass_center_x = center_x + int(center_x_offset/2)
            match_ass_center_y = center_y + int(center_y_offset/2)

            # directly overwrite center_x for MATCH mode.
            center_x = match_ass_center_x
            center_y = match_ass_center_y

        # 下一個點，可能在內縮後的右邊。
        # 這個會產生「奇怪的曲線」
        if is_apply_inside_direction:
            # PS: 目前 round idx+3 和 idx+1 的處理方式不太一樣，但理論上應該要一樣。
            self.adjust_round_idx_3_curve(new_x2,new_y2,x2_offset,y2_offset,orig_x3,orig_y3,format_dict_array,idx,apply_rule_log,generate_rule_log)

        # 下面的副程式會順便加入 idx+1 進 apply_rule_log.
        self.move_round_idx_1_position(is_apply_inside_direction,new_x1,new_y1,x1_offset,y1_offset,format_dict_array,idx,apply_rule_log,generate_rule_log)

        # PS:「湖」字的第一點的曲線，會造成S型，所以不能設太長。
        gospel_offset_length = self.config.INSIDE_ROUND_OFFSET

        gospel_1_x, gospel_1_y = spline_util.two_point_extend(x2,y2,x1,y1, gospel_offset_length)
        gospel_3_x, gospel_3_y = spline_util.two_point_extend(x1,y1,x2,y2, gospel_offset_length)

        gospel_1_x_offset = gospel_1_x - x1
        gospel_1_y_offset = gospel_1_y - y1

        gospel_3_x_offset = gospel_3_x - x2
        gospel_3_y_offset = gospel_3_y - y2

        match_virtual_node_1_x = new_x1 + gospel_1_x_offset
        match_virtual_node_1_y = new_y1 + gospel_1_y_offset

        match_virtual_node_3_x = new_x2 + gospel_3_x_offset
        match_virtual_node_3_y = new_y2 + gospel_3_y_offset

        match_center_node_1_x = int((match_virtual_node_1_x + gospel_1_x)/2)
        match_center_node_1_y = int((match_virtual_node_1_y + gospel_1_y)/2)

        match_center_node_3_x = int((match_virtual_node_3_x + gospel_3_x)/2)
        match_center_node_3_y = int((match_virtual_node_3_y + gospel_3_y)/2)

        # update #2
        # curve mode for MATCH mode.
        tail_short_mode = "CURVE"
        #tail_short_mode = "LINE"
        if self.config.PROCESS_MODE in [""]:
            tail_short_mode = "LINE"
        
        # curve mode for MATCH mode.
        tail_long_mode = "CURVE"
        #tail_long_mode = "LINE"
        if self.config.PROCESS_MODE in [""]:
            tail_long_mode = "LINE"

        # round mode.
        new_code = ' %d %d %d %d %d %d c 1\n' % (match_virtual_node_1_x, match_virtual_node_1_y, match_virtual_node_1_x, match_virtual_node_1_y, match_center_node_1_x, match_center_node_1_y)
        dot_dict={}
        dot_dict['x']=match_center_node_1_x
        dot_dict['y']=match_center_node_1_y

        if tail_short_mode == "LINE":
            # line mode.
            new_code = ' %d %d l 1\n' % (match_center_node_1_x, match_center_node_1_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=match_virtual_node_1_x
            dot_dict['y1']=match_virtual_node_1_y
            dot_dict['x2']=match_virtual_node_1_x
            dot_dict['y2']=match_virtual_node_1_y

        dot_dict['code']=new_code

        target_index = (idx+2)%nodes_length
        old_code = format_dict_array[target_index]['code']
        format_dict_array[target_index]=dot_dict
        self.apply_code(format_dict_array,target_index)

        #print("view idx+1 new code:", format_dict_array[(idx+1)%nodes_length]['code'])
        #print("assign idx+2 new code:", new_code)
        
        apply_rule_log.append(new_code)
        # PS: TODO: uni970B 的妻，還有一個地方沒套到效果。
        #   : 似乎與下一行無關。
        generate_rule_log.append(new_code)

        # insert #3
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (gospel_1_x, gospel_1_y, gospel_1_x, gospel_1_y, center_x, center_y)
        
        dot_dict={}
        dot_dict['x']=center_x
        dot_dict['y']=center_y
        
        if tail_long_mode == "LINE":
            # line
            new_code = ' %d %d l 1\n' % (center_x, center_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=gospel_1_x
            dot_dict['y1']=gospel_1_y
            dot_dict['x2']=gospel_1_x
            dot_dict['y2']=gospel_1_y

        dot_dict['code']=new_code

        target_index = (idx+3)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+3)%nodes_length
        self.apply_code(format_dict_array,target_index)

        #print("update +2 old_code:", old_code)
        #print("update +2 idx:%d, code:%s" % (target_index, new_code))
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        # append new #4
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (gospel_3_x, gospel_3_y, gospel_3_x, gospel_3_y, match_center_node_3_x, match_center_node_3_y)

        dot_dict={}
        dot_dict['x']=match_center_node_3_x
        dot_dict['y']=match_center_node_3_y

        if tail_long_mode == "LINE":
            # line
            new_code = ' %d %d l 1\n' % (match_center_node_3_x, match_center_node_3_y)
            dot_dict['t']='l'
        else:
            # round
            dot_dict['t']='c'

            dot_dict['x1']=gospel_3_x
            dot_dict['y1']=gospel_3_y
            dot_dict['x2']=gospel_3_x
            dot_dict['y2']=gospel_3_y

        dot_dict['code']=new_code
        target_index = (idx+4)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        nodes_length = len(format_dict_array)
        if idx >= target_index:
            idx += 1

        target_index = (idx+4)%nodes_length
        self.apply_code(format_dict_array,target_index)

        # append new #5
        # round
        new_code = ' %d %d %d %d %d %d c 1\n' % (match_virtual_node_3_x, match_virtual_node_3_y, match_virtual_node_3_x, match_virtual_node_3_y, new_x2, new_y2)
        dot_dict={}
        dot_dict['x']=new_x2
        dot_dict['y']=new_y2

        if tail_short_mode == "LINE":
            # line mode.
            new_code = ' %d %d l 1\n' % (new_x2, new_y2)
            dot_dict['t']='l'
        else:
            dot_dict['t']='c'

            # extra attrib for curve.
            #dot_dict['x1']=new_x1
            #dot_dict['y1']=new_y1
            dot_dict['x1']=match_virtual_node_3_x
            dot_dict['y1']=match_virtual_node_3_y
            dot_dict['x2']=match_virtual_node_3_x
            dot_dict['y2']=match_virtual_node_3_y

        dot_dict['code']=new_code
        target_index = (idx+5)%nodes_length
        format_dict_array.insert(target_index,dot_dict)

        # PS: (idx+5) don't add to rule_log, it cause next dot lose change to transform.
        #apply_rule_log.append(new_code)
        #generate_rule_log.append(new_code)

        return center_x,center_y

    # for dart transform
    # TODO: uni97B7.glyph 的鬲，會出錯，需再檢查是否有 counter-clockwise inside.
    def apply_dart_transform(self,format_dict_array,idx,apply_rule_log,generate_rule_log):
        nodes_length = len(format_dict_array)

        x0 = format_dict_array[(idx+0)%nodes_length]['x']
        y0 = format_dict_array[(idx+0)%nodes_length]['y']
        x1 = format_dict_array[(idx+1)%nodes_length]['x']
        y1 = format_dict_array[(idx+1)%nodes_length]['y']
        x2 = format_dict_array[(idx+2)%nodes_length]['x']
        y2 = format_dict_array[(idx+2)%nodes_length]['y']
        x3 = format_dict_array[(idx+3)%nodes_length]['x']
        y3 = format_dict_array[(idx+3)%nodes_length]['y']

        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)

        old_code = format_dict_array[(idx+1)%nodes_length]['code']
        old_code_array = old_code.split(' ')
        if ' c ' in old_code:
            old_code_array[5]=str(center_x)
            old_code_array[6]=str(center_y)
        else:
            old_code_array[1]=str(center_x)
            old_code_array[2]=str(center_y)
        new_code = ' '.join(old_code_array)

        format_dict_array[(idx+1)%nodes_length]['code'] = new_code
        target_index = (idx+1)%nodes_length
        self.apply_code(format_dict_array,target_index)

        #print("view idx+1 new code:", format_dict_array[(idx+1)%nodes_length]['code'])
        #print("assign idx+2 new code:", new_code)
        
        apply_rule_log.append(new_code)
        generate_rule_log.append(new_code)

        del format_dict_array[(idx+2)%nodes_length]

        return center_x,center_y

    # PS: 數學沒學好，所以開始亂寫，這應該是用函數來處理的。
    # PS: 這個目前已經改用貝茲函數，特別感謝第三方package 的作者。
    def compute_curve_with_bonus(self, x_from, y_from, x_end, y_end, round_offset, x_center,y_center):
        new_x,new_y = 0,0
        direct_distance_full = spline_util.get_distance(x_from, y_from, x_end, y_end)

        middle_x = (x_from + x_end) /2
        middle_y = (y_from + y_end) /2

        bonus_middle_x = (x_center + x_end) /2
        bonus_middle_y = (y_center + y_end) /2

        bonus_x = (middle_x + bonus_middle_x) /2
        bonus_y = (middle_y + bonus_middle_y) /2

        bonus_distance_full = spline_util.get_distance(bonus_x, bonus_y, x_end, y_end)

        is_bonus_mode = False

        # 哎，完全無法理解下面這些數字在寫什麼。
        # 應該 google 一下曲線函數的寫法。
        if direct_distance_full >= 60:
            if bonus_distance_full >= 30:
                if round_offset >= 10:
                    is_bonus_mode = True

        if False:
            print("direct_distance_full:", direct_distance_full)
            print("bonus_distance_full:", bonus_distance_full)
            print("round_offset:", round_offset)
            print("is_bonus_mode:", is_bonus_mode)

        is_bonus_mode = False
        if not is_bonus_mode:
            # without bonus.
            new_round_offset = round_offset
            if new_round_offset > direct_distance_full:
                new_round_offset = direct_distance_full
            new_x,new_y=spline_util.two_point_extend(x_from, y_from, x_end, y_end, -1 * new_round_offset)
        else:
            # work with bonus.
            direct_length = round_offset
            is_high_bonus = False
            if direct_length >= (direct_distance_full * 0.5):
                is_high_bonus = True
            direct_length = abs((direct_distance_full * 0.5) - direct_length)
            direct_percent = direct_length / direct_distance_full
            bonus_length = bonus_distance_full * direct_percent

            if bonus_length <=2:
                new_x,new_y = bonus_x,bonus_y
            else:
                # PS: bonus_length == 0 會出問題。
                # PS: 呼叫函數前，請先確定 distance_offset 不為 0，因為無法判斷要放在 from 還是 end.
                if is_high_bonus:
                    new_x,new_y=spline_util.two_point_extend(x_from, y_from, bonus_x, bonus_y, bonus_length)
                else:
                    #PS: 測下面這行 code, 可以使用 uni97FA 韺的英部件測試。
                    new_x,new_y=spline_util.two_point_extend(x_end, y_end, bonus_x, bonus_y, -1 * bonus_length)

            if False:
                print("is_high_bonus:", is_high_bonus)
                print("bonus_length:", bonus_length)
                print("x_from, y_from, bonus_x, bonus_y, bonus_length:", x_from, y_from, bonus_x, bonus_y, bonus_length)
                print("x_end, y_end, bonus_x, bonus_y, bonus_length:", x_end, y_end, bonus_x, bonus_y, bonus_length)
                print("new_x,new_y:", new_x,new_y)

        return new_x,new_y

    # 角度的影響，修改為取決於距離長度。
    def compute_curve_new_xy(self,x_from,y_from,x_center,y_center,x_end,y_end,round_offset):
        distance_full = spline_util.get_distance(x_from,y_from,x_end,y_end)
        
        round_offset_rate = 0.5
        previous_x,previous_y=x_center,y_center

        if distance_full > 1:
            if round_offset > distance_full:
                round_offset = distance_full
            round_offset_rate = round_offset / distance_full

        nodes = np.asfortranarray([
            [float(x_from), float(x_center), float(x_end)],
            [float(y_from), float(y_center), float(y_end)],
        ])
        curve = bezier.Curve(nodes, degree=2)

        point_offset = curve.evaluate(round_offset_rate)
        previous_x,previous_y=int(point_offset[0]),int(point_offset[1])

        output_debug_message = False
        #output_debug_message = True
        if output_debug_message:
            print("x_from,y_from,x_center,y_center,x_end,y_end:",x_from,y_from,x_center,y_center,x_end,y_end)
            print("distance_full:",distance_full)
            print("round_offset:",round_offset)
            print("round_offset_rate:",round_offset_rate)
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
                    fail_code = 2211
                    is_match_pattern = True
                    going_right = False

        if not is_match_pattern:
            # \ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                fail_code = 2221
                is_match_pattern = True
                going_right = False


        return going_right, fail_code

    # purpose: check for RightBottom base rule.
    # return:
    #   True: match, path going RightBottom.
    #   False: not match.
    def going_rightbottom_direction(self, format_dict_array, idx):
        going_direction = True
        is_match_pattern = False
        fail_code = 0

        nodes_length = len(format_dict_array)

        if not is_match_pattern:
            # - sharp.
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                    fail_code = 2201
                    is_match_pattern = True
                    going_direction = False
                else:
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                            fail_code = 2202
                            is_match_pattern = True
                            going_direction = False

        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                    fail_code = 2211
                    is_match_pattern = True
                    going_direction = False
                else:
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                        fail_code = 2212
                        is_match_pattern = True
                        going_direction = False

        if not is_match_pattern:
            # \ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                fail_code = 2221
                is_match_pattern = True
                going_direction = False

            if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                fail_code = 2222
                is_match_pattern = True
                going_direction = False

        return going_direction, fail_code


    # purpose: check for XD base rule.
    # return:
    #   True: match, path going right.
    #   False: not match, path going left.
    def going_xd_down(self, format_dict_array, idx):
        going_down = False
        is_match_pattern = False
        fail_code = 0

        nodes_length = len(format_dict_array)

        '''
        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0:
                    fail_code = 2201
                    is_match_pattern = True
                    going_down = True

        if not is_match_pattern:
            # - sharp.
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0:
                    fail_code = 2202
                    is_match_pattern = True
                    going_down = True
        '''

        if not is_match_pattern:
            # \ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0:
                # 第一條，雖然向下走，但接近水平線。
                if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                    # - sharp.
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0:
                        fail_code = 2202
                        is_match_pattern = True
                        going_down = True
                else:
                    fail_code = 2203
                    is_match_pattern = True
                    going_down = True

            # for < sharp. "女" 的左半邊。
            if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0:
                fail_code = 2211
                is_match_pattern = True
                going_down = True


        return going_down, fail_code

    # purpose: check for Rainbow base rule.
    # return:
    #   True: match, path going right.
    #   False: not match, path going left.
    # PS: directly use not XD, cause "五" uni4E94 fail.
    def going_rainbow_up(self, format_dict_array, idx):
        going_up = False
        is_match_pattern = False
        fail_code = 0

        nodes_length = len(format_dict_array)

        '''
        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                    fail_code = 2201
                    is_match_pattern = True
                    going_up = True

        if not is_match_pattern:
            # - sharp.
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                    fail_code = 2202
                    is_match_pattern = True
                    going_up = True
        '''

        if not is_match_pattern:
            # \ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                # 第一條，雖然向上走，但接近水平線。
                # ex: uni9787 的革，會誤判。
                if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                    # - sharp.
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                        fail_code = 2202
                        is_match_pattern = True
                        going_up = True
                else:
                    fail_code = 2203
                    is_match_pattern = True
                    going_up = True

            # for > sharp.
            if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                fail_code = 2211
                is_match_pattern = True
                going_up = True


        return going_up, fail_code

    # purpose: check for toothpaste base rule.
    # return:
    #   True: match,
    #   False: not match,
    def going_toothpaste(self, format_dict_array, idx):
        going_direction = False
        is_match_pattern = False
        fail_code = 0

        nodes_length = len(format_dict_array)

        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                # 第一條線很明確，後面就不用做比對了。
                is_match_pattern = True

                if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0:
                    if format_dict_array[(idx+1)%nodes_length]['x_direction'] < 0:
                        fail_code = 2201
                        is_match_pattern = True
                        going_direction = True
                else:
                    if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                        fail_code = 2202
                        is_match_pattern = True
                        going_direction = True

        if not is_match_pattern:
            # - sharp.
            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                # 第一條線很明確，後面就不用做比對了。
                is_match_pattern = True

                if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0:
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0:
                        fail_code = 2211
                        is_match_pattern = True
                        going_direction = True
                else:
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                        fail_code = 2212
                        is_match_pattern = True
                        going_direction = True

        if not is_match_pattern:
            # | sharp.
            if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                # 第2條線很明確，後面就不用做比對了。
                is_match_pattern = True

                if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                        fail_code = 2221
                        is_match_pattern = True
                        going_direction = True
                else:
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0:
                        fail_code = 2222
                        is_match_pattern = True
                        going_direction = True

            # - sharp.
            if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                # 第2條線很明確，後面就不用做比對了。
                is_match_pattern = True

                if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                        fail_code = 2231
                        is_match_pattern = True
                        going_direction = True
                else:
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0:
                        fail_code = 2232
                        is_match_pattern = True
                        going_direction = True

        '''
        if not is_match_pattern:
            # \\ sharp. go up.
            # / sharp. go down.
            if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                # 第一條，雖然向上走，但接近水平線。
                # ex: uni9787 的革，會誤判。
                if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                    # - sharp.
                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                        fail_code = 2202
                        is_match_pattern = True
                        going_direction = True
                else:
                    fail_code = 2203
                    is_match_pattern = True
                    going_direction = True

        '''

        # 以下的 case 會造成轉換效果大放送。放寬套用到的條件。
        if not is_match_pattern:
            # for > sharp. or < sharp
            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == format_dict_array[(idx+1)%nodes_length]['x_direction'] * -1:
                if format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[(idx+0)%nodes_length]['y_direction']:
                    fail_code = 2231
                    is_match_pattern = True
                    going_direction = True

        return going_direction, fail_code
