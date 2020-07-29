import math
import random
from itertools import chain

from scipy.stats import pointbiserialr
from util import read_config


project_config = read_config(['project_details.properties'])


def compute(data_dump):
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    project_list = project_config.get('projects', 'project_list').split(",")
    result = [['project', 'percent_coverage_s', 'statement_coverage', 'percent_coverage_c', 'checked_coverage']]
    correlation_csv = [['statement_correlation', 'checked_correlation']]

    scores_s_all = {}
    scores_c_all = {}
    f_s_all = []
    f_c_all = []
    s_r = 'NA'
    c_r = 'NA'
    for project in project_list:
        for d in data_dump:
            scores_s = []
            scores_c = []
            is_bug_included_s = []
            is_bug_included_c = []
            if d['project'] == project:
                for percent in percentage_range:
                    s_r = 'NA'
                    c_r = 'NA'
                    for tests in d['tests']:
                        for i_tests in tests['tests']:
                            if int(i_tests['percentage']) == int(percent):
                                for p_tests in i_tests['test_suites']:
                                    try:
                                        current_score = p_tests['statement_coverage']['t_score']
                                        if current_score > 0:
                                            scores_s.append(current_score)
                                            is_bug_included_s.append(
                                                p_tests['statement_coverage']['is_bug_detecting_test_included'])

                                        current_score = p_tests['checked_coverage']['t_score']
                                        if current_score > 0:
                                            scores_c.append(current_score)
                                            is_bug_included_c.append(
                                                p_tests['checked_coverage']['is_bug_detecting_test_included'])
                                    except KeyError:
                                        pass

                if len(scores_c) > 0:
                    try:
                        scores_c_all[str(percent)] = scores_c_all[str(percent)] + \
                                                     list(zip(scores_c, is_bug_included_c))
                    except KeyError:
                        scores_c_all[str(percent)] = list(zip(scores_c, is_bug_included_c))

                    try:
                        scores_s_all[str(percent)] = scores_s_all[str(percent)] + \
                                                     list(zip(scores_s, is_bug_included_s))
                    except KeyError:
                        scores_s_all[str(percent)] = list(zip(scores_s, is_bug_included_s))

    select_items = min([len(scores_c_all[idx]) for idx in scores_c_all])

    for idx in scores_c_all:
        random.shuffle(scores_c_all[idx])
        f_c_all.append(scores_c_all[idx][:select_items])

    for idx in scores_s_all:
        random.shuffle(scores_s_all[idx])
        f_s_all.append(scores_s_all[idx][:select_items])

    r_scores_s = list(list(zip(*list(chain(*f_s_all))))[0])
    r_is_bug_included_s = list(list(zip(*list(chain(*f_s_all))))[1])

    r_scores_c = list(list(zip(*list(chain(*f_c_all))))[0])
    r_is_bug_included_c = list(list(zip(*list(chain(*f_c_all))))[1])

    for _ in range(0, len(r_scores_c)):
        result.append(['project', r_scores_s[_], r_is_bug_included_s[_], r_scores_c[_], r_is_bug_included_c[_]])

    try:
        print(r_is_bug_included_s, r_scores_s)
        s_r = getattr(pointbiserialr(r_is_bug_included_s, r_scores_s), 'correlation')

        if math.isnan(s_r):
            if list(set(r_is_bug_included_s))[0]:
                s_r = 'All_True'
            else:
                s_r = 'All_False'
    except ValueError:
        pass

    try:
        print(r_is_bug_included_c, r_scores_c)
        c_r = getattr(pointbiserialr(r_is_bug_included_c, r_scores_c), 'correlation')
        if math.isnan(c_r):
            if list(set(r_is_bug_included_c))[0]:
                c_r = 'All_True'
            else:
                c_r = 'All_False'
    except ValueError:
        pass

    correlation_csv.append([s_r, c_r])

    final_result = {'for_csv': result, 'point_biserial_result': correlation_csv}
    return final_result


def compute_test():
    r_is_bug_included_c = [5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 30, 30, 35, 35, 40, 40, 45, 45, 50, 50, 55, 55, 60, 60, 65, 65, 70, 70, 75, 75, 80, 80, 85, 85, 90, 90, 95, 95, 100, 100]
    r_scores_c = [False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, True, False, True, False, False, True, False, False, True, True, True, True, False, True, False, False, True, False, True, True, True, True, True, True]
    c_r = getattr(pointbiserialr(r_is_bug_included_c, r_scores_c), 'correlation')
    print(c_r)


compute_test()
