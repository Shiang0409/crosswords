import parameters
import draw
import acc


print(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
draw.Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))

'''
response = ['b', 'e', 's', 'i', 'e', 'e', 'o', 'e', 'n', 't', 'p', 'r', 'e', 's', 's', 't', 'o', 'b', 'e', 's', 'm', 'o', 'r', 'e', 'f']
acc.Acc(response, 2)
'''