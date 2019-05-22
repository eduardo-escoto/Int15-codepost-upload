test = {   'name': 'q1',
    'points': 2,
    'suites': [   {   'cases': [   {   'code': '>>> '
                                               "all(election_sub['forecast_type'] "
                                               '== "classic")\n'
                                               'True',
                                       'hidden': False,
                                       'locked': False},
                                   {   'code': '>>> all((x == "2018-08-11") | '
                                               '(x == "2018-11-06") for x in '
                                               "election_sub['forecast_date'])\n"
                                               'True',
                                       'hidden': False,
                                       'locked': False}],
                      'scored': True,
                      'setup': '',
                      'teardown': '',
                      'type': 'doctest'}]}
