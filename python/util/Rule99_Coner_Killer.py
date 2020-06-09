#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 99
# kill all small coner.
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule, black_mode):
        redo_travel=False
        check_first_point = False

        MIN_DISTANCE = 12
        
        # default: 1.6 (large 女), 1.72 (small 女), 1.79(下半扁女）
        SLIDE_0_PERCENT_MIN = 1.40
        SLIDE_0_PERCENT_MAX = 1.80

        SLIDE_20_PERCENT_MIN = 1.52
        SLIDE_20_PERCENT_MAX = 1.88

        SLIDE_30_PERCENT_MIN = 1.59
        SLIDE_30_PERCENT_MAX = 1.88
        
        # default: 1.65 - 1.75 (large 女), 1.38 (small 女), 1.07(下半扁女）
        SLIDE_1_PERCENT_MIN = 1.54
        SLIDE_1_PERCENT_MAX = 1.88

        SLIDE_21_PERCENT_MIN = 1.18
        SLIDE_21_PERCENT_MAX = 1.58

        SLIDE_31_PERCENT_MIN = 0.87
        SLIDE_31_PERCENT_MAX = 1.27
        
        # default: 0.93 - 1.2 (large 女), 1.45 (small 女), 1.69(下半扁女）
        SLIDE_2_PERCENT_MIN = 0.73
        SLIDE_2_PERCENT_MAX = 1.38

        SLIDE_22_PERCENT_MIN = 1.25
        SLIDE_22_PERCENT_MAX = 1.65

        SLIDE_32_PERCENT_MIN = 1.49
        SLIDE_32_PERCENT_MAX = 1.88

        # 這裡 MIN 的值，需要設小。
        SLIDE_10_PERCENT_MIN = 0.79
        SLIDE_10_PERCENT_MAX = 1.80


        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 3
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip idx+0:",format_dict_array[(idx+0)%nodes_length]['code'])
                        pass
                    continue
                    
                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                # for case.3122 上面的點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip idx+2:",format_dict_array[(idx+2)%nodes_length]['code'])
                        pass
                    continue

                if format_dict_array[idx]['code'] in skip_coordinate_rule:
                    if is_debug_mode:
                        print("match skip skip_coordinate_rule +0:",format_dict_array[idx]['code'])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[627,552]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": #99 val:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')


                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                if format_dict_array[(idx+0)%nodes_length]['code']=='c':
                    x0 = format_dict_array[(idx+0)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+0)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['code']=='c':
                    x2 = format_dict_array[(idx+0)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+0)%nodes_length]['y1']

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # match ?l?
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    fail_code = 100
                    is_match_pattern = True

                # match ??l
                if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                    fail_code = 110
                    is_match_pattern = True

                if is_match_pattern:
                    fail_code = 111
                    if format_dict_array[(idx+0)%nodes_length]['distance'] <= MIN_DISTANCE:
                        fail_code = 120
                        is_match_pattern = False

                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= MIN_DISTANCE:
                        fail_code = 130
                        is_match_pattern = False


                # for all "女" 裡的空白。
                # match ?cc (almost is lcc, some is ccc).

                if not black_mode:
                    #if format_dict_array[(idx+0)%nodes_length]['t'] == 'l':
                    #fail_code = 200
                    if True:
                        if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                            fail_code = 210
                            if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                                fail_code = 220
                                if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.STROKE_WIDTH_AVERAGE:
                                    fail_code = 230
                                    if format_dict_array[(idx+1)%nodes_length]['distance'] > self.config.STROKE_WIDTH_AVERAGE:
                                        fail_code = 240

                                        slide_percent_0 = spline_util.slide_percent(format_dict_array[(idx-1+nodes_length)%nodes_length]['x'],format_dict_array[(idx-1+nodes_length)%nodes_length]['y'],format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                                        # PS: 使用 end x,y 可能會有「重覆套用」的問題。
                                        #slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                                        slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)
                                        slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                                        if is_debug_mode:
                                        #if False:
                                            print("slide_percent 0:", slide_percent_0)
                                            print("data:",format_dict_array[(idx-1+nodes_length)%nodes_length]['x'],format_dict_array[(idx-1+nodes_length)%nodes_length]['y'],format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                                            print("slide_percent 1:", slide_percent_1)
                                            print("data:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                                            print("slide_percent 2:", slide_percent_2)
                                            print("data:",format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                                        # for large 女
                                        if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                                            fail_code = 250
                                            if slide_percent_2 >= SLIDE_2_PERCENT_MIN and slide_percent_2 <= SLIDE_2_PERCENT_MAX:
                                                fail_code = 260
                                                if slide_percent_0 >= SLIDE_0_PERCENT_MIN and slide_percent_0 <= SLIDE_0_PERCENT_MAX:
                                                    is_match_pattern = True

                                        # for small 女
                                        if slide_percent_1 >= SLIDE_21_PERCENT_MIN and slide_percent_1 <= SLIDE_21_PERCENT_MAX:
                                            fail_code = 270
                                            if slide_percent_2 >= SLIDE_22_PERCENT_MIN and slide_percent_2 <= SLIDE_22_PERCENT_MAX:
                                                fail_code = 280
                                                if slide_percent_0 >= SLIDE_20_PERCENT_MIN and slide_percent_0 <= SLIDE_20_PERCENT_MAX:
                                                    is_match_pattern = True

                                        # for 下半扁 女
                                        if slide_percent_1 >= SLIDE_31_PERCENT_MIN and slide_percent_1 <= SLIDE_31_PERCENT_MAX:
                                            fail_code = 290
                                            if slide_percent_2 >= SLIDE_32_PERCENT_MIN and slide_percent_2 <= SLIDE_32_PERCENT_MAX:
                                                fail_code = 291
                                                if slide_percent_0 >= SLIDE_30_PERCENT_MIN and slide_percent_0 <= SLIDE_30_PERCENT_MAX:
                                                    is_match_pattern = True


                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                # PS: to test inside_stroke_flag, please use real position instead of x1,y1.

                # compare distance, muse large than our "large round"

                inside_stroke_flag = False
                inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)

                round_offset = self.config.ROUND_OFFSET
                if not inside_stroke_flag:
                    round_offset = self.config.INSIDE_ROUND_OFFSET

                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False

                    if black_mode:
                        # 為避免與 rule#5 衝突，
                        # 使用較短邊
                        if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET:
                            fail_code = 310
                            is_match_pattern = True
                            if format_dict_array[(idx+1)%nodes_length]['distance'] < round_offset:
                                round_offset = format_dict_array[(idx+1)%nodes_length]['distance']
                        
                        if format_dict_array[(idx+0)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET:
                            fail_code = 320
                            is_match_pattern = True
                            if format_dict_array[(idx+0)%nodes_length]['distance'] < round_offset:
                                round_offset = format_dict_array[(idx+0)%nodes_length]['distance']
                    else:
                        # white mode.
                        # 使用較短邊
                        is_match_pattern = True
                        
                        #round_offset = self.config.ROUND_OFFSET
                        # white mode 使用較小的 size.
                        if format_dict_array[(idx+1)%nodes_length]['distance'] < round_offset:
                            round_offset = format_dict_array[(idx+1)%nodes_length]['distance']
                        if format_dict_array[(idx+0)%nodes_length]['distance'] < round_offset:
                            round_offset = format_dict_array[(idx+0)%nodes_length]['distance']


                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x_from = x0
                    y_from = y0
                    x_center = format_dict_array[(idx+1)%nodes_length]['x2']
                    y_center = format_dict_array[(idx+1)%nodes_length]['y2']
                    x0 = self.compute_curve_new_x1(spline_util.get_distance(x_from,y_from,x1,y1),spline_util.get_distance(x_center,y_center,x1,y1),x_from,x_center,x1)
                    y0 = self.compute_curve_new_x1(spline_util.get_distance(x_from,y_from,x1,y1),spline_util.get_distance(x_center,y_center,x1,y1),y_from,y_center,y1)
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x_from = x2
                    y_from = y2
                    x_center = format_dict_array[(idx+2)%nodes_length]['x1']
                    y_center = format_dict_array[(idx+2)%nodes_length]['y1']
                    x2 = self.compute_curve_new_x1(spline_util.get_distance(x_from,y_from,x1,y1),spline_util.get_distance(x_center,y_center,x1,y1),x_from,x_center,x1)
                    y2 = self.compute_curve_new_x1(spline_util.get_distance(x_from,y_from,x1,y1),spline_util.get_distance(x_center,y_center,x1,y1),y_from,y_center,y1)
                #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False

                    # PS: 使用結束 x,y，會造成更誤判，因為沒有另外儲存 rule#99 處理記錄，會造成重覆套用。
                    #slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_10 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)

                    if is_debug_mode:
                            print("slide_percent 10:", slide_percent_10)
                            print("data end:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                            print("data virtual:",x0,y0,x1,y1,x2,y2)
                            print("SLIDE_10_PERCENT_MIN:", SLIDE_10_PERCENT_MIN)
                            print("SLIDE_10_PERCENT_MAX:", SLIDE_10_PERCENT_MAX)
        
                    if slide_percent_10 >= SLIDE_10_PERCENT_MIN and slide_percent_10 <= SLIDE_10_PERCENT_MAX:
                        is_match_pattern = True

                # 為了在 white mode 使用。
                if is_match_pattern:
                    need_check_join_line = False

                    fail_code = 500
                    if not inside_stroke_flag:
                        need_check_join_line = True

                    if need_check_join_line:
                        fail_code = 600
                        is_match_pattern = False

                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2)
                        join_flag_1 = join_flag
                        join_flag_2 = None
                        if not join_flag:
                            fail_code = 610
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            join_flag_2 = join_flag
                            pass

                        if is_debug_mode:
                            print("check1_flag:",join_flag_1)
                            print("check2_flag:",join_flag_2)
                            print("final join flag:", join_flag)

                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass



                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #99:", fail_code)
                    else:
                        print("match rule #99:",idx)

                if is_match_pattern:
                    # make coner curve
                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx)

                    # cache transformed nodes.
                    # we generated nodes
                    # 因為只有作用在2個coordinate. 
                    if self.config.PROCESS_MODE in ["HALFMOON"]:
                        # 加了這行，會讓「口」的最後一個角，無法套到。
                        skip_coordinate.append([previous_x,previous_y])
                        pass

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+1)%nodes_length]['code']
                    #print("generated_code:", generated_code)
                    skip_coordinate_rule.append(generated_code)

                    check_first_point = True
                    redo_travel=True

                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx
                    break
                    #redo_travel=True
                    #resume_idx = -1
                    #break

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule
