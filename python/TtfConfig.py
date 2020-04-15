#!/usr/bin/env python3
#encoding=utf-8

class TtfConfig():
    PROCESS_MODE = "GOTHIC"
    #PROCESS_MODE = "HALFMOON"

    STYLE_INDEX = 5
    STYLE_ARRAY = ["Black","Bold","DemiLight","Light","Medium","Regular","Thin"]
    STYLE=STYLE_ARRAY[STYLE_INDEX]
    print("Transform Mode:", PROCESS_MODE)
    print("Transform Style:", STYLE)

    DEFAULT_COORDINATE_VALUE = -9999

    # for Regular
    STROKE_MAX = 99
    if STYLE=="Black":
        STROKE_MAX = 114
    if STYLE=="Bold":
        STROKE_MAX = 109
    if STYLE=="DemiLight":
        STROKE_MAX = 90
    if STYLE=="Light":
        STROKE_MAX = 80
    if STYLE=="Medium":
        STROKE_MAX = 104
    if STYLE=="Thin":
        STROKE_MAX = 60

    # 有些筆劃很細，有些很粗，設太細似乎又會誤判。
    # 雖然字變重，但因為筆畫複雜時，還是有細的線條。
    STROKE_MIN = 34
    if STYLE=="Black":
        STROKE_MIN = 36
    if STYLE=="Bold":
        STROKE_MIN = 36
    if STYLE=="DemiLight":
        STROKE_MIN = 34
    if STYLE=="Light":
        STROKE_MIN = 30
    if STYLE=="Medium":
        STROKE_MIN = 34
    if STYLE=="Thin":
        STROKE_MIN = 26

    STROKE_ACCURACY_PERCENT = 10
    STROKE_WIDTH_MAX = int((STROKE_MAX * (100+STROKE_ACCURACY_PERCENT))/100)
    STROKE_WIDTH_MIN = int((STROKE_MIN * (100-STROKE_ACCURACY_PERCENT))/100)
    STROKE_WIDTH_AVERAGE = int((STROKE_MIN+STROKE_MAX)/2)
    #print("STROKE_WIDTH_MAX:", STROKE_WIDTH_MAX)
    #print("STROKE_MIN:", STROKE_WIDTH_MIN)

    # for X,Y axis equal compare.
    # each 100 px, +- 8 px.
    EQUAL_ACCURACY_MIN = 3
    EQUAL_ACCURACY_PERCENT = 0.08

    # for Regular
    ROUND_OFFSET = 33
    if STYLE=="Black":
        ROUND_OFFSET = 38
    if STYLE=="Bold":
        ROUND_OFFSET = 36
    if STYLE=="DemiLight":
        ROUND_OFFSET = 30
    if STYLE=="Light":
        ROUND_OFFSET = 27
    if STYLE=="Medium":
        ROUND_OFFSET = 33
    if STYLE=="Thin":
        ROUND_OFFSET = 20

    # don't access the distance within 5
    NEXT_DISTANCE_MIN = 5

    # for Regular
    OUTSIDE_ROUND_OFFSET = 55
    if STYLE=="Black":
        OUTSIDE_ROUND_OFFSET = 65
    if STYLE=="Bold":
        OUTSIDE_ROUND_OFFSET = 60
    if STYLE=="DemiLight":
        OUTSIDE_ROUND_OFFSET = 50
    if STYLE=="Light":
        OUTSIDE_ROUND_OFFSET = 40
    if STYLE=="Medium":
        OUTSIDE_ROUND_OFFSET = 60
    if STYLE=="Thin":
        OUTSIDE_ROUND_OFFSET = 28

    # 只需要大彎.
    if PROCESS_MODE=="HALFMOON":
        ROUND_OFFSET=OUTSIDE_ROUND_OFFSET
    
    # some inside block not able to fill 2 curve coner, use small one.
    INSIDE_SMALL_ROUND_OFFSET=15

    # unicode in field
    # 1 to 3
    UNICODE_FIELD = 2

    BMP_PATH = '/Users/chunyuyao/Documents/noto/bmp'


    def __init__(self):
        pass

    def hello(self):
        print("world!")