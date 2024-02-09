import parameters
import draw
import acc

'''
print(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
draw.Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
'''
'''
response = ['b', 'e', 's', 'i', 'e', 'e', 'o', 'e', 'n', 't', 'p', 'r', 'e', 's', 's', 't', 'o', 'b', 'e', 's', 'm', 'o', 'r', 'e', 'f']
acc.Acc(response, 2)
'''
'''
all_average = [0.3, 0.4]
all_parse_lines = [[['h1', 'apple', 5], ['h2', 'a', 4], ['h3', 'ap', 3], ['h4', 'app', 2], ['h5', 'appl', 1]], [['h6', 'apple', 5], ['h7', 'a', 4], ['h8', 'ap', 3], ['h9', 'app', 2], ['h10', 'appl', 1]]]
parsed_lines = all_parse_lines[all_average.index(max(all_average))]
parsed_lines = [(line[0].lower() + '. ' + line[1].lower(), 0) for line in parsed_lines] # 格式轉換為方便後續處理的形式
parsed_lines = sorted(parsed_lines, key = lambda x: x[1], reverse = True) # 根據信心水準進行排序
print(f'Highest {max(all_average)}')
print('\nparsed lines:\n')
print(parsed_lines)
'''
def f(s):
    s += 1
    if s != 10:
        f(s)
    else:
        print('finish')
        s = 0
    print(s)
if __name__ == '__main__':
    print(f(0))
