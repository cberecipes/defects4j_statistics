import random

from scipy.stats import pointbiserialr
from util import read_config, remove_exponent


project_config = read_config(['project_details.properties'])


def maximum(a, b):
    if a >= b:
        return a
    else:
        return b


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


def return_list_element_if_exist(the_list, i):
    try:
        return the_list[i]
    except IndexError:
        return None


def compute(data_dump):
    result = [['project', 'percent_coverage_s', 'statement_coverage', 'percent_coverage_c', 'checked_coverage']]
    correlation_csv = [['statement_correlation', 'checked_correlation']]
    bug_detecting_included_c = []
    bug_detecting_included_s = []
    percentage_c = []
    percentage_s = []
    scores_to_process_c = {}
    scores_to_process_s = {}

    for generated_test_suite in data_dump[0]['tests']:
        for project_wise_tests in generated_test_suite['tests']:
            for both_tests in project_wise_tests['test_suites']:

                try:
                    s_is_bug_detecting_included = both_tests['statement_coverage']['is_bug_detecting_test_included']
                    try:
                        scores_to_process_s[project_wise_tests['percentage']].append(s_is_bug_detecting_included)
                    except KeyError:
                        scores_to_process_s[project_wise_tests['percentage']] = [s_is_bug_detecting_included]
                except KeyError:
                    pass

                try:
                    c_is_bug_detecting_included = both_tests['checked_coverage']['is_bug_detecting_test_included']
                    try:
                        scores_to_process_c[project_wise_tests['percentage']].append(c_is_bug_detecting_included)
                    except KeyError:
                        scores_to_process_c[project_wise_tests['percentage']] = [c_is_bug_detecting_included]
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

    pbsr_statement = pointbiserialr(percentage_s, bug_detecting_included_s)
    pbsr_checked = pointbiserialr(percentage_c, bug_detecting_included_c)

    s_r = remove_exponent(getattr(pbsr_statement, 'correlation'))
    sp_value = remove_exponent(getattr(pbsr_statement, 'pvalue'))

    c_r = remove_exponent(getattr(pbsr_checked, 'correlation'))
    cp_value = remove_exponent(getattr(pbsr_checked, 'pvalue'))

    # create data for CSV
    for idx in range(maximum(len(percentage_c), len(percentage_s))):
        tmp_result = ['project',
                      return_list_element_if_exist(percentage_s, idx),
                      return_list_element_if_exist(bug_detecting_included_s, idx),
                      return_list_element_if_exist(percentage_c, idx),
                      return_list_element_if_exist(bug_detecting_included_c, idx)]
        result.append(tmp_result)

    correlation_csv.append([s_r, sp_value, c_r, cp_value])

    return {'for_csv': result, 'point_biserial_result': correlation_csv}
