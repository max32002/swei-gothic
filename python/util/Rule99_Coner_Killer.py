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

    def apply(self, stroke_dict, key, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log, black_mode):
        redo_travel=False
        check_first_point = False

        RULE_MIN_DISTANCE_REQUIREMENT = 10
        
        # 這裡 MIN 的值，需要設小。
        SLIDE_10_PERCENT_MIN = 0.59
        SLIDE_10_PERCENT_MAX = 1.80

        if self.config.PROCESS_MODE in ["B2","B4","NUT8","ALIAS"]:
            SLIDE_10_PERCENT_MIN = 0.10

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
                # skip traveled nodes.
                if idx <= resume_idx:
                    continue
                # length changed, may overfloat, break.
                nodes_length = len(format_dict_array)
                if idx >= nodes_length:
                    break
                # length changed, may integer division or modulo by zero
                if nodes_length < rule_need_lines:
                    break

                is_debug_mode = False
                #is_debug_mode = True

                detect_code = format_dict_array[(idx+0)%nodes_length]['code']
                if is_debug_mode:
                    print("current deubg code:", detect_code)
                    pass
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
                        print("current code:",format_dict_array[(idx+0)%nodes_length]['code'])
                        pass
                    continue

                # for uni6529 攩，的黑的點, 問題是 clockwise + counter clockwise ，解法之一是直接停掉Rule#99.
                # 
                check_idx_1_code = True
                # 有一個例外，不要檢查這一個Rule, 就是 nut8, 
                # 因為 nut8 裡的 Rule#1 並不會產生內縮後的點，所以會和 Rule#99 的點共用.
                # ex: uni5E3D 帽的最右上角。
                # PS: 這一個 check_idx_1_code 目前可能非必需，
                #      因為 ver 2.120 code在 Rule.py 裡修改，造成交互影響。
                check_idx_1_code = False
                if False:
                    # PS: 檢查 idx+1 會造成「口」字的最後一個節點，無法被套用。
                    if self.config.PROCESS_MODE in ["NUT8","TOOTHPASTE","ALIAS","SPIKE"]:
                        check_idx_1_code = False
                        pass
                    if check_idx_1_code:
                        if format_dict_array[(idx+1)%nodes_length]['code'] in apply_rule_log:
                            if is_debug_mode:
                                print("match skip apply_rule_log +1:",format_dict_array[(idx+1)%nodes_length]['code'])
                                pass
                            continue


                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[323,542]]
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
                # PS: 下面這2個if, 在很多之前的版本，都沒有被執行，效果也很好，也許可以直接註解掉。
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                is_match_pattern = True

                # 對太短邊做處理會出問題。
                if is_match_pattern:
                    if format_dict_array[(idx+0)%nodes_length]['distance'] <= 2:
                        is_match_pattern = False
                if is_match_pattern:
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= 2:
                        is_match_pattern = False

                #PS:需要檢查, 對太短的邊做處理，目前的code會有「很多」問題。
                if is_match_pattern:
                    fail_code = 111

                    is_nodes_enough_to_merge = True
                    if nodes_length <= 3:
                        is_nodes_enough_to_merge = False

                    # PS: merge node 在 halfmoon + toothpaste mode 下可能會出錯，因為有點重疊的問題。
                    if format_dict_array[(idx+0)%nodes_length]['distance'] <= RULE_MIN_DISTANCE_REQUIREMENT and format_dict_array[(idx+0)%nodes_length]['distance'] > 1:
                        if not is_nodes_enough_to_merge:
                            fail_code = 120
                            is_match_pattern = False
                        else:
                            # able to merge
                            # start extend (merge once)
                            old_code_string = format_dict_array[(idx+0)%nodes_length]['code']
                            old_code_array = old_code_string.split(' ')
                            if format_dict_array[(idx+0)%nodes_length]['t']=='c':
                                old_code_array[5] = str(format_dict_array[(idx+1)%nodes_length]['x'])
                                old_code_array[6] = str(format_dict_array[(idx+1)%nodes_length]['y'])
                            else:
                                # l
                                old_code_array[1] = str(format_dict_array[(idx+1)%nodes_length]['x'])
                                old_code_array[2] = str(format_dict_array[(idx+1)%nodes_length]['y'])
                            new_code = ' '.join(old_code_array)
                            # only need update code, let formater to re-compute.
                            format_dict_array[(idx+0)%nodes_length]['code'] = new_code

                            del format_dict_array[(idx+1)%nodes_length]
                            if idx > (idx+1)%nodes_length:
                                idx -=1
                            nodes_length = len(format_dict_array)

                            check_first_point = True
                            redo_travel=True
                            resume_idx = -1
                            break

                    is_nodes_enough_to_merge = True
                    if nodes_length <= 3:
                        is_nodes_enough_to_merge = False

                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= RULE_MIN_DISTANCE_REQUIREMENT and format_dict_array[(idx+1)%nodes_length]['distance'] > 1:
                        if not is_nodes_enough_to_merge:
                            fail_code = 130
                            is_match_pattern = False
                        else:
                            # able to merge
                        
                            # start extend (merge once)
                            old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                            old_code_array = old_code_string.split(' ')
                            if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                                old_code_array[5] = str(format_dict_array[(idx+2)%nodes_length]['x'])
                                old_code_array[6] = str(format_dict_array[(idx+2)%nodes_length]['y'])
                            else:
                                # l
                                old_code_array[1] = str(format_dict_array[(idx+2)%nodes_length]['x'])
                                old_code_array[2] = str(format_dict_array[(idx+2)%nodes_length]['y'])
                            new_code = ' '.join(old_code_array)
                            # only need update code, let formater to re-compute.
                            format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                            del format_dict_array[(idx+2)%nodes_length]

                            if idx > (idx+2)%nodes_length:
                                idx -=1
                            nodes_length = len(format_dict_array)

                            check_first_point = True

                            # check result again.
                            #print("idx:",idx)
                            #print("nodes_length:",nodes_length)
                            self.apply_code(format_dict_array,(idx+1)%nodes_length)
                            if format_dict_array[(idx+1)%nodes_length]['distance'] <= RULE_MIN_DISTANCE_REQUIREMENT and format_dict_array[(idx+1)%nodes_length]['distance'] > 1:
                                fail_code = 131
                                is_match_pattern = False


                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                # PS: to test inside_stroke_flag, please use real position instead of x1,y1.

                # for D.Lucy
                # only apply right part.
                if self.config.PROCESS_MODE in ["D","DEL"]:
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_d_right(format_dict_array,idx)
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

                inside_stroke_flag = False
                if is_match_pattern:
                    # B2,B4 skip check image.
                    if self.config.NEED_LOAD_BMP_IMAGE:
                        inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)

                # for NUT8
                # 遇到黑色部分，只有長線條才套用效果。
                if is_match_pattern:
                    if self.config.PROCESS_MODE in ["NUT8"]:
                        if inside_stroke_flag:
                            # for uni87BA 螺的虫的丶，必需>=1.4, 不然會套到效果. 
                            remain_rate = 1.4   # for black mode.
                            if not black_mode:
                                # for uni9ED1 黑裡的點，希望可以保留，不套用效果。
                                remain_rate = 1.7   # for black mode.
                            if format_dict_array[(idx+0)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET * remain_rate:
                                fail_code = 1341
                                is_match_pattern = False
                            if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET * remain_rate:
                                fail_code = 1342
                                is_match_pattern = False
                        else:
                            is_match_pattern = False

                if is_match_pattern:
                    # PS: SPIKE 和 NUT8 的差別，在 black mode 時，允許直接套用效果。
                    if self.config.PROCESS_MODE in ["SPIKE"]:
                        if inside_stroke_flag:
                            pass
                        else:
                            is_match_pattern = False

                if is_match_pattern:
                    # PS: ALIAS 和 NUT8 的差別，在 black mode 時，允許直接套用效果。
                    if self.config.PROCESS_MODE in ["ALIAS"]:
                        if inside_stroke_flag:
                            # for uni9797 鞗的革的廿 
                            remain_rate = 1.1   # for black mode.
                            if not black_mode:
                                # for uni9ED1 黑裡的點，希望可以保留，不套用效果。
                                remain_rate = 1.7   # for black mode.
                            if format_dict_array[(idx+0)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET * remain_rate:
                                fail_code = 1341
                                is_match_pattern = False
                            if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET * remain_rate:
                                fail_code = 1342
                                is_match_pattern = False
                        else:
                            is_match_pattern = False

                # for 攩裡的黑裡的點。
                if is_match_pattern:
                    pass

                round_offset = self.config.ROUND_OFFSET
                if not inside_stroke_flag:
                    round_offset = self.config.INSIDE_ROUND_OFFSET

                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False

                    if black_mode:
                        # 為避免與 rule#5 衝突，
                        # 使用較短邊
                        
                        #似乎不需要檢查。
                        if True:
                        #if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET:
                            #fail_code = 310
                            is_match_pattern = True
                            if format_dict_array[(idx+1)%nodes_length]['distance'] < round_offset:
                                round_offset = format_dict_array[(idx+1)%nodes_length]['distance']
                        
                        #似乎不需要檢查。
                        if True:
                        #if format_dict_array[(idx+0)%nodes_length]['distance'] <= self.config.OUTSIDE_ROUND_OFFSET:
                            #fail_code = 320
                            #is_match_pattern = True
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
                    x0 = x_center
                    y0 = y_center
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x_from = x2
                    y_from = y2
                    x_center = format_dict_array[(idx+2)%nodes_length]['x1']
                    y_center = format_dict_array[(idx+2)%nodes_length]['y1']
                    x2 = x_center
                    y2 = y_center
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
                        
                        slide_percent_10 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)
                        if slide_percent_10 >= SLIDE_10_PERCENT_MIN and slide_percent_10 <= SLIDE_10_PERCENT_MAX:
                            is_match_pattern = True


                # 為了在 white mode 使用。
                if is_match_pattern:
                    need_check_join_line = False

                    fail_code = 500
                    if not inside_stroke_flag:
                        need_check_join_line = True

                    # B2, B4 skip check image.
                    if not self.config.NEED_LOAD_BMP_IMAGE:
                        need_check_join_line = False

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
                #if True:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #99:", fail_code)
                    else:
                        print("match rule #99:",idx)

                if is_match_pattern:
                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("apply_rule_log:", generated_code)
                    apply_rule_log.append(generated_code)

                    # make coner curve
                    coner_mode = "CURVE"

                    if self.config.PROCESS_MODE in ["NUT8"]:
                        coner_mode = "STRAIGHT"
                    if self.config.PROCESS_MODE in ["ALIAS"]:
                        coner_mode = "ALIAS"
                    if self.config.PROCESS_MODE in ["SPIKE"]:
                        coner_mode = "SPIKE"

                    is_goto_apply_round = True
                    center_x,center_y = -9999,-9999
                    next_x, next_y = -9999,-9999

                    if self.config.PROCESS_MODE in ["TOOTHPASTE"]:
                        is_match_direction_base_rule, fail_code = self.going_toothpaste(format_dict_array,idx)
                        is_goto_apply_round = is_match_direction_base_rule

                    if is_goto_apply_round:
                        format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx,apply_rule_log,generate_rule_log,stroke_dict,key,coner_mode=coner_mode)

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
