#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 7
# 「多」uni591A, 字右上角的小帽子
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, apply_rule_log, generate_rule_log):
        redo_travel=False

        CAP_HEIGHT_DISTANCE = 30

        # for mode: sencond.
        # default: 1.90
        SLIDE_1_PERCENT_MIN = 1.80
        SLIDE_1_PERCENT_MAX = 1.96

        # default: 1.15
        SLIDE_2_PERCENT_MIN = 0.95
        SLIDE_2_PERCENT_MAX = 1.35

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 5
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if format_dict_array[(idx+0)%nodes_length]['code'] in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +0:",[format_dict_array[(idx+0)%nodes_length]['code']])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[46,606]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": val#7:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False

                # case: 多
                # 515 792 515 792 473 750 c 1,29,-1
                # 732 750 l 1,30,-1
                # 745 753 l 1,7,-1
                # 793 723 l 1,8,9
                # 747 643 747 643 671.5 574 c 128,-1,10

                # case: 㐉
                #0: 105 358 l 1,19,-1
                #1: 699 358 l 1,20,-1
                #2: 714 361 l 1,21,-1
                #3: 768 320 l 1,22,23
                #4: 763 314 763 314 749 308 c 0,24,25

                # match: ?lllc
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+3)%nodes_length]['t'] == 'l':
                            #if format_dict_array[(idx+4)%nodes_length]['t'] == 'c':
                            fail_code = 100
                            is_match_pattern = True
                        else:
                            fail_code = 110
                            # for case: 㐕(3415), 的乙
                            #if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                            if format_dict_array[(idx+2)%nodes_length]['distance'] <= 30:
                                if format_dict_array[(idx+2)%nodes_length]['x_direction'] < 0:
                                    if format_dict_array[(idx+2)%nodes_length]['y_direction'] < 0:
                                        if format_dict_array[(idx+3)%nodes_length]['x_direction'] < 0:
                                            if format_dict_array[(idx+3)%nodes_length]['y_direction'] < 0:
                                                is_match_pattern = True
                                    

                # 是否為「乙」的模式。
                # PS: 小帽子，被 Rule#Almost line 合併。
                is_also_mode = False

                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        is_match_pattern = True
                    else:
                        # for case 衪 886A 的 「也」/ 釶 91F6 /
                        if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0:
                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                                if format_dict_array[(idx+0)%nodes_length]['distance'] > 70:
                                    if format_dict_array[(idx-1+nodes_length)%nodes_length]['x_equal_fuzzy']:
                                        if format_dict_array[(idx-1+nodes_length)%nodes_length]['y_direction'] < 0:
                                            if format_dict_array[(idx-1+nodes_length)%nodes_length]['distance'] > 90:
                                                if format_dict_array[(idx+3)%nodes_length]['distance'] <= 40:
                                                    is_match_pattern = True
                                                    is_also_mode = True

                # compare stroke_width
                if is_match_pattern:
                    fail_code = 210
                    if format_dict_array[(idx+2)%nodes_length]['match_stroke_width']:
                        is_match_pattern = True
                    else:
                        if format_dict_array[(idx+1)%nodes_length]['distance']<50:
                            # 這樣也可以，如果(短+1)+(筆寬+2) match stroke_width
                            distance_1_to_3 = spline_util.get_distance(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                            #print("distance_1_to_3:", distance_1_to_3)
                            if distance_1_to_3 >= self.config.STROKE_WIDTH_MIN and distance_1_to_3 <= self.config.STROKE_WIDTH_MAX:
                                is_match_pattern = True


                # 是否為「乙」的模式。
                # PS: 小帽子，被 Rule#Almost line 合併。
                is_senond_mode = False

                # compare CAP_HEIGHT_DISTANCE
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= CAP_HEIGHT_DISTANCE:
                        is_match_pattern = True
                    else:
                        fail_code = 310
                        if format_dict_array[(idx+2)%nodes_length]['distance'] <= 40:
                            fail_code = 320
                            slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                            slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                            #if is_debug_mode:
                            if False:
                                print("slide_percent 1:", slide_percent_1)
                                print("data end:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                                print("slide_percent 2:", slide_percent_2)
                                print("data end:",format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                            if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                                fail_code = 330
                                if slide_percent_2 >= SLIDE_2_PERCENT_MIN and slide_percent_2 <= SLIDE_2_PERCENT_MAX:
                                    is_senond_mode = True
                                    is_match_pattern = True

                # compare direction
                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False

                    if not is_senond_mode:
                        fail_code = 410
                        # for 多。
                        if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0 :
                            if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0 :
                                if format_dict_array[(idx+2)%nodes_length]['x_direction'] > 0 :
                                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0 :
                                        if format_dict_array[(idx+2)%nodes_length]['y_direction'] < 0 :
                                            if format_dict_array[(idx+3)%nodes_length]['y_direction'] < 0 :
                                                if format_dict_array[(idx+3)%nodes_length]['x_direction'] < 0 :
                                                    is_match_pattern = True
                    else:
                        fail_code = 420
                        # for 乙
                        if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0 :
                            if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0 :
                                if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0 :
                                    if format_dict_array[(idx+2)%nodes_length]['x_direction'] < 0 :
                                        if format_dict_array[(idx+2)%nodes_length]['y_direction'] < 0 :
                                            if format_dict_array[(idx+3)%nodes_length]['x_direction'] < 0 :
                                                if format_dict_array[(idx+3)%nodes_length]['y_direction'] < 0 :
                                                    is_match_pattern = True

                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,": debug fail_code #7:", fail_code)
                    else:
                        print(idx,": match rule #7")

                if is_match_pattern:

                    if is_debug_mode:
                        print("is_senond_mode:", is_senond_mode)
                        print("is_also_mode:",is_also_mode)

                    if not is_senond_mode:
                        # 多，模式。
                        center_x = int((format_dict_array[(idx+2)%nodes_length]['x']+format_dict_array[(idx+3)%nodes_length]['x'])/2)
                        #center_y = int((format_dict_array[(idx+2)%nodes_length]['y']+format_dict_array[(idx+3)%nodes_length]['y'])/2)
                        center_y = format_dict_array[(idx+2)%nodes_length]['y']+3
                        #print("center x,y:", center_x, center_y)

                        x0 = format_dict_array[(idx+1)%nodes_length]['x']
                        y0 = format_dict_array[(idx+1)%nodes_length]['y']
                        x1 = format_dict_array[(idx+2)%nodes_length]['x']
                        y1 = format_dict_array[(idx+2)%nodes_length]['y']

                        x0_offset = format_dict_array[(idx+1)%nodes_length]['x'] - x0
                        y0_offset = format_dict_array[(idx+1)%nodes_length]['y'] - y0

                        x2 = format_dict_array[(idx+3)%nodes_length]['x']
                        y2 = format_dict_array[(idx+3)%nodes_length]['y']
                        x2_offset = 0
                        y2_offset = 0

                        # 斜線上的「內縮」的新坐標。
                        new_x1=x0+x0_offset
                        new_y1=y0+y0_offset
                        new_x2=x2+x2_offset
                        new_y2=y2+y2_offset
                        #print("new x1,y1:", new_x1, new_y1)
                        #print("new x2,y2:", new_x2, new_y2)

                        center_x_p0 = int((center_x + new_x1)/2) - 3
                        center_x_p2 = int((center_x + new_x2)/2) + 3
                        center_y_p0 = int((center_y + new_y1)/2) - 3
                        center_y_p2 = int((center_y + new_y2)/2) + 3

                        # update #2
                        new_code = ' %d %d l 1\n' % (center_x, center_y)
                        dot_dict={}
                        dot_dict['x']=center_x
                        dot_dict['y']=center_y
                        dot_dict['t']='l'
                        dot_dict['code']=new_code
                        format_dict_array[(idx+2)%nodes_length]=dot_dict

                        # 懶的重新計算長度。
                        # assign 前先讀出來.
                        dot3_distance = format_dict_array[(idx+3)%nodes_length]['distance']

                        # update new #3
                        end_x = format_dict_array[(idx+3)%nodes_length]['x']
                        end_y = format_dict_array[(idx+3)%nodes_length]['y']
                        new_code = ' %d %d %d %d %d %d c 1\n' % (center_x_p2, center_y_p2, center_x_p2, center_y_p2, new_x2, new_y2)
                        dot_dict={}
                        dot_dict['x']=new_x2
                        dot_dict['y']=new_y2
                        dot_dict['t']='c'
                        dot_dict['code']=new_code
                        #format_dict_array[(idx+3)%nodes_length]=dot_dict
                        #真神奇，註解掉，還是有作用。

                        if is_also_mode:
                            # 也模式。
                            #print("is_also_mode")
                            target_index = (idx+4)%nodes_length
                            if format_dict_array[target_index]['t'] == 'l':
                                new_x,new_y=spline_util.two_point_extend(format_dict_array[(idx+5)%nodes_length]['x'],format_dict_array[(idx+5)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],-1 * dot3_distance)
                                old_code_string = format_dict_array[target_index]['code']
                                old_code_array = old_code_string.split(' ')

                                old_code_array[1] = str(new_x)
                                old_code_array[2] = str(new_y)
                                new_code = ' '.join(old_code_array)
                                format_dict_array[target_index]['code'] = new_code
                                #print("old code+4:", old_code_string)
                                #print("new code+4:", new_code)
                    else:
                        # 乙，模式。
                        #center_x = int((format_dict_array[(idx+1)%nodes_length]['x']+format_dict_array[(idx+2)%nodes_length]['x'])/2)
                        #center_y = int((format_dict_array[(idx+1)%nodes_length]['y']+format_dict_array[(idx+2)%nodes_length]['y'])/2)
                        
                        del format_dict_array[(idx+2)%nodes_length]
                        self.apply_round_transform(format_dict_array,idx, apply_rule_log, generate_rule_log)
                        
                    redo_travel=True
                    #resume_idx = -1
                    resume_idx = idx
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, apply_rule_log, generate_rule_log
