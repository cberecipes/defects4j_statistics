import math
from itertools import chain


from scipy.stats import pointbiserialr
from util import read_config


project_config = read_config(['project_details.properties'])


def compute(data_dump):
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    project_list = project_config.get('projects', 'project_list').split(",")
    result = [['project', 'percent_coverage_s', 'statement_coverage', 'percent_coverage_c', 'checked_coverage']]
    correlation_csv = [['statement_correlation', 'checked_correlation']]
    scores_s_all = []
    scores_c_all = []
    is_bug_included_s_all = []
    is_bug_included_c_all = []

    s_r = 'NA'
    c_r = 'NA'
    for project in project_list:
        for d in data_dump:
            if d['project'] == project:
                scores_s = []
                scores_c = []
                is_bug_included_s = []
                is_bug_included_c = []
                for percent in percentage_range:
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
                max_iter = max(len(scores_s), len(is_bug_included_s), len(scores_c), len(is_bug_included_c))
                scores_s_all.append(scores_s)
                scores_c_all.append(scores_c)
                is_bug_included_s_all.append(is_bug_included_s)
                is_bug_included_c_all.append(is_bug_included_c)
                for i in range(0, max_iter):
                    result.append([project, get_value_for_csv(scores_s, i),
                                   get_value_for_csv(is_bug_included_s, i),
                                   get_value_for_csv(scores_c, i),
                                   get_value_for_csv(is_bug_included_c, i)])

    try:
        scores_s_all = list(chain(*scores_s_all))
        is_bug_included_s_all = list(chain(*is_bug_included_s_all))

        s_r = getattr(pointbiserialr(is_bug_included_s_all, scores_s_all), 'correlation')

        if math.isnan(s_r):
            if list(set(is_bug_included_s_all))[0]:
                s_r = 'All_True'
            else:
                s_r = 'All_False'
    except ValueError:
        pass

    try:
        scores_c_all = list(chain(*scores_c_all))
        is_bug_included_c_all = list(chain(*is_bug_included_c_all))

        c_r = getattr(pointbiserialr(is_bug_included_c_all, scores_c_all), 'correlation')
        if math.isnan(c_r):
            if list(set(is_bug_included_c_all))[0]:
                c_r = 'All_True'
            else:
                c_r = 'All_False'
    except ValueError:
        pass

    correlation_csv.append([s_r, c_r])
    final_result = {'for_csv': result, 'point_biserial_result': correlation_csv}
    return final_result


def get_value_for_csv(list_to_process, idx):
    try:
        return list_to_process[idx]
    except IndexError:
        return
