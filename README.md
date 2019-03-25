# ucsb-codepost-upload
Script for ucsb int 5 upload

Process:
## One time -- done for all students:
1) Set env variable in JupyterHub cp_api_key="API_KEY". API key can be found on www.codepost.io/settings
2) Put the upload_tests.py file in the jupyerhub grader repository
  - Make sure that the course and course_period variables are appropriately set in the file
3) Locally, add API-key to testing.py, and make sure course and course_period variables are correct
4) Run
```
testing.py <input_dir> <output_dir> <codePost assignment name>
```
  - This will (1) add in the test_output code to the output_dir files (2) upload the input_dir files to codePost
  - For (2) to happen, input_dir files must be named <student_email>_<assignment_name>.ipynb. If this changes, change the code appropriately. 

## During Grading:
When each student's file is being graded:
1) Ensure that the final cell has the following format. It should already be included from the pre-processing.
```
import os
<variable_name> = [ok.grade(q[:-3]) for q in os.listdir('tests') if q.startswith('q')]
%run upload_tests.py <student_email> <assignment_name> <variable_name>
```
2) Run the final cell, which will run the upload_tests.py script, pushing the test output to codePost

Explanation of additions:
1) Modifying grade_calc to get_grade_snippet(student_email, assignment_name)
def get_grade_snippet(student_email, assignment_name):
```
  return '''"import os\\n",
    "test_output = [ok.grade(q[:-3]) for q in os.listdir('tests') if q.startswith('q')]\\n",
    "%run upload_tests.py {student_email} {assignment_name} test_output"'''.format(student_email=student_email, assignment_name=assignment_name)
```


