#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 11
# check inside curve
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, stroke_dict, key, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log):
        redo_travel=False
        check_first_point = False

        # 最大的角度值，超過就skip
        ALMOST_LINE_RATE = 1.84

        # default: 1.75
        SLIDE_1_PERCENT_MIN = 0.8
        SLIDE_1_PERCENT_MAX = ALMOST_LINE_RATE

        MIN_DISTANCE = 12

        spline_dict = stroke_dict[key]

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

                # 這個效果滿好玩的，「口」會變成二直，二圓。
                if self.config.PROCESS_MODE in ["HALFMOON"]:
                    idx_previuos = (idx -1 + nodes_length) % nodes_length
                    if format_dict_array[idx_previuos]['code'] in apply_rule_log:
                        continue

                detect_code = format_dict_array[(idx+0)%nodes_length]['code']
                if detect_code in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +0:",detect_code)
                        pass
                    continue

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                detect_code = format_dict_array[(idx+2)%nodes_length]['code']
                if detect_code in generate_rule_log:
                    if is_debug_mode:
                        print("match skip generate_rule_log +2:",detect_code)
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[770,407],[850,315],[831,407]]
                    #print("="*30)
                    #print("current x,y:", [format_dict_array[idx]['x'],format_dict_array[idx]['y']])
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue
                        pass
                    else:
                        print("="*30)
                        print("index:", idx)
                        for debug_idx in range(8):
                            print(debug_idx-2,": #11 val:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                # PS: 下面這2個if, 在很多之前的版本，都沒有被執行，效果也很好，也許可以直接註解掉。
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']

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

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= MIN_DISTANCE:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= MIN_DISTANCE:
                            is_match_pattern = True

                # for D.Lucy
                if self.config.PROCESS_MODE in ["D","DEL"]:
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_d_right(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule

                # for RightBottom
                if self.config.PROCESS_MODE in ["RIGHTBOTTOM"]:
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_rightbottom_direction(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule

                # for XD
                if self.config.PROCESS_MODE in ["XD"]:
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_xd_down(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule


                # for RAINBOW
                if self.config.PROCESS_MODE in ["RAINBOW","BOW"]:
                    fail_code = 133
                    #print("before is_match_pattern:", is_match_pattern)
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_rainbow_up(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule
                    #print("after is_match_pattern:", is_match_pattern)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False

                    # PS: 使用結束 x,y，會造成更誤判，因為沒有另外儲存 rule#99 處理記錄，會造成重覆套用。
                    #slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)

                    if is_debug_mode:
                            print("slide_percent 1:", slide_percent_1)
                            print("data end:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                            print("data virtual:",x0,y0,x1,y1,x2,y2)
                            print("SLIDE_1_PERCENT_MIN:", SLIDE_1_PERCENT_MIN)
                            print("SLIDE_1_PERCENT_MAX:", SLIDE_1_PERCENT_MAX)
        
                    if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                        is_match_pattern = True
                    #else:
                    # 暫時沒有找到當初要解決的字是那一個。
                    # 但這段 code 會讓線條產生內凹，參考看看 𫣆 u2B8C6 的 思 裡的心。
                    if False:
                        # try real point.
                        # for case 「_」(忘記是那一個字）字的力的右上角。
                        # PS: 「加」(忘記是那一個字）字算是例外，一般的字，不應檢查到這裡。
                        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+1)%nodes_length]['x2']==format_dict_array[(idx+1)%nodes_length]['x1'] and format_dict_array[(idx+1)%nodes_length]['y2']==format_dict_array[(idx+1)%nodes_length]['y1']:
                                pass
                            else:
                                # x1 != x2
                                # 這個「不相等」的情況，滿特別，允許例外。
                                # PS: 後來發現，沒有很特別，還滿常見的，如果使用下面註解裡的值，幾乎都會套用到效果。
                                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                        x1 = format_dict_array[(idx+1)%nodes_length]['x']
                        y1 = format_dict_array[(idx+1)%nodes_length]['y']
                        
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+2)%nodes_length]['x2']==format_dict_array[(idx+2)%nodes_length]['x1'] and format_dict_array[(idx+2)%nodes_length]['y2']==format_dict_array[(idx+2)%nodes_length]['y1']:
                                pass
                            else:
                                # x1 != x2
                                # 這個「不相等」的情況，滿特別，允許例外。
                                # PS: 後來發現，沒有很特別，還滿常見的，如果使用下面註解裡的值，幾乎都會套用到效果。
                                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                        
                        slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)
                        if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                            is_match_pattern = True

                # check black stroke in white area. @_@;
                is_apply_large_corner = False
                if is_match_pattern:
                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_MIN, inside_stroke_dict)
                    if inside_stroke_flag:
                        is_apply_large_corner = True
                        #print("match is_apply_large_corner:",x1,y1)
                #print("is_apply_large_corner:", is_apply_large_corner)
                #print("test_inside_coner:", x0, y0, x1, y1, x2, y2)

                if not is_apply_large_corner:
                    if is_match_pattern:
                        fail_code = 400
                        is_match_pattern = False
                        
                        join_line_debug_mode = False      # online
                        #join_line_debug_mode = True       # debug
                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2,debug_mode=join_line_debug_mode)
                        join_flag_1 = join_flag
                        join_flag_2 = None
                        if not join_flag:
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            join_flag_2 = join_flag

                        if is_debug_mode:
                            print("check1_flag:",join_flag_1, "data:", x0,y0,x1,y1,x2,y2)
                            print("check2_flag:",join_flag_2, "data:", x2,y2,x1,y1,x0,y0)
                            print("final join flag:", join_flag)
                        
                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass
                else:
                    # for uni77D8 的 黑 裡的點。
                    pass



                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #11:", fail_code)
                    else:
                        print("match rule #11:",idx)

                if is_match_pattern:
                    #print("match rule #11")
                    #print(idx,"debug rule11+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule11+1:",format_dict_array[(idx+1)%nodes_length]['code'])
                    #print(idx,"debug rule11+2:",format_dict_array[(idx+2)%nodes_length]['code'])

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("generated_code:", generated_code)
                    apply_rule_log.append(generated_code)

                    # make coner curve
                    round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    # large curve, use small angle.
                    # start to resize round offset size.
                    resize_round_angle = 1.30
                    if slide_percent_1 >= resize_round_angle:
                        slide_percent_diff = 2.0 - slide_percent_1
                        slide_percent_total = 2.0 - slide_percent_diff
                        slide_percent_diff_percent = slide_percent_diff/slide_percent_total
                        round_offset_diff = self.config.OUTSIDE_ROUND_OFFSET - self.config.ROUND_OFFSET
                        round_offset_diff_added = int(round_offset_diff * slide_percent_diff_percent)
                        round_offset = self.config.ROUND_OFFSET + round_offset_diff_added

                    if not is_apply_large_corner:
                        round_offset = self.config.INSIDE_ROUND_OFFSET

                    is_goto_apply_round = True
                    center_x,center_y = -9999,-9999
                    next_x, next_y = -9999,-9999

                    if self.config.PROCESS_MODE in ["TOOTHPASTE"]:
                        is_match_direction_base_rule, fail_code = self.going_toothpaste(format_dict_array,idx)
                        is_goto_apply_round = is_match_direction_base_rule

                    if is_goto_apply_round:
                        format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx,apply_rule_log, generate_rule_log, stroke_dict, key)

                    # skip_coordinate 決定都拿掉，改用 apply_rule_log
                    # 因為只有作用在2個coordinate. 
                    if self.config.PROCESS_MODE in ["HALFMOON"]:
                        # 加了這行，會讓「口」的最後一個角，無法套到。
                        #skip_coordinate.append([previous_x,previous_y])
                        pass

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


        return redo_travel, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log
