#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 6
# 簡化 c 為 l
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx):
        redo_travel=False

        TOO_CLOSE_DISTANCE = 13

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        #split ned spline
        new_format_dict_array = []

        rule_need_lines = 7
        fail_code = -1
        #print("nodes_length:", nodes_length)
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_match_pattern = False

                #print(idx,": debug rule9:",format_dict_array[idx]['code'])

                x0 = format_dict_array[idx]['x']
                y0 = format_dict_array[idx]['y']
                x1 = self.config.DEFAULT_COORDINATE_VALUE
                y1 = self.config.DEFAULT_COORDINATE_VALUE

                # each time need reset once.
                new_format_dict_array = []

                idx_j_formated=idx
                for idx_j in range(nodes_length-1):
                    idx_j_formated = (idx + idx_j+1) % nodes_length
                    x1 = format_dict_array[idx_j_formated]['x']
                    y1 = format_dict_array[idx_j_formated]['y']

                    new_format_dict_array.append(format_dict_array[idx_j_formated].copy())

                    # skip too sibling
                    if idx_j_formated == idx:
                        continue
                    if idx_j_formated == (idx + 1) % nodes_length:
                        continue
                    if idx_j_formated == (idx + 2) % nodes_length:
                        continue
                    if idx_j_formated == (idx + nodes_length - 1) % nodes_length:
                        continue
                    if idx_j_formated == (idx + nodes_length - 2) % nodes_length:
                        continue

                    compare_distance = spline_util.get_distance(x0,y0,x1,y1)
                    if compare_distance <= TOO_CLOSE_DISTANCE:
                        #print(idx,": match too close rule9:",format_dict_array[idx]['code'])
                        #print(idx,": match too close rule to idx:",idx_j_formated,format_dict_array[idx_j_formated]['code'])
                        is_match_pattern = True
                        break

                
                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                if False:
                    print("-------------------------------")
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule9:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])


                if is_match_pattern:
                    #print("match rule #9")
                    #print(idx,": debug rule9:",format_dict_array[idx]['code'])

                    #print("new dict array length:", len(new_format_dict_array))
                    #print("new dict array:", new_format_dict_array)

                    redo_travel=True
                    #resume_idx = idx
                    #index changed!
                    resume_idx = -1
                    break

        if redo_travel:
            
            # clean orig
            nodes_length = len(new_format_dict_array)
            if nodes_length > 0:
                #print("orig dict array length (before):", len(format_dict_array))
                for idx in range(nodes_length):
                    code = new_format_dict_array[idx]['code']

                    orig_length = len(format_dict_array)
                    for orig_idx in range(orig_length):
                        if format_dict_array[orig_idx]['code']==code:
                            #print("match code at index:",orig_idx)
                            del format_dict_array[orig_idx]
                            break

                #print("orig dict array length (after):", len(format_dict_array))

                # add header for spline
                #print("full new spline:", new_format_dict_array)
                dot_dict={}
                dot_dict['x']=new_format_dict_array[-1]['x']
                dot_dict['y']=new_format_dict_array[-1]['y']
                dot_dict['t']='m'
                new_code = '%d %d m 0\n' % (dot_dict['x'],dot_dict['y'])
                dot_dict['code'] = new_code
                #print("new spline:", new_code)
                new_format_dict_array.insert(0,dot_dict)


        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        # for debug
        #redo_travel=False

        return redo_travel, resume_idx, new_format_dict_array
