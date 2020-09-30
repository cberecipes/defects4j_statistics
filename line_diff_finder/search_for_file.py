import json

from RQ3_H1.checked_coverage_better_indicator import get_covering_tests, get_modified_coverable_lines
from util import read_config
from os import path

from utils import utils
from utils.utils import get_bug_detecting_tests

project_config = read_config(['../project_details.properties'])


def compute():
    project_name = project_config.get('projects', 'project_list').split(",")
    if len(project_name) > 1:
        print("reduce number of projects to 1")
        exit(0)
    project_name = project_name.pop()

    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    if len(range(int(project_range[0]), int(project_range[1]) + 1)) > 1:
        print('reduce length of projects')
        exit(0)

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        trace_file_path = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"

        checked_coverage = {}
        statement_coverage = {}
        checked_covering_tests = []
        bug_detecting_tests = []
        if path.isdir(trace_file_path):
            patch_path = defects4j_project_path + "/" + project_name + "/" + "/patches/" + str(project_id) + \
                ".src.patch"
            bug_detecting_tests = get_bug_detecting_tests(project_id, defects4j_project_path + "/" + project_name)
            current_project_path = defects4j_project_path + "/" + project_name
            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            coverable_lines = utils.get_coverable_lines(project_id, current_project_path, modified_classes)
            dict_of_modified_coverable_lines = get_modified_coverable_lines(patch_path, coverable_lines)
            checked_coverage = utils.read_json_file(trace_file_path + '/checked_coverage.json')
            statement_coverage = utils.read_json_file(trace_file_path + '/line_coverage.json')
            detailed_checked_covering_tests = get_covering_tests(
                checked_coverage, dict_of_modified_coverable_lines, 'checked_coverable_lines')
            for checked_covering_test in detailed_checked_covering_tests:
                checked_covering_tests.append(checked_covering_test['test'])

#        print(json.dumps(checked_coverage))

        for checked_covering_test in checked_covering_tests:
            for key, value in checked_coverage.items():
                try:
                    checked_covering_details = value[checked_covering_test]
                    statement_covering_details = statement_coverage[key][checked_covering_test]
                    print(key)
                    print("cs {} {}".format(checked_covering_test, statement_covering_details))
                    print("cc {} {}".format(checked_covering_test, checked_covering_details))
                except KeyError:
                    pass
        print("#########################################################")
        for bug_detecting_test in bug_detecting_tests:
            for key, value in checked_coverage.items():
                try:
                    checked_covering_details = value[bug_detecting_test]
                    statement_covering_details = statement_coverage[key][bug_detecting_test]
                    print(key)
                    print("bs {} {}".format(bug_detecting_test, statement_covering_details))
                    print("bc {} {}".format(bug_detecting_test, checked_covering_details))
                except KeyError:
                    pass

        # counter = 1
        # for key, value in checked_coverage.items():
        #     print(key)
        #     for key2, value2 in value.items():
        #         print('\t {} - \ts-{} - {}'.format(key2, counter, statement_coverage[key][key2]))
        #         print('\t {} - \tc-{} - {} \n'.format(key2, counter, value2))
        #         counter = counter + 1


compute()
