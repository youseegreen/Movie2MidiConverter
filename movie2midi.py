#!/usr/bin/python
#
#  Copyright (C) 2021 youseegreen
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


import cv2
import numpy as np
import os
import os.path
import sys
import getopt
import csv
import operator



usage = '''Movie2Midi version 0.1 Feb. 24 2021, usage:

python movie2midi.py <options>
        [-f] <input file>
        -o <output file>
        -s <is use config> True or False 
        -m <margin>
        -d <division value>
        -a <number of utilizing an user assist>
        -l <save logfiles?> 1 or 0
        --title=<string> Adds T: field containing string
'''



# 画面の構造体作っていいね
def SaveGridInfo(f_name, first_frame_index, update_time, bot, top, time_div, left_name, left, right_name, right, white_note_num):
    with open(f_name, "w", newline='') as f:
        sup_writer = csv.writer(f)
        sup_writer.writerows([['first_frame_index', first_frame_index], ['update_time', update_time], ['bot_bar_y', bot], ['top_bar_y', top], ['time_div', time_div], ['leftest_code_name', left_name], ['leftest_bar_x', left], ['rightest_code_name', right_name], ['rightest_bar_x', right], ['white_note_num', white_note_num]])

def GetGridInfoFromText(f_name):
    with open(f_name, "r", newline='') as f:
        sup_reader = csv.reader(f)
        sup_data = [i for i in sup_reader]
        first_frame_index = (int)(sup_data[0][1])
        update_time = (int)(sup_data[1][1])
        bot = (int)(sup_data[2][1])
        top = (int)(sup_data[3][1])
        time_div = (int)(sup_data[4][1])
        left_name = sup_data[5][1]
        left = (int)(sup_data[6][1])
        right_name = sup_data[7][1]
        right = (int)(sup_data[8][1])
        white_note_num = (int)(sup_data[9][1])
    return first_frame_index, update_time, bot, top, time_div, left_name, left, right_name, right, white_note_num


def GetGridFromVideoImage(cap):
    first_frame_index = cap.get(cv2.CAP_PROP_POS_FRAMES)
    r, img = cap.read()

    # Select a frame that shows one bar clearly
    while True:        
        cv2.imshow("Select a frame that shows one bar clearly. p:prev_frame, n:next_frame, q:ok", img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("p"):
            first_frame_index -= 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index)
            r, img = cap.read()
        if key == ord("n"):
            first_frame_index += 1
            r, img = cap.read()
        if key == ord("q"):
            break
    cv2.destroyWindow("Select a frame that shows one bar clearly. p:prev_frame, n:next_frame, q:ok")
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index)

    
    # Choose y_pos of the first note.
    bottom_bar_y = (int)(img.shape[0] / 2)
    while True:
        bar_img = img.copy()
        cv2.line(bar_img, (0, bottom_bar_y), (img.shape[1] - 1, bottom_bar_y), (0, 0, 255), 1)
        cv2.imshow("Choose red_bar_y_pos. w:up, m:down, q:ok", bar_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("w"):
            bottom_bar_y -= 1
        if key == ord("s"):
            bottom_bar_y += 1
        if key == ord("q"):
            break
    cv2.destroyWindow("Choose red_bar_y_pos. w:up, m:down, q:ok")
    cv2.line(img, (0, bottom_bar_y), (img.shape[1] - 1, bottom_bar_y), (0, 0, 255), 1)

    # Select the length of one bar.
    top_bar_y = (int)(img.shape[0] / 2)
    while True:
        bar_img = img.copy()
        cv2.line(bar_img, (0, top_bar_y), (img.shape[1] - 1, top_bar_y), (0, 255, 0), 1)
        cv2.imshow("Choose green_bar_y_pos. w:up, s:down, q:ok", bar_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("w"):
            top_bar_y -= 1
        if key == ord("s"):
            top_bar_y += 1
        if key == ord("q"):
            break
    cv2.destroyWindow("Choose green_bar_y_pos. w:up, s:down, q:ok")
    cv2.line(img, (0, top_bar_y), (img.shape[1] - 1, top_bar_y), (0, 255, 0), 1)

    # Select the length between the bars.
    time_length_map = [["Quarter note", 1], ["Half note", 2], ["Whole note", 4]]
    time_length_index = 2
    while True:
        time_img = img.copy()
        cv2.putText(time_img, time_length_map[time_length_index][0], ((int)(img.shape[1] / 2), top_bar_y + 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        cv2.imshow("Select the length between the bars. 1:Whole note, 2:Half note, 4:Quarter note, q:ok", time_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("1"):
            time_length_index = 2
        if key == ord("2"):
            time_length_index = 1
        if key == ord("4"):
            time_length_index = 0
        if key == ord("q"):
            break
    cv2.destroyWindow("Select the length between the bars. 1:Whole note, 2:Half note, 4:Quarter note, q:ok")
    time_div = time_length_map[time_length_index][1]
    cv2.putText(img, time_length_map[time_length_index][0], ((int)(img.shape[1] / 2), top_bar_y + 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
    

    # Select the leftmost note.
    leftest_bar_x = (int)(img.shape[1] * 0.1)
    while True:
        bar_img = img.copy()
        cv2.line(bar_img, (leftest_bar_x, 0), (leftest_bar_x, img.shape[0] - 1), (255, 0, 0), 1)
        cv2.imshow("Select the leftmost note. d:right, a:left, q:ok", bar_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("a"):
            leftest_bar_x -= 1
        if key == ord("d"):
            leftest_bar_x += 1
        if key == ord("q"):
            break
    cv2.destroyWindow("Select the leftmost note. d:right, a:left, q:ok")
    cv2.line(img, (leftest_bar_x, 0), (leftest_bar_x, img.shape[0] - 1), (255, 0, 0), 1)


    code_name_map = ["C", "D", "E", "F", "G", "A", "B"]
    # Select the leftest note name.
    leftest_note_code_name_value = 0
    leftest_note_octave_name_value = 0
    while True:
        note_img = img.copy()
        cv2.putText(note_img, code_name_map[leftest_note_code_name_value] + str(leftest_note_octave_name_value), (leftest_bar_x, bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
        cv2.imshow("Select the leftest note name. c:C ~ b:B, 0:0 ~ 8:8, q:ok", note_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("a"):
            leftest_note_code_name_value = 5
        if key == ord("b"):
            leftest_note_code_name_value = 6
        if key == ord("c"):
            leftest_note_code_name_value = 0
        if key == ord("d"):
            leftest_note_code_name_value = 1
        if key == ord("e"):
            leftest_note_code_name_value = 2
        if key == ord("f"):
            leftest_note_code_name_value = 3
        if key == ord("g"):
            leftest_note_code_name_value = 4
        if key == ord("0"):
            leftest_note_octave_name_value = 0
        if key == ord("1"):
            leftest_note_octave_name_value = 1
        if key == ord("2"):
            leftest_note_octave_name_value = 2
        if key == ord("3"):
            leftest_note_octave_name_value = 3
        if key == ord("4"):
            leftest_note_octave_name_value = 4
        if key == ord("5"):
            leftest_note_octave_name_value = 5
        if key == ord("6"):
            leftest_note_octave_name_value = 6
        if key == ord("7"):
            leftest_note_octave_name_value = 7
        if key == ord("8"):
            leftest_note_octave_name_value = 8
        if key == ord("q"):
            break
    cv2.destroyWindow("Select the leftest note name. c:C ~ b:B, 0:0 ~ 8:8, q:ok")
    leftest_note_name = code_name_map[leftest_note_code_name_value] + str(leftest_note_octave_name_value)
    cv2.putText(img, leftest_note_name, (leftest_bar_x, bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

    # Select the rightmost note.
    rightest_bar_x = (int)(img.shape[1] * 0.9)
    while True:
        bar_img = img.copy()
        cv2.line(bar_img, (rightest_bar_x, 0), (rightest_bar_x, img.shape[0] - 1), (255, 255, 0), 1)
        cv2.imshow("Select the rightmost note. d:right, a:left, q:ok", bar_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("a"):
            rightest_bar_x -= 1
        if key == ord("d"):
            rightest_bar_x += 1
        if key == ord("q"):
            break
    cv2.destroyWindow("Select the rightmost note. d:right, a:left, q:ok")
    cv2.line(img, (rightest_bar_x, 0), (rightest_bar_x, img.shape[0] - 1), (255, 255, 0), 1)


    # Select the rightest note name.
    rightest_note_code_name_value = 6
    rightest_note_octave_name_value = 6
    note_index_func = lambda c, v: c + v * 7

    while True:
        note_img = img.copy()
        cv2.putText(note_img, code_name_map[rightest_note_code_name_value] + str(rightest_note_octave_name_value), (rightest_bar_x - 30, bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
        cv2.putText(note_img, "white_note_num = " + str(note_index_func(rightest_note_code_name_value, rightest_note_octave_name_value) - note_index_func(leftest_note_code_name_value, leftest_note_octave_name_value) + 1), ((int)((rightest_bar_x + leftest_bar_x) / 2), bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
        cv2.imshow("Select the rightest note name. c:C ~ b:B, 0:0 ~ 8:8, q:ok", note_img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("a"):
            rightest_note_code_name_value = 5
        if key == ord("b"):
            rightest_note_code_name_value = 6
        if key == ord("c"):
            rightest_note_code_name_value = 0
        if key == ord("d"):
            rightest_note_code_name_value = 1
        if key == ord("e"):
            rightest_note_code_name_value = 2
        if key == ord("f"):
            rightest_note_code_name_value = 3
        if key == ord("g"):
            rightest_note_code_name_value = 4
        if key == ord("0"):
            rightest_note_octave_name_value = 0
        if key == ord("1"):
            rightest_note_octave_name_value = 1
        if key == ord("2"):
            rightest_note_octave_name_value = 2
        if key == ord("3"):
            rightest_note_octave_name_value = 3
        if key == ord("4"):
            rightest_note_octave_name_value = 4
        if key == ord("5"):
            rightest_note_octave_name_value = 5
        if key == ord("6"):
            rightest_note_octave_name_value = 6
        if key == ord("7"):
            rightest_note_octave_name_value = 7
        if key == ord("8"):
            rightest_note_octave_name_value = 8
        if key == ord("q"):
            break
    cv2.destroyWindow("Select the rightest note name. c:C ~ b:B, 0:0 ~ 8:8, q:ok")
    rightest_note_name = code_name_map[rightest_note_code_name_value] + str(rightest_note_octave_name_value)
    cv2.putText(img, rightest_note_name, (rightest_bar_x - 30, bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
    white_note_num = note_index_func(rightest_note_code_name_value, rightest_note_octave_name_value) - note_index_func(leftest_note_code_name_value, leftest_note_octave_name_value) + 1
    cv2.putText(img, "white_note_num = " + str(white_note_num), ((int)((rightest_bar_x + leftest_bar_x) / 2), bottom_bar_y + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))


    # Select update time
    update_time = 5
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index + update_time)
    r, img = cap.read()
    cv2.line(img, (0, bottom_bar_y), (img.shape[1] - 1, bottom_bar_y), (0, 0, 255), 1)

    while True:
        cv2.imshow("Select update time. p:prev_frame, n:next_frame, q:ok", img)
        key = cv2.waitKey(0) & 0xff
        if key == ord("p"):
            update_time -= 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index + update_time)
            r, img = cap.read()
            cv2.line(img, (0, bottom_bar_y), (img.shape[1] - 1, bottom_bar_y), (0, 0, 255), 1)
        if key == ord("n"):
            update_time += 1
            r, img = cap.read()
            cv2.line(img, (0, bottom_bar_y), (img.shape[1] - 1, bottom_bar_y), (0, 0, 255), 1)
        if key == ord("q"):
            break
    cv2.destroyWindow("Select update time. p:prev_frame, n:next_frame, q:ok")
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index)

    return (int)(first_frame_index), (int)(update_time), bottom_bar_y, top_bar_y, time_div, leftest_note_name, leftest_bar_x, rightest_note_name, rightest_bar_x, white_note_num





def ExtractNotes(img, top, bot, left, right, notes_data, left_note_name, white_note_num, time_div, bar, min_note_length=0.25, is_consider_triplet=True, log=False, channel_num=2):
    
    image = img[top:bot, left:right]

    height = image.shape[0]
    width = image.shape[1]
    x_unit = width / white_note_num # the width(px) of one white note
    # 400 px, quarter note: 1.0, min: 1/16 note: 0.25 => 100 px
    # 400 px, whole note: 4.0, min, 1/32 note: 0.125 => 12.5 px
    y_unit = height * min_note_length / time_div  # the height(px) of min_note_length
    x_unit_num = (int)(white_note_num)
    y_unit_num = (int)(height / y_unit)

    cv2.imshow("target", image)
    cv2.waitKey(1)

    # reference : http://okkah.hateblo.jp/entry/2018/08/02/163045
    # get gray_scale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # get binary image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # get label info
    label = cv2.connectedComponentsWithStats(gray)

    # オブジェクト情報を項目別に抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0)

    if log == True:
        # ラベリング結果書き出し用に二値画像をカラー変換
        color_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    errors = []

    # オブジェクト情報を利用してラベリング結果を表示
    for i in range(n):
        # 各オブジェクトの外接矩形を赤枠で表示
        x0 = data[i][0]
        y0 = data[i][1]
        w = data[i][2]
        h = data[i][3]
        x1 = x0 + w
        y1 = y0 + h

        # skip miss detections
        # ここ黒鍵が0.7倍ぐらいという主観がはいっている
        if w < x_unit * 0.45:
            continue
        if h < y_unit * 0.5:
            continue

        ###########################################################
        ################# estimate the note name ##################
        ###########################################################
        whitenote2num_map = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
        num2whitenote_map = ["C", "D", "E", "F", "G", "A", "B"]
        # e.g. E4 => E, 4 => 2 + 4 * 7 = 30
        left_whitenote_num = whitenote2num_map[left_note_name[0]] + (int)(left_note_name[1]) * 7

        # if 0.45 < x_unit < 0.75, then the note must a black note
        if w < x_unit * 0.75:
            # e.g.) left_note_num is A0, target note is D#1
            # | |A|     |C| |D|     |F| |G| |A|
            # | |#|     |#| |#|     |#| |#| |#|
            #| A | B | C | D | E | F | G | A | B |
            #|   |   |   |   |   |   |   |   |   |
            #| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
            #              ^^
            #              ||_ (x0 / x_unit) = 3.85
            #              |__ (x0 / x_unit - 0.15) = 3.7
            # then, (int)(x0 / x_unit - 0.15) = 3
            # A0's whitenote_num = 5
            # whitenote_num = 5 + 3 = 8
            # tmp1 = num2wnote[8 % 7 = 1] = D
            # tmp2 = (int)(8 / 7) = 1
            # note_name = D + # + 1 = D#1

            whitenote_num = left_whitenote_num + (int)(x0 / x_unit - 0.15)
            tmp1 = num2whitenote_map[(int)(whitenote_num % 7)]
            tmp2 = str((int)(whitenote_num / 7))
            note_name = tmp1 + "#" + tmp2
            # E#, B# is miss
            if tmp1 == "E" or tmp1 == "B":
                note_name = tmp1 + tmp2

        # if x_unit > 0.75, then the note must a white note
        else:
            # e.g.) left_note_num is C1, target note is E2
            #   |C| |D|     |F| |G| |A|     |C| |D|
            #   |#| |#|     |#| |#| |#|     |#| |#|
            #|C1 | D | E | F | G | A | B |C2 | D | E |
            #|   |   |   |   |   |   |   |   |   |   |
            #| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
            #                                    ^^
            #             (x0 / x_unit) = 9.01___||
            #                                     |__ (x0 / x_unit + 0.15) = 9.16
            # then, (int)(x0 / x_unit + 0.15) = 9
            # C1's whitenote_num = 7
            # whitenote_num = 7 + 9 = 16
            # tmp1 = num2wnote[16 % 7 = 2] = E
            # tmp2 = (int)(16 / 7) = 2
            # note_name = E + 2 = E2
            whitenote_num = left_whitenote_num + (int)(x0 / x_unit + 0.15)
            tmp1 = num2whitenote_map[(int)(whitenote_num % 7)]
            tmp2 = str((int)(whitenote_num / 7))
            note_name = tmp1 + tmp2



        ##########################################################################
        ################# estimate the note duration and start time ##############
        ##########################################################################
        # quarter_note = 1.0
        note_duration = h / y_unit * min_note_length
        note_start_time = (height - y1 + 1) / y_unit * min_note_length

        # e.g.) min : 0.5 (1/8 note)
        # 2.0 ------------------------  ---
        #                                ^
        # 1.5 ------------------------   |
        #        []    | |               |
        # 1.0 ------------------------ half dur.
        #              | |
        # 0.5 ------------------------   |   ---
        #                                |    | : min_note_length
        # 0.0 ------------------------  ---  ---
        #

        # consider note_duration_list
        # this version consider only [if triplet: 0.33] + nCi[min_note_length, ..., 1/8, 1/4, ..., y_unit_num * min_note_length]
        # e.g.) triplet = True, min_note_length = 0.25, y_unit_num = 16, time_div = 4
        # note_dur_cand_list = [0.25, 0.5, 0.75, 1.0, 1.25, 3.25, 3.5, 3.75, 4.0, 0.333]
        # np.linspace(0.25, 4.0, 16) = [0.25, 0.5, 0.75, 1.0, 1.25, 3.25, 3.5, 3.75, 4.0]
        note_dur_cand_list = np.linspace(min_note_length, time_div, y_unit_num)
        if is_consider_triplet == True:
            note_dur_cand_list.append(0.333)
        
        # np.linspace(0.25, 4.0, 17) = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 3.25, 3.5, 3.75, 4.0]
        note_start_cand_list = np.linspace(0, time_div, y_unit_num + 1)
        if is_consider_triplet == True:
            # np.linspace(0, 4.0, 4*3+1) = [0.0, 0.333, 0.666, 1, 1.333, ..., 3.666, 4]
            # np.concatenate([a, b]) = [0.0, 0.25, 0.5, 0.75, 1.0,... 4.0, 0.0, 0.333, 0.666, 1, 1.333, ..., 3.666, 4]
            # np.unique() = [0.0, 0.25, 0.5, 0.75, 1.0,... 4.0, 0.333, 0.666, 1.333, ..., 3.666]
            # To reduce the priority of the triplet, sort is not done.
            note_start_cand_triplet_list = np.unique(np.concatenate([note_start_cand_list, np.linspace(0, time_div, (int)(time_div * 3 + 1))]))
        
        # Select the nearest value from the candidate list
        pred_note_duration=note_dur_cand_list[np.abs(note_dur_cand_list - note_duration).argmin()]
        if note_duration == 0.333:
            ## ここを-1を+1とみるのでなく、重みづけでどうにかしたい
            pred_note_start_time = note_start_cand_triplet_list[np.abs(note_start_cand_triplet_list - note_start_time).argmin()]
        else:  # if note_duration is not the triplet, then the triplet list is not used.
            pred_note_start_time = note_start_cand_list[np.abs(note_start_cand_list - note_start_time).argmin()]

        # 推定と実際の値の誤差
        # この値が大きいと、正しく推定できていない可能性がupする
        errors.append(pred_note_start_time - note_start_time)

        # channel  will fix
        note_channel = 0
        color = image[int(center[i][1]), int(center[i][0])]
        if channel_num == 2 and color[0] > color[2]:
            note_channel = 1

      #  midi_note = {"time":bar * time_div + pred_note_start_time, "channel":note_channel, "note_name":note_name, "duration":pred_note_duration}
        midi_note = [bar * time_div + pred_note_start_time, note_channel, note_name, pred_note_duration]
        notes_data.append(midi_note)

        if log == True:
        # 各オブジェクトのラベル番号と面積に黄文字で表示
            cv2.putText(color_image, "ID: " +str(i + 1), (x0, y1 + 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
            cv2.rectangle(color_image, (x0, y0), (x1, y1), (0, 0, 255))
            cv2.putText(color_image, note_name + " " + str(pred_note_duration) + " " + str(pred_note_start_time), (x0, y1 - 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        # 各オブジェクトの重心座標をに黄文字で表示
    #     cv2.putText(color_src, "X: " + str(int(center[i][0])), (x1 - 10, y1 + 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
    #     cv2.putText(color_src, "Y: " + str(int(center[i][1])), (x1 - 10, y1 + 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
    if log == True:
        #画像の保存
        cv2.imwrite('./log/log_extracted_image.png', color_image)
        #print(self.midiData)

    if len(errors) == 0:
        return 0
    errors_in_quarter_note = np.average(errors)  # 四分音符何個ずれているか　
    errors_in_pixel = height / time_div * errors_in_quarter_note
    if abs(errors_in_quarter_note) > 0.06:
        if log == True:
            print("error_in_pixel" + str(errors_in_pixel))
            cv2.imshow("is This Safe?", image)
            cv2.waitKey(0)
    
    return (int)(errors_in_pixel / 2 - 0.75) if errors_in_pixel < 0 else (int)(errors_in_pixel / 2 + 0.75)




# 次これ実装する
def NormalizeMetaData(meta_data):
    # テンポとかの違いを上手くまとめる
    # print(len(meta_data))
    # for u in meta_data:
    #     print(u)
    return [meta_data[0]]


def ConvertMidiData(division, notes_data, meta_data):
    midi_data = []
    note2value = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    

    meta2ope = {"tempo":81}
    meta2len = {"tempo": 3}
    for meta in meta_data:
        # meta[0] : absolute_time
        # meta[1] : operation (string)
        # meta[2] : operation_length (int)
        # meta[3] : value
        midi_data.append([meta[0] * division, 'meta', meta2ope[meta[1]], meta2len[meta[1]], (int)(60000000 / meta[2])])


    for note in notes_data:
        # note[0] : absolute_time
        # note[1] : note_channel
        # note[2] : note_pitch (string)
        # note[3] : note_duration
        c = note[2][0:2] if (note[2][1] == "#" or note[2][1] == 'b') else note[2][0:1]
        v = note[2][-1]
        n = note2value[c] + (int)(v) * 12 + 12
        # on
        midi_data.append([note[0] * division, 'midi', 1, note[1], n])
        
        # off
        midi_data.append([(note[0] + note[3]) * division, 'midi', 0, note[1], n])
    


    # midi_data include midi and meta data
    import operator
    midi_data = sorted(midi_data, key=operator.itemgetter(0))
    return midi_data


def ConvertMidiBinaryData(data):
    midi_binary = b''
    prev_time = 0
    length = 0
    prev_run_state = -1

    value2byte_func = lambda v, l: ((int)(v)).to_bytes((int)(l), 'big')


    for d in data:
        # d[0] : abs_cnt
        # d[1] : midi or meta (string)
        # midi
        # d[2] : on or off (1 or 0)
        # d[3] : channel
        # d[4] : pitch value (int)
        # meta
        # d[2] : ope_code (int)
        # d[3] : ope_len (int)
        # d[4] : ope_value (int)

        delta = d[0] - prev_time
        binary, _len = GetDeltaTime(delta)
        
        if d[1] == 'midi':
            # status 
            e_type = 9 * 16 + d[3]
            if e_type != prev_run_state:
                binary = binary + value2byte_func(e_type, 1)
                _len += 1
                prev_run_state = e_type
            # pitch
            binary = binary + value2byte_func(d[4], 1)
            # velocity
            velo = 5 * 16 + 10 if d[2] == 1 else 0
            binary = binary + value2byte_func(velo, 1)
            _len += 2

        else:
            binary = binary + value2byte_func(255, 1)
            binary = binary + value2byte_func(d[2], 1)
            binary = binary + value2byte_func(d[3], 1)
            binary = binary + value2byte_func(d[4], d[3])
            prev_run_state = d[2]
            _len += 3 + d[3]

        midi_binary = midi_binary + binary
        prev_time = d[0]
        length += _len

    return midi_binary, length

# デルタタイムが4バイト以上になる可能性は限りなく0
# ∵ 0~127：1バイト、128~ 2^14=16383：2バイト、16384~2097151：3バイト
def GetDeltaTime(value):
    # 割の使用頻度の高そうな2 byteまでは速攻返すようにする
    if value < 128:
        return ((int)(value)).to_bytes(1, 'big'), 1
    if value < 16384:
        top = (int)(value / 128)
        bot = (int)(value % 128) 
        top = (top + 128).to_bytes(1, 'big')
        bot = (bot).to_bytes(1, 'big')
        return top + bot, 2
    
    v = value
    each_bytes = []
    length = 1

    while v >= 128:
        each_bytes.append(v % 128)
        v = (int)(v / 128)
        length += 1
    each_bytes.append(v)
    ret = b''
    for i in range(length):
        d = each_bytes[length - i - 1]
        if i == length - 1:
            ret = ret + d.to_bytes(1, 'big')
        else:
            ret = ret + ((int)(d + 128)).to_bytes(1, 'big')
    return ret, length




def GetRawMidiData(title, division, midi_data, midi_len):
    # value 2 binary function
    value2byte_func = lambda v, l: ((int)(v)).to_bytes((int)(l), 'big')

    # msg : raw midi data
    # header
    msg = b'MThd'
    header_chunk_size = value2byte_func(6, 4)   # header size 6 
    midi_format = value2byte_func(0, 2)         # format 0
    track_num = value2byte_func(1, 2)           # track number 1
    time_count = value2byte_func(division, 2)   # time_count = division (240 or 480)
    msg = msg + header_chunk_size + midi_format + track_num + time_count

    # track 0 
    msg = msg + b'MTrk'
    track_end = b'\x00\xff\x2F\x00' # 4 byte
    track_length = value2byte_func(midi_len + 4, 4)
    msg = msg + track_length + midi_data + track_end
    return msg


# return the raw midi binary data
def movie2midi(filename, is_use_support_file, margin, assist_num, division, title, is_log):
    if is_log and not os.path.exists('./log'):
        os.mkdir('./log/')

    cap = cv2.VideoCapture('./input_movie/' + filename)
    if cap.isOpened() == False:
        print('Error: file could not read!')
        sys.exit(2)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # get grid of notes and time_div of notes
    support_filename = './config/' + filename[0:-4] + '_sup.txt'

    if not is_use_support_file or not os.path.exists(support_filename):
        first_frame_index, update_time, bot, top, time_div, left_name, left, right_name, right, white_note_num = GetGridFromVideoImage(cap)
        SaveGridInfo('./config/' + filename[0:-4] + "_sup.txt", first_frame_index, update_time, bot, top, time_div, left_name, left, right_name, right, white_note_num)
    else:
    # if not os.path.exists(support_filename):
    #     print('Error: support file could not find : ' + support_filename)
    #     sys.exit(2)
        ext = support_filename[-3:]
        if ext == 'txt' or ext == 'csv':
            first_frame_index, update_time, bot, top, time_div, left_name, left, right_name, right, white_note_num = GetGridInfoFromText(support_filename)
        else:
            print('Error: This support file is not covered! Please use a txt or png file.')
            sys.exit(2)


    notes_data = []  #
    bar = 0  # represent "n-syosetu"
    meta_data = []

    # loi_dyをadaptiveに推定する方法はないだろうか
    judge_height = 100

    # set the frame which first bar appears on y_pos_bot
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame_index)

    # 1小節目だけ推定する
    r, ref_frame = cap.read()
    loi_dy = ExtractNotes(ref_frame, top, bot, left, right, notes_data, left_name, white_note_num, time_div, bar, min_note_length=0.125, is_consider_triplet=False, log=True, channel_num=2)
    bar += 1

    # 次の小節のはじめを推定するための変数達
    prev_bar_frame_num = first_frame_index  # いらない
    skip_frame_num = update_time
    target_loi = ref_frame[top-judge_height+loi_dy:top+loi_dy, left:right]

    while True:
        for i in range(skip_frame_num):
            r, ref_frame = cap.read()
            if not r:
                break
        if not r:
            break

        # now_frameをy方向に-margin~margin(px)動かしたときの、target_loiとの差分画像を計算
        # 最も差が小さいものを利用する
        # もし、error_listの分布がおかしいならば、
        # 1. テンポが変わった。　2. 音符無しゾーン
        # なので、対応する        
        # というより、error_listの分布集めた方がいいですね
        y_bias = 0
        error_list = []
        for dy in range(-margin, margin):
            roi = ref_frame[bot-judge_height + dy: bot + dy, left: right]
            im_diff = np.abs(roi.astype(int) - target_loi.astype(int))
            error = np.sum(im_diff)
            error_list.append([dy, error])

            if is_log == True:
                show_diff = np.uint8(im_diff)
                cv2.imshow("diff", show_diff)
                cv2.waitKey(1)

        if is_log == True:
            if not os.path.exists('./log/errors/'):
                os.mkdir('./log/errors/')
            with open('./log/errors/' + str(bar) + '.csv', 'w', newline='') as f:
                ewriter = csv.writer(f)
                ewriter.writerows(error_list)

        error_list = sorted(error_list, key=operator.itemgetter(1))
        y_bias = error_list[0][0]

        # if estimate_accuracy_might_worse
        # then, use human hueristic

        # by obtaining y_bias, we can calculate the tempo
        # delta_time from the prev bar calc.: delta_time = 1 / fps * skip_frame_num
        # 四分音符何個分進んだか = delta_quarter_note = (height + y_bias) * time_div / height
        # 1秒あたりに四分音符何個分進むか = delta_time / delta_quarter_time
        # tempo = 60 * delta_time / delta_quarter_time
        height = bot - top
        del_time = skip_frame_num / fps
        del_quar_note = (height + y_bias) * time_div / height
        tempo = 60 * del_quar_note / del_time
        meta_data.append([(bar - 1) * time_div, "tempo", tempo])
        # if tempo is correct, then we can calculate the appropriate skip_frame_num
        # del_time : del_quar_note = 1 / fps : x?
        # x = (del_quar_note / fps) / del_time = del_quar_note / skip_frame_num
        # x は 1フレームで、四分音符何個分進むかを表す
        # 四分音符がtime_div進むのに適切なxは？
        # x : 1 = time_div : y
        # tmp = time_div / x
        #
        # time_div * skip_frame_num / del_quar_note = time_div * skip_frame_num * height / (time_div * (height + y_bias))
        # if y_bias = 0: skip_frame_num

        loi_dy = ExtractNotes(ref_frame, top, bot, left, right, notes_data, left_name, white_note_num, time_div, bar, min_note_length=0.125, is_consider_triplet=False, log=True, channel_num=2)
#        print(loi_dy)
        print("bar : " + str(bar))
        bar += 1
        prev_bar_frame_num = prev_bar_frame_num + skip_frame_num    # いらない
        skip_frame_num = (int)(time_div / (del_quar_note / skip_frame_num) + 0.5)
        target_loi = ref_frame[top - judge_height + loi_dy:top + loi_dy, left:right]
        if is_log == True:
            cv2.imshow("next_ref", target_loi)
            cv2.waitKey(1)


    # print(len(notes_data))
    # notes_data = sorted(notes_data, key=lambda x: x['time'])
    # for u in notes_data:
    #     print(u)

    # for u in meta_data:
    #     print(u)

    meta_data = NormalizeMetaData(meta_data)
    # midiデータ（音符のオン、オフ）
    midi_data = ConvertMidiData(division, notes_data, meta_data)
    # print(midi_data)
    midi_binary, bin_length = ConvertMidiBinaryData(midi_data)
    # print(midi_binary)
    # print(bin_length)
    raw = GetRawMidiData("hoge", division, midi_binary, bin_length)
    return raw


def main(argv):
    # setup default values
    filename = ''
    output_filename = ''
    safety_margin = 20
    assist_num = 0
    title = None
    division = 240
    is_save_log = False
    is_use_support_file = True

    try:
        opts, args = getopt.getopt(argv, 'h:s:f:o:m:a:l:d', ['title=', 'help=', 'margin=', 'assist=', 'log=', 'division='])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        try:
            if opt in ('-h', '--help'):
                print(usage)
                sys.exit()
            elif opt in ('-m', '--margin'):
                safety_margin = (int)(arg)
            elif opt in ('-a', '--assist'):
                assist_num = (int)(arg)
            elif opt in ('-l', '--log'):
                is_save_log = True
            elif opt in ('-d', '--division',):
                division = (int)(arg)
            elif opt in ('--title',):
                title = arg
            elif opt in ('-f',):
                filename = arg
            elif opt in ('-o',):
                output_filename = arg
            elif opt in ('-s',):
                if arg == 'False':
                    is_use_support_file = False
        except Exception:
            print('Error parsing argument: %s' % opt)
            print(usage)
            sys.exit(2)

    if not filename:
        print('Error: filename (-f) required!')
        print(usage)
        sys.exit(2)

    result = movie2midi(filename, is_use_support_file, safety_margin, assist_num, division, title, is_save_log)

    if output_filename:
        open('./output_midi/' + output_filename, 'wb').write(result)
    else:
        print(result)


if __name__ == '__main__':
    main(sys.argv[1:])
#    main(['-f', 'sample.mp4', '-o', 'sample.midi', '--log=True', '-m', '20'])
