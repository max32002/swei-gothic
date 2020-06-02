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

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate, black_mode):
        redo_travel=False

        MIN_DISTANCE = 12
        
        # 最大的角度值，超過就skip
        ALMOST_LINE_RATE = 1.84

        # default: 1.6 (large 女), 1.72 (small 女)
        SLIDE_0_PERCENT_MIN = 1.49
        SLIDE_0_PERCENT_MAX = 1.71

        SLIDE_20_PERCENT_MIN = 1.61
        SLIDE_20_PERCENT_MAX = 1.83
        
        # default: 1.75 (large 女), 1.38 (small 女)
        SLIDE_1_PERCENT_MIN = 1.64
        SLIDE_1_PERCENT_MAX = ALMOST_LINE_RATE

        SLIDE_21_PERCENT_MIN = 1.27
        SLIDE_21_PERCENT_MAX = 1.49
        
        # default: 0.93 (large 女), 1.45 (small 女)
        SLIDE_2_PERCENT_MIN = 0.92
        SLIDE_2_PERCENT_MAX = 1.04

        SLIDE_22_PERCENT_MIN = 1.34
        SLIDE_22_PERCENT_MAX = 1.56

        SLIDE_10_PERCENT_MIN = 0.80
        SLIDE_10_PERCENT_MAX = ALMOST_LINE_RATE


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

                #print(idx,"debug rule99+0:",format_dict_array[idx]['code'])

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue
                    
                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                # for case.3122 上面的點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[742,291]]
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

                # compare distance, muse large than our "large round"
                round_offset = self.config.ROUND_OFFSET

                inside_stroke_flag = False
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False

                    if black_mode:

                        inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                        if not inside_stroke_flag:
                            round_offset = self.config.INSIDE_ROUND_OFFSET

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
                        round_offset = self.config.INSIDE_ROUND_OFFSET
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

                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']

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
                    if black_mode:
                        fail_code = 500
                        if not inside_stroke_flag:
                            need_check_join_line = True
                    else:
                        # white mode.
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
                    #print("match rule #99")
                    #print(idx,"debug rule99+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule99+1:",format_dict_array[(idx+1)%nodes_length]['code'])
                    #print(idx,"debug rule99+2:",format_dict_array[(idx+2)%nodes_length]['code'])

                    # make coner curve
                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx)

                    # cache transformed nodes.
                    # we generated nodes
                    # 因為只有作用在2個coordinate. 
                    skip_coordinate.append([previous_x,previous_y])


                    redo_travel=True

                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx
                    break
                    #redo_travel=True
                    #resume_idx = -1
                    #break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
