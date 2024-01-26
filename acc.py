import json
import parameters

def Acc(answer, crosswords, i):
    '''
    with open(parameters.data_path_crosswords, 'r') as file: # 讀取交叉字謎的答案
        answer = json.load(file)

    with open(parameters.json_file_name.format(idx = parameters.idx), 'r') as file: # 讀取模型生成的答案
        crosswords = json.load(file)
    '''

    #crosswords = crosswords['answer'] # 從模型生成的答案中提取交叉字謎的答案部分
    print(crosswords)
    answer = [x.lower() for x in answer[0][1]] # 將兩個答案轉換為小寫以進行比較
    print(answer)

    for i in range(5): # 逐行比較水平方向的答案
        if answer[i * 5 : (i + 1) * 5] == crosswords[i * 5 : (i + 1) * 5]:
            print('correct')
        else:
            print('wrong')
        print(crosswords[i * 5 : (i + 1) * 5])
        print(answer[i * 5 : (i + 1) * 5])
    for i in range(5): # 逐行比較垂直方向的答案
        if answer[i::5] == crosswords[i::5]:
            print('correct')
        else:
            print('wrong')
        print(crosswords[i::5])
        print(answer[i::5])
    