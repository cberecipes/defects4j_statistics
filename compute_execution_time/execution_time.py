import random
from os import path, walk
from datetime import datetime

from RQ3_H2 import point_biserial_correlation_v3
from util import read_config
from utils import utils

results_folder_path = 'compute_execution_time/results'
project_config = read_config(['project_details.properties'])


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        for_each_project(project)


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    extracted_results_path = project_config.get('paths', 'extracted_results_path')

    for root, dirs, files in walk(extracted_results_path):
        for file in files:
            if is_valid_file(str(file)):
                print("deleted " + str(file))


def is_valid_file(file_name):
    return True
