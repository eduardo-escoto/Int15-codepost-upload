import os
import sys
import requests
# install by 'pip install codePost'. Documentation can be found at https://github.com/codepost-io/codePost-python
import codePost_api as codePost

# set API key via %env cp_api_key = <API KEY>
api_key = os.environ["cp_api_key"]
course_name = 'New course'
course_period = '2019'
student_email = sys.argv[1]
assignment_name = sys.argv[2]

# NOTE: THIS SHOULD BE EDITED BY USER BASED ON DESIRED BEHAVIOR. File name for codePost
test_output_file_name = "Output.txt"

import sys as _sys
import requests as _requests

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
        from aenum import Enum as _Enum
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
        "deleteUnspecifiedFiles" : False,

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
        "deleteUnspecifiedFiles" : False,

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
        "deleteUnspecifiedFiles" : False,

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
        "deleteUnspecifiedFiles" : True,

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
        "deleteUnspecifiedFiles" : True,

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


if __name__ == "__main__":
    upload_test_output(api_key, course_name, course_period,
                       student_email, assignment_name, test_output)
