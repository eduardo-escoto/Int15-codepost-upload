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

2. Ensure that necessary packages are installed in python environment
    - run `pip install requirements.txt` in order to make sure all packages are in current environment

3. Run `sh runGrading.sh input_dir output_dir assignment_name `
    - For example, to run the assignments in this repo run: `sh runGrading.sh input_dir output_dir hw01`

4. Done! 🎊🎉 

## Process

This works by first processing all of the notebook files by:

1. Commenting (or deleting) any lines that have `ok.submit()` to prevent resubmissions
2. Appends a cell that runs the autograding script which then uploads it to codepost
3. Executes the notebook, and the autograding cell
4. Parses the test output and adds comments and deducts points for failed tests.
5. Done! 🎊🎉 