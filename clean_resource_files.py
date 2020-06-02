from util import read_config, get_project_root
import os
import shutil

project_config = read_config(['project_details.properties'])
defects4j_project_path = project_config.get('paths', 'defects4j_project_path')


def clean_source_dir():
    for root, dirs, files in os.walk(defects4j_project_path):
        folder_path = os.path.join(str(get_project_root()), root)
        if is_deletable(folder_path):
            shutil.rmtree(folder_path, ignore_errors=False, onerror=None)
            print("deleted " + folder_path)
        for file in files:
            if is_deletable(str(file)):
                file_path = folder_path + '/' + str(file)
                os.remove(file_path)
                print("deleted " + file_path)


def is_deletable(name):
    return name.endswith('_dir') or \
           name.endswith('all_test_methods') or \
           name.endswith('running.log') or \
           name.endswith('tracing_completed.json')


clean_source_dir()
