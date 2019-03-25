# ucsb-codePost-upload
Script for ucsb int 5 upload

## Process:
### One time -- done for all students:
0. `pip3 install codePost` in local environment. Also install `python3` if needed.
1. Add your API-key to a local version of ```preprocess-add-grade.py```. Your API key can be found at www.codepost.io/settings. This key is unique to you and can be reset at any time.  
    * Make sure that the `course_name` and `course_period` variables are the same as your course in codePost.
2. After students have submitted, run ```python3 preprocess-add-grade.py <input_dir> <output_dir> <codePost assignment name>```
    This will:
      * Add in codePost test upload code to the final cell in the ```output_dir``` files.
      * Upload the ```input_dir``` files to codePost. ```input_dir``` files must be named `<student_email>_<assignment_name>.ipynb`. If this changes, change the code appropriately. 
3. Upload `output_dir` to the JupyterHub grader repository (same as current process).
4. `pip3 install codePost` in JupyerHub grader environment,
5. Set env variable in JupyterHub ```cp_api_key="API_KEY"``` using the same API key from step 0 above. This can be done by either:  
    * Open up JupyerHub terminal environment and `export cp_api_key=<API_KEY>`.
    * Create a Jupyer notebook in directory and run `%env cp_api_key=<API_KEY>`.
    * **Make sure that this variable is not accessible from the student directory on JupyterHub.** Anyone with access to your API key can access and modify all course data, so you should restrict access to it. If you suspect your API key has been compromised, you can reset it (and invalidate the old one) at www.codepost.io/settings. 
6. Modify `parse_test_output` and `add_comments` functions in `upload_tests.py` to your desired behavior:
    * `parse_test_output` defines what amount of test output is uploaded to codePost and exposed to students. By default it returns the full test output.
    *  `add_comments` defines when to programatically add comments based on the test output. This depends on how you choose to score tests. 
7. Upload the ```upload_tests.py``` file in the jupyerhub grader folder.
    * Make sure that the `course_name` and `course_period` variables are the same as your course in codePost.

### During Grading:
When each student's file is being graded:
1. Ensure that the final cell has the following lines of code. It should already be included from the pre-processing. If you rename `test_output` to a different variable, make sure you rename the variable used in `upload_tests.py`. They share the same namespace.
```
import os
test_output = [ok.grade(q[:-3]) for q in os.listdir('tests') if q.startswith('q')]
%run -i ../upload_tests.py <student_email> <assignment_name>
```
2. Run the final cell, which will run the ```upload_tests.py``` script, pushing the test output to codePost.
3. Visit the URL printed out in the notebook to navigate to the uploaded submission. Assign yourself as the grader, add additional feedback, and click 'Finalize'.
  
============================================================================

## Explanation of changes:
### preprocess-add-grade.py
1. Changing `grade_calc` to `get_grade_snippet()`  
`get_grade_snippet` adds three lines to the final cell of a student's notebook to:  
  
   * Store the autograder output into a variable ```test_output```.
   * Run the ```upload_tests.py``` script from the JupyterHub directory . 
    
   In order to call get_grade_snippet, we need the `student_email`. This is captured as `student_email=file.split('_')[0]`, assuming file naming convention of `<student_email>_<assignment_name>.ipynb`.

2. Upload `input_dir` (the submitted student notebooks) to codePost.
  
   * The correct assignment object is retrieved via ```codePost.get_assignment_info_by_name```.
   * ```upload_notebooks(<input_dir>, assignment)``` bulk uploads all of the `input_dir` files to codePost. Once again, the file naming convention of ```<student_email>_<assignment_name>.ipynb``` is assumed. 

### upload_tests.py
This python script is run in each students' jupyter notebook upon grading. It contains three functions:
1. ```parse_test_output(test_output)``` 

Returns the test output content to be uploaded to codePost. **YOU SHOULD MODIFY THIS FUNCTION TO SPECIFY YOUR DESIRED BEHAVIOR.** For example, if we wanted to expose the full test_output to students, this function would read:
```
def parse_test_output(test_output):
  return test_output
```
  
  
2. ```add_comments(api_key, test_output, file)```  

Adds comments to a file after the file has been uploaded to codePost. **YOU SHOULD MODIFY THIS FUNCTION TO SPECIFY YOUR DESIRED BEHAVIOR.** For example, if we wanted to add a single comment to the top of the file, saying "Good Job! You get an extra point!" with a point value of +1, this function would read:
```
def add_comments(api_key, test_output, file):
  codePost.post_comment(api_key, file, "Good Job! You get an extra point!", -1, 0, 1, 0, 0)
```
The syntax of post_comment is ```post_comment(api_key, file, text, pointDelta, startChar, endChar, startLine, endLine, rubricComment=None)```, where pointDelta defaults to negative. For example, a pointDelta of 1 means that the comment will be associated with -1 on codePost.
  
  
3. ```upload_test_output(api_key, course_name, course_period, student_email, assignment_name, test_output)``` 

This is the main function, which:
* (a) Given a ```course_name```, ```course_period```, ```assignment_name```, and ```student_email```, finds the student's submission.
* (b) Posts a new file ```new_file``` to that student's submission with the contents of ```parse_test_output(test_output)```.
* (c) Calls ```add_comments(api_key, test_output, new_file``` to add comments to ```new_file```.


### A few notes on ```upload_tests.py```
  * Assumed that the student is a valid student in the course. If the student has not been added on codePost to the course,  this will not work. 
  * Assumed that an assignment with name of `assignment_name` has been added to codePost for the course of ```course_name | course_period```. If no such assignment exists, this will not work.
  * The name of the file once uploaded is defined at the top of ```upload_tests.py``` as ```test_output_file_name```. If another file exists for a submission of the same name, then the upload will not work. File names must be unique for a given submission. 
