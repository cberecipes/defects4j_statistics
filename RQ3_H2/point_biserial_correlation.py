import math

from scipy.stats import pointbiserialr
from util import read_config


project_config = read_config(['project_details.properties'])


def compute(data_dump):
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    project_list = project_config.get('projects', 'project_list').split(",")
    result = [['project', 'percent_coverage', 'statement_coverage', 'checked_coverage']]
    for project in project_list:
        for d in data_dump:
            if d['project'] == project:
                for percent in percentage_range:
                    scores_s = []
                    scores_c = []
                    is_bug_included_s = []
                    is_bug_included_c = []
                    s_r = 'NA'
                    c_r = 'NA'
                    for tests in d['tests']:
                        for i_tests in tests['tests']:
                            if int(i_tests['percentage']) == int(percent):
                                for p_tests in i_tests['test_suites']:

                                    current_score = p_tests['statement_coverage']['score']
                                    if current_score > 0:
                                        scores_s.append(current_score)
                                        is_bug_included_s.append(
                                            p_tests['statement_coverage']['is_bug_detecting_test_included'])

                                    current_score = p_tests['checked_coverage']['score']
                                    if current_score > 0:
                                        scores_c.append(current_score)
                                        is_bug_included_c.append(
                                            p_tests['checked_coverage']['is_bug_detecting_test_included'])
                    try:
                        s_r = getattr(pointbiserialr(scores_s, is_bug_included_s), 'correlation')
                        if math.isnan(s_r):
                            if list(set(is_bug_included_s))[0]:
                                s_r = 'All_True'
                            else:
                                s_r = 'All_False'
                    except ValueError:
                        pass

                    try:
                        c_r = getattr(pointbiserialr(scores_c, is_bug_included_c), 'correlation')
                    except ValueError:
                        pass

                    result.append([project, percent, s_r, c_r])

    return result
