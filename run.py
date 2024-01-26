import pandas as pd
import json
import parameters
import llm_function
from dfs import *
import record_function as record
import re
import time
import crosswords_function as crosswords
import draw
import acc

if __name__ == '__main__':
    llm = llm_function.get_llm() # 取得語言模型
    locs = list() # 儲存結果的列表

    print('llm ok')
    record.Init_record_file(parameters.all_json_file_name, '') # 初始化整體 JSON 記錄檔案
    parameters.reset_idx() # 重置節點索引
    for i in range(parameters.initial_idx, parameters.initial_idx + parameters.question_sets): #一題跑一圈
        # initialize(為每個問題集初始化紀錄檔案)
        record.Init_record_file(parameters.file_name, parameters.model_path + '\ntemperature: ' + str(parameters.temperature) + '\n')
        record.Init_record_file(parameters.json_file_name, '')
        crosswords.env.reset() # 重置填字遊戲環境
        nodes = [{'id': crosswords.env.get_id(), 'answer': None, 'value': None, 'parent_node': None, 'ancestor_value': None}] # 初始節點，沒有答案
        #call dfs
        start_time = time.time()
        loc = dfs(llm, nodes)
        end_time = time.time()
        # record
        loc['id'] = parameters.idx
        #loc['T/F'] = acc.Acc(parameters.data_path_crosswords, loc['answer'], i)
        loc['cost time'] = end_time - start_time
        locs.append(loc)
        record.Record_json(parameters.json_file_name, loc)
        print(loc)
        crosswords.env.reset() # 重置填字遊戲環境，準備處理下一個問題集
        parameters.increase_idx() # 下一題
    record.Record_json(parameters.all_json_file_name, locs) # 紀錄所有問題集的總體結果
    draw.Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))