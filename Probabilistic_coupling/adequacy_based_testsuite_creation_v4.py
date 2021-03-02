import random
from os import path
from datetime import datetime

# from pyaml import print
from Probabilistic_coupling.tests.class_details import print_class_details
from util import read_config
from utils import utils
from statistics import mean
import statistics
import pandas as pd

from utils.test_analyser import find_test_nature, determine_test_nature
from utils.utils import a_intersection_b, len_a_intersection_b

results_folder_path = 'Probabilistic_coupling/results/'
project_config = read_config(['project_details.properties'])
random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
file_path = results_folder_path + '/point_biserial_correlation__'
static_correlation_path = results_folder_path + '/correlation_final_lang.txt'
aggregated_csv = [['project_id', 'adequacy_based_tests_statement', 'adequacy_based_tests_checked']]


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        for_each_project(project)


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        print("running for {}, with bug-id {}".format(project_name, project_id))
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(is_project_path_exist):
            statement_as_rows = dict()
            checked_stmt_as_rows = dict()
            low_checked_coverage = 0
            # for i in range(0, int(test_suite_size)):
            exception_trace_path = defects4j_project_path + "/" + project_name + "/trigger_tests/" + str(project_id)
            patch_path = defects4j_project_path + "/" + project_name + "/" + "/patches/" + \
                         str(project_id) + ".src.patch"
            current_project_path = defects4j_project_path + "/" + project_name
            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            coverable_lines = utils.get_coverable_lines(project_id, current_project_path, modified_classes)
            dict_of_modified_coverable_lines = dict()
            try:
                dict_of_modified_coverable_lines = utils.get_modified_coverable_lines(patch_path, coverable_lines)
            except Exception:
                pass
            stmt_modified_coverable_lines = []
            checked_modified_coverable_lines = []
            current_project_path = defects4j_project_path + "/" + project_name
            list_of_bug_detecting_tests = utils.get_bug_detecting_tests(project_id, current_project_path)
            bug_detecting_test_natures = find_test_nature(exception_trace_path, list_of_bug_detecting_tests)
            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            projects_statement_coverage = utils.get_statement_coverage(project_id, current_project_path
                                                                       , modified_classes)
            projects_checked_coverage = utils.get_checked_coverage(project_id, current_project_path,
                                                                   modified_classes)
            # print("list_of_bug_detecting_tests: " + ",".join(list_of_bug_detecting_tests))

            # take coverable lines
            for stmt in coverable_lines:
                try:
                    for stmt_line_no in coverable_lines[stmt]['statement_coverable_lines']:
                        stmt_modified_coverable_lines.append(stmt + "." + str(stmt_line_no))
                    for stmt_line_no in coverable_lines[stmt]['checked_coverable_lines']:
                        checked_modified_coverable_lines.append(stmt + "." + str(stmt_line_no))
                except TypeError:
                    pass

            for stmt_coverable_statements in stmt_modified_coverable_lines:
                statement_as_rows[stmt_coverable_statements] = []

            for checked_coverable_statements in checked_modified_coverable_lines:
                checked_stmt_as_rows[checked_coverable_statements] = []

            for stmt_covered_classes in projects_statement_coverage:
                for a_test in projects_statement_coverage[stmt_covered_classes]:
                    for statements in projects_statement_coverage[stmt_covered_classes][a_test]:
                        try:
                            statement_as_rows[stmt_covered_classes + "." + str(statements)].append(a_test)
                        except KeyError:
                            # print("bug detecting test does not cover this statement - statement coverage")
                            pass

            for checked_covered_classes in projects_checked_coverage:
                for a_test in projects_checked_coverage[checked_covered_classes]:
                    for statements in projects_checked_coverage[checked_covered_classes][a_test]:
                        try:
                            checked_stmt_as_rows[checked_covered_classes + "." + str(statements)].append(a_test)
                        except KeyError:
                            # print("bug detecting test does not cover this statement - checked coverage")
                            pass

            # print(dict_of_modified_coverable_lines)
            result_checked = {}
            # result_statement = {}

            # for statements in statement_as_rows:
            #     if statements in stmt_modified_coverable_lines:
            #         result_statement[statements] = divide(len(list_of_bug_detecting_tests),
            #                                               len(statement_as_rows[statements])) + ", " + \
            #                                        str(len(list_of_bug_detecting_tests)) + "/" + \
            #                                        str(len(statement_as_rows[statements]))

            for statements in checked_stmt_as_rows:
                if float(divide(len(a_intersection_b(list_of_bug_detecting_tests, checked_stmt_as_rows[statements])),
                                len(checked_stmt_as_rows[statements]))) > 0 and \
                        float(divide(len(a_intersection_b(list_of_bug_detecting_tests, statement_as_rows[statements])),
                                     len(statement_as_rows[statements]))) > 0:
                    result_checked[statements] = ".".join(statements.split(".")[:-1]) + \
                                                 ", {}-{}".format(project_name, project_id) + "," + \
                                                 divide(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                             checked_stmt_as_rows[statements])),
                                                        len(checked_stmt_as_rows[statements])) + "," + \
                                                 divide(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                             statement_as_rows[statements])),
                                                        len(statement_as_rows[statements])) + "," + \
                                                 str(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                          checked_stmt_as_rows[statements]))) + "/" + \
                                                 str(len(checked_stmt_as_rows[statements])) + "," + \
                                                 str(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                          statement_as_rows[statements]))) + "/" + \
                                                 str(len(statement_as_rows[statements])) + "," + \
                                                 determine_test_nature(bug_detecting_test_natures,
                                                                       a_intersection_b(
                                                                           list_of_bug_detecting_tests,
                                                                           checked_stmt_as_rows[statements])) + "," + \
                                                 determine_test_nature(bug_detecting_test_natures,
                                                                       a_intersection_b(
                                                                           list_of_bug_detecting_tests,
                                                                           statement_as_rows[statements])) + "," + \
                                                 is_this_statement_modified(dict_of_modified_coverable_lines,
                                                                            statements,
                                                                            "checked_coverable_lines") + "," + \
                                                 is_this_statement_modified(dict_of_modified_coverable_lines,
                                                                            statements,
                                                                            "statement_coverable_lines")

                     # print(".".join(statements.split(".")[:-1]) +
                    #       ", {}-{}".format(project_name, project_id) + ", " +
                    #       divide(len(a_intersection_b(list_of_bug_detecting_tests,
                    #                                   checked_stmt_as_rows[statements])),
                    #              len(checked_stmt_as_rows[statements])) + ", " +
                    #       divide(len(a_intersection_b(list_of_bug_detecting_tests,
                    #                                   statement_as_rows[statements])),
                    #              len(statement_as_rows[statements])) + ", " +
                    #       str(len(a_intersection_b(list_of_bug_detecting_tests,
                    #                                checked_stmt_as_rows[statements]))) + "/" +
                    #       str(len(checked_stmt_as_rows[statements])) + ", " +
                    #       str(len(a_intersection_b(list_of_bug_detecting_tests,
                    #                                statement_as_rows[statements]))) + "/" +
                    #       str(len(statement_as_rows[statements])) + "-> " +
                    #       "[" + ", ".join(statement_as_rows[statements]) + "] [" +
                    #       ", ".join(checked_stmt_as_rows[statements]) + "] [" +
                    #       ", ".join(list_of_bug_detecting_tests) + "]"
                    #       )
                    if statements in checked_modified_coverable_lines:
                        pass
                else:
                    low_checked_coverage = low_checked_coverage + 1

            # utils.write_list_as_csv([["target", "statement coverage probabilistic coupling",
            #                           "len(bug detecting tests)/len(covering tests)",
            #                           "checked coverage probabilistic coupling",
            #                           "len(bug detecting tests)/len(covering tests)"]],
            #                         "{}/prob_coupling_{}_{}_{}.csv"
            #                         .format(results_folder_path, "statement", project_name, project_id))
            # utils.write_dict_as_csv(result_statement, "{}/prob_coupling_{}_{}_{}.csv"
            #                         .format(results_folder_path, "statement", project_name, project_id))
            print("low_checked_coverage: " + str(low_checked_coverage))
            if len(result_checked) > 0:
                utils.write_list_as_csv([["target",
                                          "class_name",
                                          "Proj-id",
                                          "checked_pc",
                                          "statement_pc",
                                          "len(bug_detecting_tests)/len(covering_tests)",
                                          "len(bug_detecting_tests)/len(covering_tests)",
                                          "checked_nature",
                                          "statement_nature",
                                          "checked_modified",
                                          "statement_modified"]],
                                        "{}/prob_coupling_{}_{}.csv"
                                        .format(results_folder_path, project_name, project_id))

                utils.write_dict_as_csv(result_checked, "{}/prob_coupling_{}_{}.csv"
                                        .format(results_folder_path, project_name, project_id))


def divide(a, b):
    try:
        # return str(a / b)
        return str(1) if a / b > 1 else str(a / b)
    except ZeroDivisionError:
        return str(0)


def is_this_statement_modified(dict_of_modified_coverable_lines, statement, type_of_coverage):
    splitted = statement.split(".")
    class_name = ".".join(splitted[:-1])
    line_nr = splitted[-1]
    try:
        result_list = dict_of_modified_coverable_lines[class_name][type_of_coverage]

        if len_a_intersection_b(result_list, [int(line_nr)]) > 0:
            return "x"
        else:
            return "."
    except Exception:
        return ""
