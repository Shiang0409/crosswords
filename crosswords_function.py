from crosswords import *
import json
import llm_function
import parameters
import re
import record_function as record
import crosswords_env
import time

env = crosswords_env.CrosswordsEnv(file_name = parameters.data_path_crosswords)

def Parse_propose_response(response: str):
    format = r'^([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\)$' # 定義提議回應的格式
    parsed_lines = list() # 存放解析後的結果的列表
    for line in response.split('\n'): # 逐行解析提議回應
        print( 'line: ' + line + '\n')
        match = re.match(format, line) # 使用正則表達式進行匹配
        if match: # 如果匹配成功，將各組成部分添加到解析結果中
            parts = [match.group(1), match.group(2), match.group(3)]
            parsed_lines.append(parts)
    return parsed_lines


def Generator(llm, node, refine = False):
    # initialize
    confidence_to_value = {'certain': 1, 'high': 0.75, 'medium': 0.5, 'low': 0.1} # 將信心水準映射到數值，用於排序
    new_nodes = list()  # 存放新生成節點的列表
    # call llm
    input_string = env.board_render() + env.ans_render()
    question = propose_prompt.format(input = input_string, k = parameters.k)
    print('\nquestion:\n' +  question + '\n')
    pattern = r'([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\)'
    patterns = '\n'.join([pattern for i in range(parameters.k)])
    start_time = time.time()
    response = llm_function.call_llm(llm, question, patterns)
    end_time = time.time()
    print('\nresponse:\n' + response + '\n')
    # parse response & return 
    parsed_lines = Parse_propose_response(response + '\n') # 解析模型生成的回應
    # 如果產出的可能性過低，再產一遍
    sum_of_convalue = 0
    count_of_loop = 0
    for line in parsed_lines:
        sum_of_convalue += confidence_to_value.get(line[2], 0)
        count_of_loop += 1
    print(f'\nAvarage confidence value: {sum_of_convalue / count_of_loop}\n')
    if count_of_loop == 0 or sum_of_convalue / count_of_loop < 0.4: 
        print('-----\nGenerate Again!\n-----\n')
        Generator(llm, node, refine = False)
    parsed_lines = [(line[0].lower() + '. ' + line[1].lower(), confidence_to_value.get(line[2], 0)) for line in parsed_lines] # 格式轉換為方便後續處理的形式
    parsed_lines = sorted(parsed_lines, key = lambda x: x[1], reverse = True) # 根據信心水準進行排序
    print('\nparsed lines:\n')
    print(parsed_lines)
    record.Record_txt(parameters.file_name, '\nGenerator: \n' + str(parsed_lines) + '\n') # 將解析後的結果轉換為新節點
    for i in range(len(parsed_lines)): # 將解析後的結果轉換為新節點
        if i == parameters.k:
            break
        new_nodes.append({'id': env.get_id(), 'answer': parsed_lines[i][0], 'value': None, 'parent_node': node['id'], 'ancestor_value': Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])})
    # refine(如果未生成新節點，進行 refine 操作)
    if len(new_nodes) == 0:
        print('refine')
        new_nodes = Generator(llm, node, refine = True)
    if refine == False: # 輸出生成節點或 refine 的相關信息
        print(f'cost time: {end_time - start_time}')
        record.Record_txt(parameters.file_name, 'Generator nodes:\n' + str(new_nodes) + '\ncost time: ' + str(end_time - start_time) + '\n\n')
    else:
        print(f'refine\ncost time: {end_time - start_time}')
        record.Record_txt(parameters.file_name, 'refine\ncost time: ' + str(end_time - start_time) + '\n\n')
    return new_nodes


def Parse_value_response(response, input): #若 response 是 "sure"、"maybe" 或 "impossible" 中的一個，則返回解析後的回應；否則返回 None
    #old ver.
    '''
    short_response = response.strip().split('\n')[-1]
    pattern = fr"Output: ((?:sure)|(?:maybe)|(?:impossible)) \({input}\)"
    answer = re.search(pattern, fr"Output: {short_response} ({input})")
    print(pattern)
    print(f'evaluator parse: {answer}')
    if answer:
        return answer.group(1)
    else:
        return None
    '''
    answer = response.strip().split('\n')[-1]
    print('Last line in response:' + answer)
    if answer == 'sure' or answer == 'maybe' or answer == 'impossible':
        return answer
    elif 'impossible' in response:
        return 'impossible'
    elif 'maybe' in response:
        return 'maybe'
    elif 'sure' in response:
        return 'sure'
    elif ('extremely unlikely' in response) or ('very unlikely' in response):
        return 'impossible'
    else: None


def Evaluator(llm, nodes):
    new_nodes = list()
    for node in nodes: # 對每一個給定的 node 進行評估
        # initialize
        count = {'sure': 0, 'maybe': 0, 'impossible': 0}
        # 儲存當前狀態，以便後續重置
        board = env.board.copy()
        status = env.status.copy()
        t = env.t
        env.change_env(node['answer']) # 將 node 的答案應用於環境
        for i in range(10): # 對每一行及列進行評估
            print(f'\nThe {i+1} row')
            print(env.board_render())
            print(f'env.ans: {env.ans[i]}')
            # skip _____ & ____ answers(跳過包含大量空格的答案)
            if env.ans[i].count('_') >= 4:
                continue
            # 取得當前行的答案
            ans = ''.join(env.ans[i].lower()) 
            line = f'{env.data[i]}: {ans}'
            print('each ans: ' + line)
            question = value_prompt.format(input = line) # 構建問題，使用 value_prompt
            pattern = r"[\d|\w|\s|\+|\-|\*|\/|\=|\(|\)|,|\.|\:|\"|\'|_|;|\!|\?]{0,500}[sure|maybe|impossible]" # 定義模式，用於解析模型回應
            # call llm
            start_time = time.time()
            response = llm_function.call_llm(llm, question, pattern)
            end_time = time.time()
            # parse response & return
            print('\nEvaluator response:\n')
            print(response)
            print(f'\ncost time: {end_time - start_time}')
            record.Record_txt(parameters.file_name, '\ninput: ' + line + '\nEvaluator response: ' + response + '\ncost time: ' + str(end_time - start_time) + '\n')
            answer = Parse_value_response(response, env.ans[i])
            print(f'\nThe value is {answer}\n')
            if answer != None: # 若解析成功，則更新計數
                count[answer] += 1
        node['value'] = count  # 更新 node 的 value 屬性
        record.Record_txt(parameters.file_name, '\nanswer: ' + str(node['answer']) + '\nCount: ' + str(node['value']) + '\n\n') # 將結果記錄下來
        new_nodes.append(node) # 將更新後的 node 加入新節點列表
        env.reset(board = board, status = status, t = t, id = env.id) # 還原環境狀態
    return new_nodes


def Value_mapping(value):
    if value == None: # 若 value 為 None，則返回 0
        return 0
    count = 0 # 初始化計數
    count += value['sure'] * 20 + value['maybe'] + value['impossible'] * 0.001 # 根據給定的權重進行加權計算，然後加總起來
    return count


def Sorted_by_value(node): #回傳一個值，用於比較不同節點的大小
    return Value_mapping(node['value']) + node['ancestor_value']


def Sorted_by_id(node): # 回傳節點的 id，以確保排序的唯一性
    return node['id']
    

if __name__ == '__main__':
    # 初始化棋盤和狀態
    board = '______________________________'
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    env.reset() # 重置環境
    print(env.board_render() + env.ans_render()) # 輸出當前棋盤和狀態 
    env.change_env('h1. agend') # 在水平方向上填入單詞 'agend'
    print(env.board_render() + env.ans_render()) # 輸出當前棋盤和狀態
    env.change_env('v1. amass') # 在垂直方向上填入單詞 'amass'
    print(env.board_render() + env.ans_render()) # 輸出當前棋盤和狀態
    print(env.status) # 輸出狀態
    '''
    node = {'id': env.get_id()}
    llm = llm_function.get_llm()
    env.change_env('h1. agend')
    new_nodes = Generator(llm, node)
    print(new_nodes)
    print(env.board_render())
    board = env.board.copy()
    status = env.status.copy()
    t = env.t
    new_nodes = Evaluator(llm, new_nodes)
    print(new_nodes)
    env.reset(board = board, status = status, t = t, id = env.id)
    print(env.board, env.status, env.t)
    '''