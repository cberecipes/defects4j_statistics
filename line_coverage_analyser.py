import json

from util import read_config
from utils import utils

project_config = read_config(['project_details.properties'])


def list_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def iterate_all_print():
    project_name = "JacksonDatabind"
    defects4j_project_path = "/home/pepper/Dropbox/Documents/Study/Masters/thesis/projects/defects4j/framework/projects"
    current_project_path = defects4j_project_path + "/" + project_name

    file_path = current_project_path + "/trace_files/10f/" + "line_coverage_new.json"
    statement_coverage = utils.read_json_file(file_path)
    for classes in statement_coverage:
        print("{} ->".format(classes))
        # for tests in statement_coverage[classes]:
        #     print("{} -> {}".format(tests, statement_coverage[classes][tests]))


def print_given():
    project_name = "JacksonDatabind"
    defects4j_project_path = "/home/pepper/Dropbox/Documents/Study/Masters/thesis/projects/defects4j/framework/projects"
    current_project_path = defects4j_project_path + "/" + project_name
    given_class = "com.fasterxml.jackson.databind.AnnotationIntrospector"
    given_test = "com.fasterxml.jackson.databind.TestFormatSchema::testFormatForGenerators"
    file_path_new = current_project_path + "/trace_files/10f/" + "line_coverage_new.json"
    file_path = current_project_path + "/trace_files/10f/" + "line_coverage.json"
    statement_coverage = utils.read_json_file(file_path)
    statement_coverage_new = utils.read_json_file(file_path_new)

    # for tests in statement_coverage_new[given_class]:
    #     print(tests)
    stop_at = 5
    counter = 0
    print_from = 5
    for classes in statement_coverage:
        counter = counter + 1
        if counter >= print_from:
            print("{} -> {}".format(classes, ""))
            for tests in statement_coverage[classes]:
                try:
                    statement_coverage_new[classes][tests]
                    # print("{}{} -> {}".format("\t", tests, statement_coverage[classes][tests]))
                    # print("{}{} -> {}".format("\t", tests, statement_coverage_new[classes][tests]))
                except KeyError:
                    print(tests)
        if counter >= stop_at:
            break


def class_diff_identifier():
    project_name = "JacksonDatabind"
    defects4j_project_path = "/home/pepper/Dropbox/Documents/Study/Masters/thesis/projects/defects4j/framework/projects"
    current_project_path = defects4j_project_path + "/" + project_name
    given_class = "com.fasterxml.jackson.databind.AnnotationIntrospector"
    given_test = "com.fasterxml.jackson.databind.TestFormatSchema::testFormatForGenerators"
    file_path_new = current_project_path + "/trace_files/10f/" + "line_coverage_new.json"
    file_path = current_project_path + "/trace_files/10f/" + "line_coverage.json"
    statement_coverage = utils.read_json_file(file_path)
    statement_coverage_new = utils.read_json_file(file_path_new)

    statement_tests = []
    statement_new_tests = []

    for classes in statement_coverage:
        statement_tests.append(classes)

    for classes in statement_coverage_new:
        statement_new_tests.append(classes)

    print(statement_tests)
    print(len(statement_new_tests))
    print(len(statement_tests))
    print(list_diff(statement_new_tests, statement_tests))


class_diff_identifier()

# com.fasterxml.jackson.databind.DeserializationConfig