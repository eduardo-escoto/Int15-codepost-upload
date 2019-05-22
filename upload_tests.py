import json
import requests as _requests
import sys as _sys
import os
import sys
import requests
# install by 'pip install codePost'. Documentation can be found at https://github.com/codepost-io/codePost-python
import codePost_api as codePost

# set API key via %env cp_api_key = <API KEY>
# api_key = os.environ["cp_api_key"]
course_name = 'New course'
course_period = '2019'

# NOTE: THIS SHOULD BE EDITED BY USER BASED ON DESIRED BEHAVIOR. File name for codePost
test_output_file_name = "Output.txt"


api_key = "c0f0e3594c99b2e58a46cf3fc97538385c28eae0"

try:
    # Python 2
    from urllib import quote as _urlquote
    from urllib import urlencode as _urlencode
except ImportError:
    # Python 3
    from urllib.parse import quote as _urlquote
    from urllib.parse import urlencode as _urlencode

try:
    # Python 3
    from enum import Enum as _Enum
except ImportError:
    no_enum = True

    # Python 2 fallbacks
    try:
        from enum import Enum as _Enum
        no_enum = False
    except ImportError:
        try:
            from enum34 import Enum as _Enum
            no_enum = False
        except ImportError:
            pass

    if no_enum:
        raise RuntimeError(
            "This package requires an 'Enum' object. These are available "
            "in Python 3.4+, but requires a third-party library, either "
            "'enum34' or 'aenum'. Please install:\n\npip install --user aenum")


class _DocEnum(_Enum):
    def __init__(self, value, doc):
        try:
            super().__init__()
        except TypeError:
            # Python 2: the super() syntax was only introduced in Python 3.x
            super(_DocEnum, self).__init__()
        self._value_ = value
        self.__doc__ = doc

##########################################################################


BASE_URL = 'https://api.codepost.io'


class _Color:
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


_TERM_INFO = "{END}[{BOLD}INFO{END}]{END}".format(**_Color.__dict__)
_TERM_ERROR = "{END}[{BOLD}{RED}ERROR{END}]{END}".format(**_Color.__dict__)


def _print_info(msg):
    print("{tag} {msg}".format(tag=_TERM_INFO, msg=msg), file=_sys.stderr)


class UploadModes(_DocEnum):
    """
    Describes all possible predefined upload modes for codePost's upload methods.
    """

    CAUTIOUS = {
        "updateIfExists": False,
        "updateIfClaimed": False,
        "resolveStudents": False,

        "addFiles": False,
        "updateExistingFiles": False,
        "deleteUnspecifiedFiles": False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'Cautious' mode: If a submission already exists for this (student, assignment)
    pair (including partners), then cancel the upload. If no such submission exists,
    create it.
    """

    EXTEND = {
        "updateIfExists": True,
        "updateIfClaimed": False,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": False,
        "deleteUnspecifiedFiles": False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'Extend' mode: If a submission already exists for this (student, assignment) pair
    (including partners), then check to see if any files (key = name) in the upload request are
    not linked to the existing submission. If so, add these files to the submission. This mode
    does not unclaim a submission upon successful extension.
    """

    DIFFSCAN = {
        "updateIfExists": True,
        "updateIfClaimed": True,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles": False,

        "removeComments": False,
        "doUnclaim": False,
        "deleteAffectedSubmissions": False
    }, """
    With the 'DiffScan' mode: If a submission already exists for this (student, assignment) pair
    (including partners), compare the contents of uploaded files with their equivalent in the
    request body (key = (name, extension), value = code). If any files do not match, overwrite
    the existing files with their equivalent version in the request body. If no matching file
    exists in the submission, add it (same behavior as the 'Extend' mode). If any existing files
    are overwritten, clear comments on these files. This mode does not unclaim a submission upon
    successful extension.
    """

    OVERWRITE = {
        "updateIfExists": True,
        "updateIfClaimed": True,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles": True,

        "removeComments": True,
        "doUnclaim": True,
        "deleteAffectedSubmissions": True
    }, """
    With the 'Overwrite' mode: If a submission already exists for this (student, assignment) pair
    (including partners), overwrite it with the contents of the request. Keep the existing submission
    linked to any partners not included in the request. If at least one file is either added or
    updated, then: Delete any existing comments and unclaim the submission (set the `grader` field
    of the submission to `None`).
    """

    PREGRADE = {
        "updateIfExists": True,
        "updateIfClaimed": False,
        "resolveStudents": True,

        "addFiles": True,
        "updateExistingFiles": True,
        "deleteUnspecifiedFiles": True,

        "removeComments": True,
        "doUnclaim": False,
        "deleteAffectedSubmissions": True
    }, """
    If a submission has not been claimed, overwrite it.
    """


DEFAULT_UPLOAD_MODE = UploadModes.DIFFSCAN


def upload_test_output(api_key, course_name, course_period, student_email, assignment_name, test_output):
    # Find Assignment
    assn = codePost.get_assignment_info_by_name(
        api_key, course_name, course_period, assignment_name)
    if(not assn):
        raise Exception(
            "No Assignment found with the given name and course info. Please check to make sure the names are correct.")
    # Find Submission for student
    sub = codePost.get_assignment_submissions(
        api_key, assn['id'], student=student_email)
    if(len(sub) != 1):
        raise Exception("No submission found for this student and assignment.")
    # Parse the test output to the format desired to upload to codePost
    test_output_to_be_uploaded = parse_test_output(test_output)

    # Upload test output to codePost
    # new_file = codePost.post_file(api_key, sub[0]['id'], test_output_file_name, str(
    #     test_output_to_be_uploaded), "txt")

    file_to_upload = {"name": test_output_file_name,
                      "code": test_output_to_be_uploaded, "extension": "txt"}
    upload = codePost.upload_submission(api_key, assn, [student_email], [
                                        file_to_upload], mode=DEFAULT_UPLOAD_MODE)
    print(
        "Test output successfully updated. Check it out on codePost at www.codepost.io/grade/{sub}".format(sub=sub[0]['id']))
    # Add comments to file
    # add_comments(api_key, test_output, new_file)
    # print(upload)
    add_comments(api_key, test_output, upload)
    print(
        "Comments succesfully added. Check it out on codePost at www.codepost.io/grade/{sub}".format(sub=sub[0]['id']))


def parse_test_output(test_output):
    """
    Given a test output file and returns the file to be uploaded to codePost
    NOTE: THIS FUNCTION SHOULD BE EDITED BASED ON DESIRED USER BEHAVIOR
    """
    # question_data = test_output.split("Question")
    # output = []
    # for question in enumerate(question_data):
    #     if "k." in question:
    #         output.append("Question " + question[:4] + " failed a test.")

    # example: returns full test output
    return test_output


def add_comments(api_key, test_output, file):
    """
    Adds comments to a codePost file, given an API Key, output to parse for comments, and a file object
    NOTE: THIS FUNCTION SHOULD BE EDITED BASED ON DESIRED USER BEHAVIOR
    """
    # example: posts a comment for each failed test
    # syntax: post_comment(api_key, file, text, pointDelta, startChar, endChar, startLine, endLine, rubricComment=None)
    # pointDelta is parsed as a negative. e.g., a pointDelta of 1 is -1 on codePost'
    test_by_q = test_output.split("Question")
    line_counter = 0
    for i in test_by_q:
        if ("k.." in i):  # indicator that a single test failed
            comment_text = "### Question {question} has a failed test.".format(
                question=i[:4])
            codePost.post_comment(
                api_key, file, comment_text, 1, 0, 10, line_counter, line_counter)
        line_counter += len(i.split("\n"))-1


def get_output(notebook_data):
    test_output = ""
    for cell in notebook_data["cells"]:
        source = cell["source"]
        for line in source:
            if('ok.grade("q' in line):
                for output in cell["outputs"]:
                    test_output += ''.join(output["text"])
    return test_output


def getAssignmentData(assignment_name):
    """ Get assignment for given assignemnt name """
    assignment = codePost.get_assignment_info_by_name(
        api_key, course_name, course_period, assignment_name)
    if(not assignment):
        raise Exception(
            "No Assignment found with the given name and course info. Please check to make sure the name is correct.")
    else:
        return assignment


def processAllNotebooks(output_dir, assignment_name):
    """ Processes all notebooks in input directory for the assignment name
    and saves them to ouput directory
    """
    for file in os.listdir(output_dir):
        if(file.endswith(".ipynb")):
            try:
                print("Uploading Tests for: " + file + " 🤔")
                filepath = output_dir + '/' + file

                idx = file.rfind("_")
                student_email = file[:idx]

                test_output = processNotebook(
                    filepath, student_email, assignment_name)

                upload_test_output(api_key, course_name, course_period,
                                student_email, assignment_name, test_output)

                print(file + " has test output uploaded! 🎊")
            except Exception as e:
                print("❌!!ERROR!!❌:" + str(e))


def processNotebook(notebook_path, student_email, assignment_name):
    """ Processes the notebook to comment/delete okpy lines, and adds cell containing the
    autograder snippet
    """
    with open(notebook_path, 'r') as json_file:
        notebook_data = json.load(json_file)

    test_output = get_output(notebook_data)

    return test_output


def startProcess(output_dir, assignment_name):
    """ Runs all of the processing """
    assignment = getAssignmentData(assignment_name)
    processAllNotebooks(output_dir, assignment["name"])


def checkSysArgs():
    """ Checks to see if the right amount of parameters are passed by command line """
    if len(sys.argv) < 3:
        raise Exception(
            "There are missing parameters. The following are necessary Input Directory, Output Direcory, Assignment Name")


if __name__ == "__main__":

    checkSysArgs()
    output_dir, assignment_name, *rest = sys.argv[1:]
    startProcess(output_dir, assignment_name)
