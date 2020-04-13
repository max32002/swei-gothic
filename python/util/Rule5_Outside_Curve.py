#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 5
# check outside curve
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict, skip_coordinate):
        redo_travel=False
        check_first_point = False

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

                # 這個效果滿好玩的，「口」會變成二直，二圓。            
                if self.config.PROCESS_MODE in ["HALFMOON"]:
                    idx_previuos = (idx -1 + nodes_length) % nodes_length
                    if [format_dict_array[idx_previuos]['x'],format_dict_array[idx_previuos]['y']] in skip_coordinate:
                        continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                # for case.3122 上面的點。
                # PS: 由於 half-moon 不套用 #1,2,3
                if self.config.PROCESS_MODE in ["GOTHIC"]:
                    if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                        continue

                # 因為我們程式會去移動下一個點，所以可能前二和後二的距離會是<10.

                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']]==[687,352]) :
                    #continue

                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # debug purpose:
                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']]==[530,836]):
                #if not([x1,y1]==[325,528]):
                    #continue
                
                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                #if True:
                if False:
                    print("-" * 20)
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule5:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')


                # use more close coordinate.
                #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']
                #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # 向下最少 20 點，才能開始長大。
                NEED_TO_EXTEND_DISTANCE_MIN = 15
                # 鄰居要夠長，才能借長度。
                NEED_TO_EXTEND_DISTANCE_SIBLING_MIN = 110
                # 左右 offset <= 8
                NEED_TO_EXTEND_X_OFFSET = 8


                # for .3187, 「力」、「馬」、「号」 系列，有奇怪的停頓點。
                #0 : values for rule1:  286 731 l 1
                #1 : values for rule1:  482 731 l 1
                #2 : values for rule1:  482 702 l 1
                #3 : values for rule1:  475 513 466 441 444 416 c 0
                # PS: for case. 3180, 借高度的，增加先決條件。x_direction + y_direction 要盡量相同。
                # PS: for case. 21324, 「林」，白色部份，不應該被「借高度」。
                is_extend_lag = False
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        # almost vertical.
                        #if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                            # match small distance
                            if abs(format_dict_array[(idx+2)%nodes_length]['x']-format_dict_array[(idx+1)%nodes_length]['x']) <= NEED_TO_EXTEND_X_OFFSET:
                                # not enough long.
                                if format_dict_array[(idx+1)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_MIN:
                                    if format_dict_array[(idx+1)%nodes_length]['distance'] < self.config.OUTSIDE_ROUND_OFFSET:
                                        if format_dict_array[(idx+2)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_SIBLING_MIN:
                                            # 好長哦，借一些來用用。
                                            if format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+2)%nodes_length]['y_direction']:
                                                # extend to new coordinate.
                                                #print("match extend")
                                                is_extend_lag = True

                # 成功的情況下，增加例外。
                # PS: for case. 3180,
                if is_extend_lag:
                    if format_dict_array[(idx+1)%nodes_length]['x_direction'] !=0:
                        if format_dict_array[(idx+1)%nodes_length]['x_direction'] != format_dict_array[(idx+2)%nodes_length]['x_direction']:
                            is_extend_lag = False

                # 成功的情況下，增加例外。
                # PS: for case. 21324,
                if is_extend_lag:
                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                    if not inside_stroke_flag:
                        is_extend_lag = False

                # PS: 該「先長腳」還是等其他所有的判斷都成立，再長腳，應該是後者比較好。目前是使用問題較多的前者。
                if is_extend_lag:
                    extend_x,extend_y=spline_util.two_point_extend(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'], -1 * self.config.OUTSIDE_ROUND_OFFSET)

                    #print("new coordinate:",extend_x,extend_y)
                    format_dict_array[(idx+2)%nodes_length]['x']=extend_x
                    format_dict_array[(idx+2)%nodes_length]['y']=extend_y
                    new_code = ' %d %d l 1\n' % (extend_x, extend_y)
                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                    # [IMPORTANT] if change code, must triger check_first_point=True
                    check_first_point=True

                    # manuall compute distance for PREVIOUS dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                    #print("new distance #1:",new_distance)
                    format_dict_array[(idx+1)%nodes_length]['distance']=new_distance

                    # manuall compute distance for NEXT dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    #print("new distance #2:",new_distance)
                    format_dict_array[(idx+2)%nodes_length]['distance']=new_distance

                # for .31725, 「殳」系列，左上角有奇怪的停頓點。
                #-1 : values for rule5:  486 655 464 676 494 687 c 1 -( 108 )
                #0 : values for rule5:  577 717 571 729 571 764 c 2 -( 43 )
                #1 : values for rule5:  571 807 l 1 -( 257 )
                #2 : values for rule5:  828 807 l 1 -( 80 )

                # 因為「縏」筆畫很擠，只設 90
                NEED_TO_EXTEND_DISTANCE_SIBLING_MIN = 90

                extend_lag_flag = False
                idx_previuos = (idx+nodes_length-1)%nodes_length
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        # almost vertical.
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                            # match small distance
                            if abs(format_dict_array[(idx+0)%nodes_length]['x']-format_dict_array[(idx+1)%nodes_length]['x']) <= NEED_TO_EXTEND_X_OFFSET:
                                # not enough long.
                                if format_dict_array[(idx+0)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_MIN:
                                    if format_dict_array[(idx+0)%nodes_length]['distance'] < self.config.OUTSIDE_ROUND_OFFSET:
                                        if format_dict_array[idx_previuos]['distance'] >= NEED_TO_EXTEND_DISTANCE_SIBLING_MIN:
                                            # 好長哦，借一些來用用。
                                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[idx_previuos]['y_direction']:
                                                extend_lag_flag = True
                if extend_lag_flag:
                    # extend to new coordinate.
                    #print("match extend lag")
                    extend_x,extend_y=spline_util.two_point_extend(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'], -1 * self.config.OUTSIDE_ROUND_OFFSET)

                    offset_x = extend_x - format_dict_array[(idx+0)%nodes_length]['x']
                    offset_y = extend_y - format_dict_array[(idx+0)%nodes_length]['y']

                    #print("old coordinate:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'])
                    #print("new coordinate:",extend_x,extend_y)
                    #print("offset:",offset_x,offset_y)
                    format_dict_array[(idx+0)%nodes_length]['x']=extend_x
                    format_dict_array[(idx+0)%nodes_length]['y']=extend_y

                    old_code_string = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("old_code_string:",old_code_string)
                    old_code_array = old_code_string.split(' ')
                    if format_dict_array[(idx+0)%nodes_length]['t']=='c':
                        old_code_array[1] = str(int(old_code_array[1])+offset_x)
                        old_code_array[2] = str(int(old_code_array[2])+offset_y)
                        old_code_array[3] = str(int(old_code_array[3])+offset_x)
                        old_code_array[4] = str(int(old_code_array[4])+offset_y)
                        old_code_array[5] = str(extend_x)
                        old_code_array[6] = str(extend_y)
                    else:
                        old_code_array[1] = str(extend_x)
                        old_code_array[2] = str(extend_y)
                    new_code = ' '.join(old_code_array)
                    format_dict_array[(idx+0)%nodes_length]['code'] = new_code
                    #print("new_code:", new_code)

                    # [IMPORTANT] if change code, must triger check_first_point=True
                    check_first_point=True


                    # manuall compute distance for PREVIOUS dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                    #print("new distance #1:",new_distance)
                    format_dict_array[(idx+0)%nodes_length]['distance']=new_distance

                    # manuall compute distance for PREVIOUS PREVIOUS dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[idx_previuos]['x'],format_dict_array[idx_previuos]['y'])
                    #print("new distance #2:",new_distance)
                    format_dict_array[idx_previuos]['distance']=new_distance


                # pre-format for 「甾」系列的《
                #+0 : values for rule5:  548 428 516 414 501 441 c 1 -( 215 )
                #+1 : values for rule5:  495 471 448 555 396 629 c 1 -( 190 )
                #+2 : values for rule5:  437 694 464 745 488 796 c 1 -( 52 )
                LONG_EDGE_DISTANCE=120
                
                # PS: >= 0.01 很可怕，ex:「叔」系列。
                DISTANCE_IN_LINE_ACCURACY = 0.004

                idx_previuos = (idx+nodes_length-1)%nodes_length
                # converted by our others rule.
                #if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                if format_dict_array[(idx+0)%nodes_length]['t'] == 'c':
                    # converted by our others rule.
                    #if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':

                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= LONG_EDGE_DISTANCE:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= LONG_EDGE_DISTANCE:
                            # maybe tranformed by our small curve
                            #if format_dict_array[(idx+2)%nodes_length]['match_stroke_width']:
                            
                            # for 「㚢」
                            #if format_dict_array[(idx+2)%nodes_length]['distance'] <= self.config.STROKE_WIDTH_MAX:
                            if True:
                                # maybe tranformed by our small curve
                                #if format_dict_array[idx_previuos]['match_stroke_width']:
                                # for 「㚢」
                                if True:
                                #if format_dict_array[idx_previuos]['distance'] <= self.config.STROKE_WIDTH_MAX:
                                    is_match_direction = False

                                    # go left-top
                                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                                            # go right-top
                                            if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                                                if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0:
                                                    #print("mom I am here.")
                                                    is_match_direction = True

                                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] < 0:
                                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0:
                                            # go right-bottom
                                            if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0:
                                                if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                                                    #print("mom I am here.")
                                                    is_match_direction = True

                                    if is_match_direction:
                                        if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                                            x1=format_dict_array[(idx+0)%nodes_length]['x']
                                            y1=format_dict_array[(idx+0)%nodes_length]['y']
                                            x2=format_dict_array[(idx+1)%nodes_length]['x']
                                            y2=format_dict_array[(idx+1)%nodes_length]['y']
                                            x2_1 = format_dict_array[(idx+1)%nodes_length]['x1']
                                            y2_1 = format_dict_array[(idx+1)%nodes_length]['y1']
                                            x2_2 = format_dict_array[(idx+1)%nodes_length]['x2']
                                            y2_2 = format_dict_array[(idx+1)%nodes_length]['y2']
                                            if spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY) and spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY):
                                                #print("convert c to l#1!")
                                                format_dict_array[(idx+1)%nodes_length]['x']=x2
                                                format_dict_array[(idx+1)%nodes_length]['y']=y2
                                                format_dict_array[(idx+1)%nodes_length]['t']='l'
                                                new_code = ' %d %d l 1\n' % (x2, y2)
                                                format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                                                # [IMPORTANT] if change code, must triger check_first_point=True
                                                check_first_point=True

                                        if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':                                                    
                                            x1=format_dict_array[(idx+1)%nodes_length]['x']
                                            y1=format_dict_array[(idx+1)%nodes_length]['y']
                                            x2=format_dict_array[(idx+2)%nodes_length]['x']
                                            y2=format_dict_array[(idx+2)%nodes_length]['y']
                                            x2_1 = format_dict_array[(idx+2)%nodes_length]['x1']
                                            y2_1 = format_dict_array[(idx+2)%nodes_length]['y1']
                                            x2_2 = format_dict_array[(idx+2)%nodes_length]['x2']
                                            y2_2 = format_dict_array[(idx+2)%nodes_length]['y2']
                                            if spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY) and spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY):
                                                #print("convert c to l#2!")
                                                format_dict_array[(idx+2)%nodes_length]['x']=x2
                                                format_dict_array[(idx+2)%nodes_length]['y']=y2
                                                format_dict_array[(idx+2)%nodes_length]['t']='l'
                                                new_code = ' %d %d l 1\n' % (x2, y2)
                                                format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                                                # [IMPORTANT] if change code, must triger check_first_point=True
                                                check_first_point=True


                # match llc(姚) or cll(源)
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    fail_code = 100
                    is_match_pattern = True

                # [同時增加處理case] for 丸的尾巴，是  ccl,
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    fail_code = 110
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                            is_match_pattern = True

                # =============================================
                # [IMPORTANT] 這條線以下，不要增追加可能的 case.
                # =============================================

                # 排除 16 號Rule.
                # 這個，應該有其他更好&更簡單的解法，暫時沒去想。
                if is_match_pattern:
                    # if match rule no#16, pleas do nothing.
                    rule_no=16
                    fail_code=-1
                    match_rule_16, fail_code=self.rule_test(format_dict_array,idx,rule_no,inside_stroke_dict)
                    if match_rule_16:
                        is_match_pattern = False

                    idx_next=(idx - 1 + nodes_length) % nodes_length
                    match_rule_16, fail_code=self.rule_test(format_dict_array,idx_next,rule_no,inside_stroke_dict)
                    if match_rule_16:
                        is_match_pattern = False

                    idx_previuos=(idx + 1) % nodes_length
                    match_rule_16, fail_code=self.rule_test(format_dict_array,idx_previuos,rule_no,inside_stroke_dict)
                    if match_rule_16:
                        is_match_pattern = False

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                            is_match_pattern = True

                # data been overwrite by pre-format code.
                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                
                # use more close coordinate.
                #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']
                #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                # for case:.3180 「㚓」裡的大，因角度太小，硬被畫白角，變很怪！
                if is_match_pattern:
                    fail_code = 300
                    previous_x,previous_y=spline_util.two_point_extend(x0,y0,x1,y1,-1 * self.config.OUTSIDE_ROUND_OFFSET)
                    next_x,next_y=spline_util.two_point_extend(x2,y2,x1,y1,-1 * self.config.OUTSIDE_ROUND_OFFSET)
                    #print("test data:",x0,y0,x1,y1,x2,y2)
                    #print("previous_x,previous_y:", previous_x,previous_y)
                    #print("next_x,next_y:", next_x,next_y)
                    d3 = spline_util.get_distance(previous_x,previous_y,next_x,next_y)
                    threshold=(self.config.OUTSIDE_ROUND_OFFSET * 0.8)
                    if d3 <= threshold:
                        #print("match too small angel:", self.config.OUTSIDE_ROUND_OFFSET , '-', d3, '-' , threshold)
                        is_match_pattern = False

                    # skip almost line triangle
                    if is_match_pattern:
                        fail_code = 310
                        # PS: 1.7 or 1.8 will meet "甾"!
                        if d3 >= self.config.OUTSIDE_ROUND_OFFSET * 1.8:
                            #print("match too large angel.")
                            is_match_pattern = False



                # 從成功的項目裡，排除已轉彎的項目。
                if is_match_pattern:
                    #if True:
                    if False:
                        print("-" * 20)
                        for debug_idx in range(6):
                            print(debug_idx-2,": values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])

                    # ex: 「扌」和「糸」下方的水平腳
                    #is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[(idx+1)%nodes_length]['y_direction']:
                                # allow some accuracy
                                #if format_dict_array[(idx+1)%nodes_length]['x']==format_dict_array[(idx+2)%nodes_length]['x1']:
                                if abs(format_dict_array[(idx+1)%nodes_length]['x']-format_dict_array[(idx+2)%nodes_length]['x1'])<=4:
                                    is_match_pattern = False

                    # ex: 「繞」右下方的勾
                    #+0 : values for rule1:  771 -2 775 -5 798 -5 c 2xc050
                    #+1 : values for rule1:  875 -5 l 2
                    #+2 : values for rule1:  887 -5 891 -5 894 64 c 1
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == format_dict_array[(idx+1)%nodes_length]['x_direction']:
                                # allow some accuracy
                                #if format_dict_array[(idx+1)%nodes_length]['y']==format_dict_array[(idx+2)%nodes_length]['y1']:
                                if abs(format_dict_array[(idx+1)%nodes_length]['y']-format_dict_array[(idx+2)%nodes_length]['y1'])<=4:
                                    center_x = int((format_dict_array[(idx+1)%nodes_length]['x']-format_dict_array[(idx+2)%nodes_length]['x'])/2)
                                    #print("center_x:", center_x)
                                    # 力量線過半，即為曲線。
                                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0:
                                        #go right
                                        if format_dict_array[(idx+2)%nodes_length]['x1'] >= center_x:
                                            is_match_pattern = False
                                    else:
                                        #go left
                                        if format_dict_array[(idx+2)%nodes_length]['x1'] <= center_x:
                                            is_match_pattern = False


                # compare distance, muse large than our "large round"
                is_apply_large_corner = False

                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False

                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                    #print(idx,"debug rule1+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule1+3:",format_dict_array[(idx+3)%nodes_length]['code'])
                    #print("x1=%d\ny1=%d\nx2=%d\ny2=%d\nx3=%d\ny3=%d" % (previous_x, previous_y, x1, y1, next_x, next_y))
                    #print("y_offset=", self.bmp_y_offset)
                    #print("inside_stroke_flag:", inside_stroke_flag)

                    if inside_stroke_flag:
                        # match outside large conver.
                        #print("match large coner")
                        #print(idx,"large rule5:",format_dict_array[idx]['code'])
                        is_apply_large_corner = True
                        is_match_pattern = True
                    else:
                        # 使用圖片去猜，會有遇到 X 這種斜邊的判斷，有點難。
                        # 改用手動輸入的 default stroke width 來判斷 line join.

                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2)
                        #print("check1_flag:",join_flag)
                        if not join_flag:
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            #print("check2_flag:",join_flag)
                            pass

                        #print("final join flag:", join_flag)
                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass

                if not is_match_pattern:
                    #print(idx,"debug fail_code #5:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #5:",idx)

                    #if True:
                    if False:
                        print("-" * 20)
                        for debug_idx in range(6):
                            print(debug_idx-2,": values for rule5:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                    # make coner curve
                    round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    if not is_apply_large_corner:
                        round_offset = self.config.ROUND_OFFSET

                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx)

                    # cache transformed nodes.
                    # we generated nodes
                    # 因為只有作用在2個coordinate. 
                    if self.config.PROCESS_MODE in ["HALFMOON"]:
                        # 加了這行，會讓「口」的最後一個角，無法套到。
                        skip_coordinate.append([previous_x,previous_y])
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

        return redo_travel, resume_idx, inside_stroke_dict, skip_coordinate
