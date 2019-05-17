# CodePost Upload

## To use:
0. Create Assignment in CodePost. The name of this assignment is assignment_name
    - In this example, create an assignment named: `hw01` on codepost.

1. Have Input directory structured as:
    - input_dir/
        - tests/
            - test files
        - \[assignment_name\].ok
        - python notebook files with naming structure: \[student_email\]_\[assignment_name\].ipynb
    - An example is contained in this repository named `input_dir`

2. Ensure that necessary packages that are used as part of the course (i.e., in the hw and labs) are installed in python environment (on the computer that's running the grading)
    - run `pip install requirements.txt` in order to make sure all packages are in current environment

3. Run `sh runGrading.sh input_dir output_dir assignment_name `
    - For example, to run the assignments in this repo run: `sh runGrading.sh input_dir output_dir hw01`
[TODO]: run the script to capture its output into a log file, so that after the script is finished, we can search through the log to see if any noteboks have failed.

4. Done! 🎊🎉 

## What runGrading.sh does

This works by first pre-processing all of the notebook files in `[input_dir]` and stores them in the `[output_dir]`.
_This step happens on the grader's computer (make sure `requirements.txt` mentioned above is up-to-date)._

### Pre-processing

For every original student notebook in the `[input_dir]`:
1. Uploads the original notebook to codepost
2. Commenting (or deleting) any lines that have `ok.submit()` to prevent resubmissions
3. Appends a cell that runs the autograding script
4. Saves the preprocessed notebooks into `[output_dir]`

Then the autograding and uploading runs on the notebooks in `[output_dir]`

### Autograding

1. Executes the notebook, and its autograding cell (in the `getUploadTestSnippet` from the `preprocess-add-grade.py`)
2. Parses the test output (using `parse_test_output` and `test_output` in the `getUploadTestSnippet`).
3. [TODO]: should happen in `parse_test_output` but currently it just returns the output produced by the notebook, which gets saved in `output.txt` **on Codepost** (via the `upload_test_output()`)
    3.1 Adds comments (via `add_comments()` that looks for the "k..." string and adds `comment_text` that will be sent back to codepost via its API); 
    3.2 should also deduct points for failed tests.

After all the previous steps are finished, all that is left is managing the assignments from CodePost (e.g., grading manually conceptual questions and releasing the grades)

### Finalizing

1. Manually finalize each submission, while also grading conceptual questions

### Done! 🎊🎉 




## Troubleshooting

* If a notebook fails during the execution, that notebook's processing is terminated and the script moves to the next notebook.
