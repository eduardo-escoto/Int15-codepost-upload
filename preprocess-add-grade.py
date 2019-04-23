# REWRITTEN for UCSB INT 15 by Eduardo Escoto


"""
Importing Necessary Modules:

copyfile:    Used to copy files to temp directory
codePost:   Codepost api
            Install by 'pip install codePost'. 
            Documentation can be found at https://github.com/codepost-io/codePost-python
os:         For accessing folder structure
sys:        For accessing command line args
json:       For manipulating IPYNB JSON
"""
from shutil import copyfile, copytree, rmtree
import codePost_api as codePost
import os
import sys
import json

"""
Setting CodePost Constants:

api_key:        CodePost API Key
                Found in settings panel
                Set API key via %env cp_api_key = <API KEY> in nb file
course_name:    The course to upload assignments to
course_period:  The course period
"""
api_key = "c0f0e3594c99b2e58a46cf3fc97538385c28eae0"
course_name = 'New course'
course_period = '2019'


"""
Creating Utility functions to aid in processing the notebooks correctly
"""


def createIPYNBCell(cell_type_str, source_str_list, metadata_dict={}, output_list=[], exec_count=None):
    """ Returns a dictionary with the proper IPYNB specified formatting for code.
    Read more about how to format IPYNB json here: http://ipython.org/ipython-doc/stable/notebook/nbformat.html

    Parameters:
        :param cell_type_str: Specifies what kind of cell to create
        :type cell_type_str: str
        :param source_str_list: The source code for the cell with each line comma separated with a newline character at the end
        :type source_str_list: list
        :param metadata_dict: The desired cell metadata
        :default metadata_dict: {}
        :type metadata_dict: dictionary
        :param output_list: Contains output and output types
        :default output_list: []
        :param exec_count: Represents how many times the cell was ran
        :default exec_count: None
        :type exect_count: None or int

        :returns: IPYNB structured dictionary for a cell to be dumped to json
    """
    return {
        'cell_type': cell_type_str,
        "execution_count": exec_count,
        'metadata': metadata_dict,
        "outputs": output_list,
        'source': source_str_list
    }


def getUploadTestSnippet(student_email, assignment_name):
    """ Creates the snippet to run the okpy grader and then submit output to codepost """

    return [
        "import os\n",
        "import io\n",
        "from contextlib import redirect_stdout\n",
        "%env cp_api_key = {api}\n".format(api = api_key),
        "f = io.StringIO()\n",
        "with redirect_stdout(f):\n",
        "    [ok.grade(q[:-3]) for q in os.listdir('tests') if q.startswith('q')]\n",
        "test_output = f.getvalue()\n",
        "%run -i ../upload_tests.py {student_email} {assignment_name}".format(
            student_email=student_email, assignment_name=assignment_name)
    ]


def addCodePostSubmitCell(notebook_data, student_email, assignment_name):
    """ Adds a cell containing the autograder snippet """

    codepost_snippet = getUploadTestSnippet(student_email, assignment_name)
    codepost_snippet_json = createIPYNBCell("code", codepost_snippet)
    notebook_data["cells"].append(codepost_snippet_json)

    return notebook_data


def commentOKPYSubmit(notebook_data, mode="comment"):
    """ Comments out any lines that contain ok.submit() to prevent automatic resubmission for students 
    can change mode to 'delete' in order to remove the line instead"""
    for cell in notebook_data["cells"]:
        source = cell["source"]
        for index, line in enumerate(source):
            if("ok.submit" in line):
                if mode == "comment":
                    source[index] = "# Removed by AutoGrader" + line
                elif mode == "delete":
                    del source[index]

    return notebook_data


def processNotebook(notebook_path, student_email, assignment_name, ok_line_mode="comment"):
    """ Processes the notebook to comment/delete okpy lines, and adds cell containing the 
    autograder snippet 
    """
    with open(notebook_path, 'r') as json_file:
        notebook_data = json.load(json_file)

    notebook_data = commentOKPYSubmit(notebook_data)
    notebook_data = addCodePostSubmitCell(
        notebook_data, student_email, assignment_name)

    return notebook_data


def saveNotebook(notebook_data, path):
    """ Saves the notebook to path """
    with open(path, 'w') as out_file:
        json.dump(notebook_data, out_file, indent=2)


def copyTestsFolder(input_dir, output_dir, assignment_name):
    """ Copies tests to output dir """
    ok_file_name = assignment_name + '.ok'

    if os.path.exists(output_dir + "/tests"):
        rmtree(output_dir + "/tests")

    copytree(input_dir + "/tests", output_dir + "/tests")
    copyfile(input_dir + '/' + ok_file_name, output_dir + '/' + ok_file_name)


def processAllNotebooks(input_dir, output_dir, assignment_name, ok_line_mode="comment"):
    """ Processes all notebooks in input directory for the assignment name
    and saves them to ouput directory
    """
    temp_dir = output_dir + "_temp"

    if(not os.path.exists(output_dir)):
        os.mkdir(output_dir)

    if(not os.path.exists(temp_dir)):
        os.mkdir(temp_dir)

    for file in os.listdir(input_dir):
        if(file.endswith(".ipynb")):
            print("Now Processing: " + file + " 🤔")

            copyfile(input_dir+'/'+file, temp_dir+'/'+file)

            temp_nb_file_path = temp_dir + '/' + file
            final_nb_file_path = output_dir + '/' + file
            student_email = file.split('_')[0]

            new_notebook_data = processNotebook(
                temp_nb_file_path, student_email, assignment_name, ok_line_mode)

            saveNotebook(new_notebook_data, final_nb_file_path)

            os.remove(temp_dir+'/'+file)
            print(file + " has been processed! 🎊")

    os.rmdir(output_dir + "_temp")


def uploadNotebooksToCodePost(input_dir, assignment):
    """ Uploads notebooks to codepost """
    for file in os.listdir(input_dir):
        if(file.endswith(".ipynb")):
            student_email = file.split('_')[0]
            new_file_name = file.split('_')[1]
            file_to_upload = {"name": new_file_name, "code": open(
                input_dir+'/'+file, 'r').read(), "extension": "ipynb"}
            result = codePost.upload_submission(api_key, assignment, [student_email], [
                                                file_to_upload], codePost.UploadModes.OVERWRITE)
            if (result):
                print("Successfully uploaded notebook for %s" %
                      student_email + " 🎉 🎊")


def getAssignmentData(assignment_name):
    """ Get assignment for given assignemnt name """
    assignment = codePost.get_assignment_info_by_name(
        api_key, course_name, course_period, assignment_name)
    if(not assignment):
        raise Exception(
            "No Assignment found with the given name and course info. Please check to make sure the name is correct.")
    else:
        return assignment


def startProcess(input_dir, output_dir, assignment_name, ok_line_mode="comment"):
    """ Runs all of the processing """
    assignment = getAssignmentData(assignment_name)

    processAllNotebooks(input_dir, output_dir,
                        assignment["name"], ok_line_mode)

    uploadNotebooksToCodePost(input_dir, assignment)
    copyTestsFolder(input_dir, output_dir, assignment_name)


def checkSysArgs():
    """ Checks to see if the right amount of parameters are passed by command line """
    if len(sys.argv) < 4:
        raise Exception(
            "There are missing parameters. The following are necessary Input Directory, Output Direcory, Assignment Name")


if __name__ == "__main__":
    """ If this is run from the command line it will automatically process the notebooks. """
    checkSysArgs()
    input_dir, output_dir, assignment_name, *rest = sys.argv[1:]
    startProcess(input_dir, output_dir, assignment_name)
