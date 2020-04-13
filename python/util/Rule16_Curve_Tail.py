#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 16
# 已灣，且向後翹的尾巴。
# PS: 因為 array size change, so need redo.
# PS: too many condition in one rule, make the rule COMPLEX.
#     but, too many RULE, make maintain code COMPLEX.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
        redo_travel=False

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 4
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                if [format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y']] in skip_coordinate:
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                is_match_pattern = False


                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in [[874,418]]):
                    #continue

                #print("-"*20)
                #print(idx,"debug rule16:",format_dict_array[idx]['code'])

                #if True:
                if False:
                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule16:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                rule_no=16
                is_match_pattern, fail_code = self.rule_test(format_dict_array,idx,rule_no,inside_stroke_dict)

                if not is_match_pattern:
                    #print(idx,"debug fail_code16:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #16:", idx, format_dict_array[idx]['code'])

                    #if True:
                    if False:
                        print("="*30)
                        print("index:", idx)
                        for debug_idx in range(6):
                            print(debug_idx-2,": values for rule16:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                    center_x,center_y = self.apply_round_transform(format_dict_array,idx)

                    # cache transformed nodes.
                    # 加了，會造成其他的誤判，因為「點」共用。
                    #skip_coordinate.append([format_dict_array[idx]['x'],format_dict_array[idx]['y']])
                    
                    # we generated nodes
                    skip_coordinate.append([center_x,center_y])
                    
                    # next_x,y is used for next rule!
                    # 加了，會造成其他的誤判，因為「點」共用。
                    #skip_coordinate.append([new_x2,new_y2])

                    # keep the new begin point [FIX]
                    # 加了，會造成其他的誤判，因為「點」共用。例如「甾」的右上角。
                    #skip_coordinate.append([new_x1,new_y1])

                    redo_travel=True
                    #resume_idx = idx
                    resume_idx = -1
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
