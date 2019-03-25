# ucsb-codepost-upload
Script for ucsb int 5 upload

## Process:
### One time -- done for all students:
1. Set env variable in JupyterHub ```cp_api_key="API_KEY"```. Your API key can be found on www.codepost.io/settings. 
2. Add your API-key to a local version of ```preprocess-add-grade.py``` (or alternative key entry method)
    * Make sure that the `course_name` and `course_period` variables are the same as your course in codePost
3. After students have submitted, run ```preprocess-add-grade.py <input_dir> <output_dir> <codePost assignment name>```
    * This will (1) add in test upload code to the ```output_dir``` files (2) upload the ```input_dir``` files to codePost
    * For (2) to happen, ```input_dir``` files must be named ```<student_email>_<assignment_name>.ipynb```. If this changes, change the code appropriately. 
4. Upload `output_dir` to the JupyterHub grader repository (same as current process)
5. Modify `parse_test_output` and `add_comments` functions in `upload_tests.py` to your desired behavior:
    * `parse_test_output` defines what amount of test output is uploaded to codePost and exposed to students. By default it returns the full test output.
    *  `add_comments` defines when to programatically add comments based on the test output. This depends on how you choose to score tests. 
6. Put the ```upload_tests.py``` file in the jupyerhub grader folder
    * Make sure that the `course_name` and `course_period` variables are the same as your course in codePost

### During Grading:
When each student's file is being graded:
1. Ensure that the final cell has the following lines of code. It should already be included from the pre-processing.
```
import os
<variable_name> = [ok.grade(q[:-3]) for q in os.listdir('tests') if q.startswith('q')]
%run upload_tests.py <student_email> <assignment_name> <variable_name>
```
2. Run the final cell, which will run the ```upload_tests.py``` script, pushing the test output to codePost . 
  
============================================================================

## Explanation of changes:
### preprocess-add-grade.py
1. Changing `grade_calc` to `get_grade_snippet()`  
`get_grade_snippet` adds three lines to the final cell of a student's notebook to:  
  
   * Store the autograder output into a variable ```test_output```  
   * Run the ```upload_tests.py``` script from the JupyterHub directory . 
    
   In order to call get_grade_snippet, we need the `student_email`. This is captured as `student_email=file.split('_')[0]`, assuming a file naming convention of `<student_email>_<assignment_name>.ipynb`

2. Uploading the files in input_dir (the original student notebooks) to codePost, independent of flattening  
  
   * The correct assignment object from codePost is retrieved via ```codePost.get_assignment_info_by_name```
   * ```upload_notebooks(<input_dir>, assignment)``` is called to bulk upload all of the input_dir files to codePost. Once again, the file naming convention of ```<student_email>_<assignment_name>.ipynb``` is assumed. 

### upload_tests.py
This python script is run in each students' jupyter notebook upon grading. It contains three functions:
1. ```parse_test_output(test_output)``` 

This function returns the test output content to be uploaded to codePost. **THIS FUNCTION SHOULD BE MODIFIED BY USER FOR DESIRED BEHAVIOR.** For example, if we wanted to expose the full test_output to students, this function would read:
```
def parse_test_output(test_output):
  return test_output
```
  
  
2. ```add_comments(api_key, test_output, file)```  

This function adds comments to a file after the file has been uploaded to codePost. **THIS FUNCTION SHOULD BE MODIFIED BY USER FOR DESIRED BEHAVIOR.** For example, if we wanted to add a single comment to the top of the file, saying "Good Job! You get an extra point!" with a point value of +1, this function would read:
```
def add_comments(api_key, test_output, file):
  codePost.post_comment(api_key, file, "Good Job! You get an extra point!", -1, 0, 1, 0, 0)
```
The syntax of post_comment is ```post_comment(api_key, file, text, pointDelta, startChar, endChar, startLine, endLine, rubricComment=None)```, where pointDelta defaults to negative. For example, a pointDelta of 1 means that the comment will be associated with -1 on codePost.
  
  
3. ```upload_test_output(api_key, course_name, course_period, student_email, assn_name, test_output)``` 

This is the main function, which:
  a. Given a ```course_name```, ```course_period```, ```assn_name```, and ```student_email```, finds the student's submission
  b. Posts a new file ```new_file``` to that student's submission with the conttents of ```parse_test_output(test_output)```
  c. Calls ```add_comments(api_key, test_output, new_file``` to add comments to ```new_file```


### A few notes on ```upload_tests.py```
  * Assumed that the student is a valid student in the course. If the student has not been added on codePost to the course then this will not work. 
  * Assumed that an assignment with name of assn_name has been added to codePost for the course of ```course_name | course_period```. If an assignment doesn't exist, this will not work.
  * The name of the file once uploaded is defined at the top of ```upload_tests.py``` as ```test_output_file_name```. If another file exists for a submission of the same name, then the upload will not work. File names must be unique for a submission. 
