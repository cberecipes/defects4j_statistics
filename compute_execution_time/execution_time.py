import time
from os import walk, stat, path

from util import read_config
from utils import utils

results_folder_path = 'compute_execution_time/results'
project_config = read_config(['project_details.properties'])


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        file_path = 'compute_execution_time/results/execution_time_for__' + project
        result = for_each_project(project)
        utils.write_list_as_csv(result, file_path + '.csv')


def for_each_project(project_name):
    result = []
    project_range = project_config.get('projects', project_name).split(",")
    extracted_results_path = project_config.get('paths', 'extracted_results_path') + '/' + project_name

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        folder_path = extracted_results_path + '/trace_files/' + str(project_id) + 'f/'
        for root, dirs, files in walk(folder_path):
            for file in files:

                if is_valid_file(str(file)):
                    tmp_result = [project_name, project_id,
                                  str(file).split(".")[0],
                                  time.strftime('%d.%m.%Y %H:%M:%S',
                                                time.localtime(stat(path.join(root, file)).st_mtime)),
                                  int(stat(path.join(root, file)).st_mtime)]

                    print(tmp_result)
                    result.append(tmp_result)
    return result


def is_valid_file(file_name):
    return file_name.__contains__("slice.output")
