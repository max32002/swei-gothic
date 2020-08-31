#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 13
# smooth all small coner - Flip.
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log):
        redo_travel=False

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        #print("travel rule#13.")

        rule_need_lines = 4
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                # [IMPORTANT]:
                # dead lock will appear, if redo this rule on same point.
                # new point added at +3.
                if format_dict_array[(idx+3)%nodes_length]['code'] in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +3:",[format_dict_array[(idx+3)%nodes_length]['code']])
                        pass
                    continue

                # 隨手亂加的，沒有去思考。
                if format_dict_array[(idx+2)%nodes_length]['code'] in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +2:",[format_dict_array[(idx+2)%nodes_length]['code']])
                        pass
                    continue

                if is_debug_mode:
                    debug_coordinate_list = [[555,674]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')


                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                x3 = format_dict_array[(idx+3)%nodes_length]['x']
                y3 = format_dict_array[(idx+3)%nodes_length]['y']

                # debug purpose:
                #if not(x1==763 and y1==674):
                    #continue

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                #if True:
                if False:
                    print("-" * 20)
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule13:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                # for case .31439 綈的「弟」第2點。
                #0 : values for rule13:  555 674 l 1 -( 208 )
                #1 : values for rule13:  763 674 l 1 -( 45 )
                #2 : values for rule13:  720 689 l 1 -( 132 )
                #3 : values for rule13:  783 806 l 1 -( 54 )

                if format_dict_array[(idx+0)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                        fail_code = 100
                        is_match_pattern = True

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.STROKE_WIDTH_MIN:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.STROKE_WIDTH_AVERAGE:
                            if format_dict_array[(idx+2)%nodes_length]['distance'] >= self.config.STROKE_WIDTH_MIN:
                                is_match_pattern = True

                # dot +1 angle skip small angle
                # PS: disable this check will cause endless loop.
                if is_match_pattern:
                    fail_code = 210
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= 13:
                        is_match_pattern = False

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # +1 angle skip small angle
                if is_match_pattern:
                    fail_code = 300
                    previous_x,previous_y=spline_util.two_point_extend(x1,y1,x2,y2,-1 * self.config.ROUND_OFFSET)
                    next_x,next_y=spline_util.two_point_extend(x3,y3,x2,y2,-1 * self.config.ROUND_OFFSET)
                    d3 = spline_util.get_distance(previous_x,previous_y,next_x,next_y)
                    if d3 <= self.config.ROUND_OFFSET * 0.5:
                        #print("match too small angel.")
                        is_match_pattern = False

                    # skip almost line triangle
                    if is_match_pattern:
                        fail_code = 310
                        # 這裡用 1.5， OK。用來判斷又的筆畫 90度左右角度。
                        if d3 >= self.config.ROUND_OFFSET * 1.5:
                            is_match_pattern = False

                # +2 angle must match small angle
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    mouth_previous_x,mouth_previous_y=spline_util.two_point_extend(x0,y0,x1,y1,-1 * self.config.ROUND_OFFSET)
                    mouth_next_x,mouth_next_y=spline_util.two_point_extend(x2,y2,x1,y1,-1 * self.config.ROUND_OFFSET)
                    d3 = spline_util.get_distance(mouth_previous_x,mouth_previous_y,mouth_next_x,mouth_next_y)
                    if d3 <= self.config.ROUND_OFFSET:
                        #print("match small angel.")
                        is_match_pattern = True

                # stroke in while area. @_@;
                if is_match_pattern:
                    is_match_pattern = False
                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.ROUND_OFFSET, inside_stroke_dict)
                    if not inside_stroke_flag:
                        #print("match is_apply_large_corner:",x1,y1)
                        is_match_pattern = True

                if not is_match_pattern:
                    #print(idx,"debug fail_code #13:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #12:", idx, format_dict_array[idx]['code'])

                    #if True:
                    if False:
                        print("="*30)
                        print("index:", idx)
                        for debug_idx in range(6):
                            print(debug_idx-2,": values for rule13:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("generated_code:", generated_code)
                    apply_rule_log.append(generated_code)

                    # generate small coner.
                    # 這是較佳的長度，但是可能會「深入」筆畫裡。
                    previous_x,previous_y=spline_util.two_point_extend(x1,y1,x2,y2,-1 * self.config.ROUND_OFFSET)
                    next_x,next_y=spline_util.two_point_extend(x3,y3,x2,y2,-1 * self.config.ROUND_OFFSET)

                    # 使用較短的邊。
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= self.config.ROUND_OFFSET:
                        #previous_x,previous_y=x1,y1
                        # 直接使用 x1,y1 需要改其程式，因為"點共用"
                        previous_x,previous_y=spline_util.two_point_extend(x1,y1,x2,y2,-1 * (format_dict_array[(idx+1)%nodes_length]['distance']-2))
                    if format_dict_array[(idx+2)%nodes_length]['distance'] <= self.config.ROUND_OFFSET:
                        #next_x,next_y=x3,y3
                        # 直接使用 x3,y3 需要改其程式，因為"點共用"
                        next_x,next_y=spline_util.two_point_extend(x3,y3,x2,y2,-1 * (format_dict_array[(idx+2)%nodes_length]['distance']-2))

                    # stronge version
                    #previous_recenter_x,previous_recenter_y=x1,y1
                    #next_recenter_x,next_recenter_y=x1,y1

                    # make curve more "SOFT"
                    previous_recenter_x = int((previous_x + x2)/2)
                    previous_recenter_y = int((previous_y + y2)/2)

                    next_recenter_x = int((next_x + x2)/2)
                    next_recenter_y = int((next_y + y2)/2)

                    # update 1
                    format_dict_array[(idx+2)%nodes_length]['x']= previous_x
                    format_dict_array[(idx+2)%nodes_length]['y']= previous_y

                    old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
                    old_code_array = old_code_string.split(' ')
                    if format_dict_array[(idx+2)%nodes_length]['t']=="c":
                        # [TODO]: move x1,y1 maybe..

                        old_code_array[5] = str(previous_x)
                        old_code_array[6] = str(previous_y)
                    else:
                        # l
                        old_code_array[1] = str(previous_x)
                        old_code_array[2] = str(previous_y)
                    new_code = ' '.join(old_code_array)
                    # only need update code, let formater to re-compute.
                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code
                    #print("rule13 update +2 code:", new_code)


                    # for Rule#99 to avoid same code apply twice.
                    #print("generated_code:", new_code)
                    apply_rule_log.append(new_code)
                    # 不確定下面這行是否會造成什麼問題。
                    apply_rule_log.append(format_dict_array[(idx+1)%nodes_length]['code'])

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

                    format_dict_array.insert((idx+3)%nodes_length,dot_dict)
                    #print("rule13 appdend +3 new_code:", new_code)
                    apply_rule_log.append(new_code)

                    # 由於"點共用"，for skip_coordinate，所以要增加新的點, 
                    # PS: 目前已全部刪掉 skip_coordinate，改用 apply_rule_log.
                    #     等程式都沒問題後，下一版會刪掉這一個block 的code.
                    if False:
                        mouth_next_x_deep,mouth_next_y_deep=spline_util.two_point_extend(x3,y3,x2,y2,-1 * (self.config.ROUND_OFFSET+3))
                        if idx > (idx+3)%nodes_length:
                            idx +=1
                        nodes_length = len(format_dict_array)
                        new_code = ' %d %d l 1\n' % (mouth_next_x_deep, mouth_next_y_deep)

                        dot_dict={}
                        dot_dict['x']=mouth_next_x_deep
                        dot_dict['y']=mouth_next_y_deep
                        dot_dict['t']='.'
                        dot_dict['code']=new_code

                        format_dict_array.insert((idx+4)%nodes_length,dot_dict)
                        apply_rule_log.append(new_code)

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


        return redo_travel, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log
