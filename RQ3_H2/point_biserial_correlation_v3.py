import math
import random
from itertools import chain

from scipy.stats import pointbiserialr
from util import read_config


project_config = read_config(['project_details.properties'])


def resize_lists(list_to_trim):
    max_key_size = max(list_to_trim, key=int)
    max_resize_size = len(list_to_trim.__getitem__(max_key_size))

    for list_key in list_to_trim:
        shuffle_and_trim(list_to_trim.__getitem__(list_key), max_resize_size)


def shuffle_and_trim(list_to_shuffle, reduce_size):
    random.shuffle(list_to_shuffle)
    current_size = len(list_to_shuffle)
    to_size = current_size - reduce_size
    del list_to_shuffle[:to_size]


def compute(data_dump):
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    project_list = project_config.get('projects', 'project_list').split(",")
    result = [['project', 'percent_coverage_s', 'statement_coverage', 'percent_coverage_c', 'checked_coverage']]
    correlation_csv = [['statement_correlation', 'checked_correlation']]

    bug_detecting_included_c = []
    bug_detecting_included_s = []

    percentage_c = []
    percentage_s = []

    scores_to_process_c = {}
    scores_to_process_s = {}

    # for all_tests in data_dump[0]['tests']:
    #     print(all_tests)

    for all_tests in data_dump[0]['tests']:
        for project_tests in all_tests['tests']:
            for both_tests in project_tests['test_suites']:

                try:
                    s_is_bug_detecting_included = both_tests['statement_coverage']['is_bug_detecting_test_included']
                    c_is_bug_detecting_included = both_tests['checked_coverage']['is_bug_detecting_test_included']
                    # print(project_tests['percentage'])
                    # print(s_is_bug_detecting_included)
                    # print(c_is_bug_detecting_included)

                    try:
                        scores_to_process_c[project_tests['percentage']].append(c_is_bug_detecting_included)
                    except KeyError:
                        scores_to_process_c[project_tests['percentage']] = [c_is_bug_detecting_included]

                    try:
                        scores_to_process_s[project_tests['percentage']].append(s_is_bug_detecting_included)
                    except KeyError:
                        scores_to_process_s[project_tests['percentage']] = [s_is_bug_detecting_included]

                except KeyError:
                    pass

    # resize_lists(scores_to_process_s)
    # resize_lists(scores_to_process_c)

    for key in scores_to_process_s:
        for val in scores_to_process_s[key]:
            percentage_s.append(key)
            bug_detecting_included_s.append(val)

    for key in scores_to_process_c:
        for val in scores_to_process_c[key]:
            percentage_c.append(key)
            bug_detecting_included_c.append(val)

    print(percentage_s)
    print(bug_detecting_included_s)

    print(percentage_c)
    print(bug_detecting_included_c)

    s_r = getattr(pointbiserialr(percentage_s, bug_detecting_included_s), 'correlation')
    c_r = getattr(pointbiserialr(percentage_c, bug_detecting_included_c), 'correlation')

    print("statement correlation" + str(s_r))
    print("checked correlation" + str(c_r))

    # create data for CSV

    for idx, itm in enumerate(percentage_c):
        tmp_result = ['project', percentage_s[idx], bug_detecting_included_s[idx], percentage_c[idx],
                      bug_detecting_included_c[idx]]
        result.append(tmp_result)

    correlation_csv.append([s_r, c_r])

    return {'for_csv': result, 'point_biserial_result': correlation_csv}
