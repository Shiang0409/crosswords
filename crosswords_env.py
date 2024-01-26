import json
import parameters
import re

class CrosswordsEnv():
    def __init__(self, file_name): # 初始化填字遊戲環境，讀取填字遊戲數據
        self.all_data = self.load_data(file_name)
        self.id = 0

    def get_id(self): # 取得唯一識別 id
        self.id += 1
        return self.id - 1

    def load_data(self, file_name): # 從檔案中讀取填字遊戲數據
        data = None
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data

    def reset(self, board = None, status = None, t = None, id = None): # 重置填字遊戲環境的狀態
        self.board = ['_'] * 25 # 25 blanks on the board
        self.ans = ['_____'] * 10 # memory each line
        self.status = [0] * 10 # 10 lines status 0: Unfilled, 1: Filled, 2: Changed
        self.t = 0 # steps
        self.id = 0
        self.data = self.all_data[parameters.idx][0]  # 從數據集中取得填字遊戲數據
        # 如果有提供初始值，則應用
        if board != None:
            self.board = board
            self.ans = self.get_ans(self.board)
        if status != None:
            self.status = status
        if t != None:
            self.t = t
        if id != None:
            self.id = id

    def board_render(self): # 以字串形式呈現目前的棋盤
        string = 'Current Board\n' 
        for i in range(5):
            string += ''.join(self.board[i * 5 : (i + 1) * 5])
            string += '\n'
        return string

    def get_lines(self, status): # 取得指定狀態的填字行數據
        lines = list()
        # horizontal
        for i in range(5):
            #print(self.data[i])
            if status == None or self.status[i] == status:
                lines.append(f'h{i + 1}. ' + self.data[i] + ': ' + ''.join(self.board[i * 5 : (i + 1) * 5]))
        # vertical
        for i in range(5):
            if status == None or self.status[i + 5] == status:
                lines.append(f'v{i + 1}. ' + self.data[i + 5] + ': ' + ''.join(self.board[i::5]))
        return lines

    def get_ans(self, board):  # 取得填字答案
        ans = [''] * 10
        for i in range(5):
            ans[i] = ''.join(board[i * 5 : (i + 1) * 5])
        for i in range(5):
            ans[i + 5] = ''.join(board[i::5])
        return ans

    def ans_render(self): # 以字串形式呈現填字答案
        string = 'Unfilled:\n'
        string += '\n'.join(self.get_lines(status = 0))
        string += '\n'
        string += '\n'.join(self.get_lines(status = 2))
        string += '\n'

        return string

    def change_env(self, ans): # 更改填字遊戲環境
        if ans == None:
            return
        # 定義正則表達式模式，用於解析填字命令格式
        format = r'^([hv][1-5])\. ([a-zA-Z]{5}).*$'
        match = re.match(format, ans)
        if not match: # 如果填字命令格式不匹配，直接返回
            return
        line_index, answer = match.group(1), match.group(2) # 從正則匹配中獲取填字命令的行索引和答案
        l = int(line_index[1]) - 1 # 行索引轉換為列表索引
        print(f'line_index = {l}')
        direction = line_index[0]
        # status(更新行狀態)
        for i in range(5):
            self.status[i] = 0
            if all(element != '_' for element in self.board[i * 5 : (i + 1) * 5]):
                self.status[i] = 1
        for i in range(5):
            self.status[i + 5] = 0
            if all(element != '_' for element in self.board[i::5]):
                self.status[i + 5] = 1
        # board(根據填字方向更新棋盤)
        if direction == 'h':
            self.board[l * 5 : (l + 1) * 5] = [char for char in answer]
        if direction == 'v':
            self.board[l::5] = [char for char in answer]
        # t
        self.t += 1
        #ans(更新填字答案)
        self.ans = self.get_ans(self.board)