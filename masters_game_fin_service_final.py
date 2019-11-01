from flask import Flask, url_for
from flask import request
from flask import Response
from flask import json
import numpy as np
from flask_cors import CORS
from optparse import OptionParser

app = Flask(__name__)
CORS(app)


@app.route('/get_comp_code', methods = ['GET'])
def api_get_comp_code():

    global colorList,game_size,valid_states_1,valid_states_2,code_comb_list,code_2

    colorList = ['r','g','b','y']
    game_size = 3
    valid_states_1 = {}
    valid_states_2 = {}
    code_comb_list = []
    code_2_in = np.random.randint(65,size=1)
    ct = 0
    code_1 = ''
    code_2 = ''
    for i in range(0,len(colorList)):
        code_comb_1 = colorList[i]
        for j in range(0,len(colorList)):
            code_comb_2 = code_comb_1 + colorList[j]
            for k in range(0,len(colorList)):
                code_comb_3 = code_comb_2 + colorList[k]
                ct = ct+1
                if ct == code_2_in:
                    code_2 = code_comb_3
                code_comb_list.append(code_comb_3)
                valid_states_1[code_comb_3] = 1
                valid_states_2[code_comb_3] = 1

    data = {
        'code'  : code_2
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')

    return resp

@app.route('/get_feedback', methods = ['POST'])
def api_get_feedback():

    if request.headers['Content-Type'] == 'application/json':
        js = request.json
        if js['data'] and js['data']['guess_code']:
            user_code = js['data']['code']
            guess_code = js['data']['guess_code']
            feedback_one,feedback_two = get_feedbacks(guess_code,user_code,code_2,colorList)
            feedback_data = {
                'feed_user' : feedback_one,
                'feed_comp' : feedback_two
            }
            js_new = json.dumps(feedback_data)
            resp = Response(js_new, status=200, mimetype='application/json')
            return resp

@app.route('/get_comp_guess', methods = ['POST'])
def api_get_comp_guess():
    if request.headers['Content-Type'] == 'application/json':
        json_data = request.json
        if json_data['data'] and json_data['data']['player'] == 2:
            guess_code = make_guess(2,valid_states_2,code_comb_list,code_2,colorList)
            guess_data = {
                'comp_guess' : guess_code
            }
            js_new = json.dumps(guess_data)
            resp = Response(js_new, status=200, mimetype='application/json')
            return resp


@app.route('/filter_invalid_states', methods = ['POST'])
def api_filter_invalid_states():

    if request.headers['Content-Type'] == 'application/json':
        js = request.json
        if js['data'] and js['data']['guess_code']:
            filtered_states_and_knowledge = {}
            if js['data']['player'] == 1:
                guess_code = js['data']['guess_code']
                feedback_two = js['data']['feed_comp']
                filter_inval_states_aft_mov(feedback_two,guess_code,valid_states_1,colorList,code_2)
                know_val1 = current_knowldege(1,valid_states_1,colorList)
                filtered_states_and_knowledge['1_states'] = valid_states_1
                filtered_states_and_knowledge['1_know'] = know_val1

            else:
                guess_code = js['data']['guess_code']
                feedback_one = js['data']['feed_user']
                user_code = js['data']['code']
                filter_inval_states_aft_mov(feedback_one,guess_code,valid_states_2,colorList,user_code)
                know_val2 = current_knowldege(2,valid_states_2,colorList)
                filtered_states_and_knowledge['2_states'] = valid_states_2
                filtered_states_and_knowledge['2_know'] = know_val2

            js = json.dumps(filtered_states_and_knowledge)
            resp = Response(js, status=200, mimetype='application/json')
            return resp


@app.route('/filter_invalid_states_and_guess', methods = ['POST'])
def filter_invalid_states_and_guess():
    if request.headers['Content-Type'] == 'application/json':
        js = request.json
        if js['data'] and js['data']['user_guess_code']:
            filtered_states_and_knowledge = {}
            user_code = js['data']['user_code']
            user_guess_code = js['data']['user_guess_code']
            computer_code = code_2
            guess_code = make_guess(2,valid_states_2,code_comb_list,code_2,colorList)
            feedback_one_f_comp,feedback_two_f_comp = get_feedbacks(guess_code,user_code,code_2,colorList)
            feedback_one_f_user,feedback_two_f_user = get_feedbacks(user_guess_code,user_code,code_2,colorList)
            filter_inval_states_aft_mov(feedback_one_f_comp,guess_code,valid_states_2,colorList,user_code)
            filter_inval_states_aft_mov(feedback_two_f_user,user_guess_code,valid_states_1,colorList,code_2)
            know_val2 = current_knowldege(2,valid_states_2,colorList)
            know_val1 = current_knowldege(1,valid_states_1,colorList)
            filtered_states_and_knowledge['comp_states'] = valid_states_2
            filtered_states_and_knowledge['comp_know'] = know_val2
            filtered_states_and_knowledge['user_states'] = valid_states_1
            filtered_states_and_knowledge['user_know'] = know_val1
            filtered_states_and_knowledge['comp_guess_code'] = guess_code
            js = json.dumps(filtered_states_and_knowledge)
            resp = Response(js, status=200, mimetype='application/json')
            return resp


def feedback_from_1_or_2(cur_player_guess,code,colorList):

    code_loc_list = {}
    for col in colorList:
        code_loc_list[col] = []

    feedback_pos = {}
    for game_pos in range(0,game_size):
        feedback_pos[game_pos] = ''

    for i in range(0,len(cur_player_guess)):
        if cur_player_guess[i] == code[i]:
            feedback_pos[i] = 'b'
            code_loc_list[cur_player_guess[i]].append(i)


    for i in range(0,len(cur_player_guess)):
        if feedback_pos[i] == '':
            fdback_loc_val = ''
            for j in range(0,len(code)):
                if cur_player_guess[i] == code[j] and not j in code_loc_list[code[j]]:
                    fdback_loc_val = 'w'
                    code_loc_list[code[j]].append(j)
                    break

            if not fdback_loc_val == '':
                feedback_pos[i] = fdback_loc_val

    feedback = ''
    for i in range(0,len(cur_player_guess)):
        feedback = feedback + feedback_pos[i]

    return feedback

def current_knowldege(cur_player,cur_valid_states,colorList):
    # print("Current valid states for player {}: \n{}".format(cur_player, cur_valid_states))
    know_pos = {0:[],1:[],2:[]}
    col_np = {}
    
    for col in colorList:
        col_np[col] = -1

    for code in cur_valid_states:
        if cur_valid_states[code] == 1:
            for j in range(len(code)):
                if not code[j] in know_pos[j]:
                    know_pos[j].append(code[j])



    know_val = 'K'+str(cur_player)+' ['
    not_and = 0
    for pos in know_pos:
        pos_list = know_pos[pos]
        for j in range(len(pos_list)):
            if j == 0:
                know_val = know_val+ ' ( '+pos_list[j]+str(not_and+1)
            else :
                know_val = know_val+ ' \u2228 '+pos_list[j]+str(not_and+1)
            col_np[pos_list[j]] = not_and

        know_val = know_val + ' ) '
        col_np[pos_list[j]] = not_and
        not_and = not_and +1
        if not not_and == len(know_pos):
            know_val = know_val + ' \u2227 '
    
    
    #know_val = know_val + ' ] '
    for col in col_np:
        if col_np[col] == -1:
            know_val =  know_val + ' \u2227 '+' \u00ac '+col


    know_val = know_val + ' ] '
    return know_val


def get_feedbacks(cur_player_guess,code_1,code_2,color_list):

    feedback_one = feedback_from_1_or_2(cur_player_guess,code_1,color_list)
    feedback_two = feedback_from_1_or_2(cur_player_guess,code_2,color_list)
    return feedback_one,feedback_two

def find_total_match(str1, str2):
    ct = 0
    for i in range(0,str1):
        if str1[i] == str2[i]:
            ct = ct+1
    return ct

def make_guess(cur_player,valid_states,code_comb_list,cur_code,colorList):

    code_pref_list = [-1]*10
    for i in range(0,len(code_comb_list)):
        guess_code = code_comb_list[i]
        one_match_code = ''
        two_match_code = ''
        three_match_code = ''
        if valid_states[guess_code] == 1 :
            feedback_cur = feedback_from_1_or_2(guess_code,cur_code,colorList)
            # print('----------')
            # print(feedback_cur)
            # print(guess_code)
            # print(cur_code)
            # print('--------')
            if feedback_cur == 'w':
                code_pref_list[0] = i
                break;
            elif feedback_cur == 'b':
                code_pref_list[1] = i
            elif feedback_cur == 'ww':
                code_pref_list[2] = i
            elif feedback_cur == 'wb' or feedback_cur == 'bw':
                code_pref_list[3] = i
            elif feedback_cur == 'bb':
                code_pref_list[4] = i
            elif feedback_cur == 'www':
                code_pref_list[5] = i
            elif feedback_cur == 'wbw' or feedback_cur == 'wwb' or feedback_cur == 'bww':
                code_pref_list[6] = i
            elif feedback_cur == 'wbb' or feedback_cur == 'bwb' or feedback_cur == 'bbw':
                code_pref_list[7] = i
            elif feedback_cur == 'bbb':
                code_pref_list[8] = i
            elif feedback_cur == '':
                code_pref_list[9] = i



    best_guess_code = -1
    for val in code_pref_list:
        if not val == -1:
            best_guess_code = code_comb_list[val]
            break;
    return best_guess_code



def filter_inval_states_aft_mov(feedback,guess_code,valid_states,colorList,org_code):
    for code in valid_states:
        if valid_states[code] == 1:

            fdback_for_code = feedback_from_1_or_2(code,guess_code,colorList)
            fdback_for_code2 = feedback_from_1_or_2(org_code,guess_code,colorList)
            feedback_code_dict = {'b':0,'w':0}
            feedback_code2_dict = {'b':0,'w':0}
            for code_in in fdback_for_code:
                if code_in in feedback_code_dict:
                    feedback_code_dict[code_in] = feedback_code_dict[code_in] + 1

            for code_in in fdback_for_code2:
                if code_in in feedback_code2_dict:
                    feedback_code2_dict[code_in] = feedback_code2_dict[code_in] + 1

            flag = True
            for key in feedback_code_dict:
                if not feedback_code_dict[key] == feedback_code2_dict[key]:
                    flag = False
                    break

            if flag:
                valid_states[code] = 1
            else:
                valid_states[code] = 0

    return valid_states


def play_game(gsize,colorList):

    valid_states_1 = {}
    valid_states_2 = {}
    code_comb_list = []
    code_1_in = np.random.randint(65,size=1)
    code_2_in = np.random.randint(65,size=1)
    ct = 0
    code_1 = ''
    code_2 = ''
    for i in range(0,len(colorList)):
        code_comb_1 = colorList[i]
        for j in range(0,len(colorList)):
            code_comb_2 = code_comb_1 + colorList[j]
            for k in range(0,len(colorList)):
                code_comb_3 = code_comb_2 + colorList[k]
                ct = ct+1
                if ct == code_1_in:
                    code_1 = code_comb_3
                if ct == code_2_in:
                    code_2 = code_comb_3
                code_comb_list.append(code_comb_3)
                valid_states_1[code_comb_3] = 1
                valid_states_2[code_comb_3] = 1


    t_num_moves = 30
    cur_move = 0
    #code_1 = "bbr"
    #code_2 = "gbb"
    print('*********')
    print(code_1)
    print(code_2)
    print('*********')
    while(cur_move < t_num_moves):
        # print('--------------')
        # print(valid_states_1)
        # print(valid_states_2)
        # print('------------')
        if cur_move %2 == 0:
            guess_code = make_guess(1,valid_states_1,code_comb_list,code_1,colorList)
            print('cur guess ',str(1),' ',guess_code,' ',code_2)

        else:
            guess_code = make_guess(2,valid_states_2,code_comb_list,code_2,colorList)
            print('------------')

            print('cur guess ',str(2),' ',guess_code,' ',code_1)
            print('----------')

        feedback_one,feedback_two = get_feedbacks(guess_code,code_1,code_2,colorList)
        if (cur_move %2 == 0) and feedback_two == 'bbb':
            print('player one wins')
            break;
        if not (cur_move %2 == 0) and feedback_one == 'bbb':
            print('player 2 wins')
            break;
        if cur_move %2 == 0:
            valid_states_1 = filter_inval_states_aft_mov(feedback_two,guess_code,valid_states_1,colorList,code_2)
            know_val1 = current_knowldege(1,valid_states_1,colorList)
            print((know_val1))
        else:
            valid_states_2 = filter_inval_states_aft_mov(feedback_one,guess_code,valid_states_2,colorList,code_1)
            know_val2 = current_knowldege(2,valid_states_2,colorList)
            print((know_val2))


        cur_move  += 1


#commandline arguments reading
colorList = ['r','g','b','y']
game_size = 3
valid_states_1 = {}
valid_states_2 = {}
code_comb_list = []
code_1_in = np.random.randint(65,size=1)
code_2_in = np.random.randint(65,size=1)
ct = 0
code_1 = ''
code_2 = ''
for i in range(0,len(colorList)):
    code_comb_1 = colorList[i]
    for j in range(0,len(colorList)):
        code_comb_2 = code_comb_1 + colorList[j]
        for k in range(0,len(colorList)):
            code_comb_3 = code_comb_2 + colorList[k]
            ct = ct+1
            if ct == code_1_in:
                code_1 = code_comb_3
            if ct == code_2_in:
                code_2 = code_comb_3
            code_comb_list.append(code_comb_3)
            valid_states_1[code_comb_3] = 1
            valid_states_2[code_comb_3] = 1



if __name__ == '__main__':
    #play_game(3,color_list)
    #feedback_from_1_or_2("gyr","ygb",color_list)
    app.run()