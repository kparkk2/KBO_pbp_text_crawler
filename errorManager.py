# errorManager.py


def print_error(file_name, line_no, func_name, error_msg, error_type=None):
    print("From {0} in {1}:{2}".format(func_name, file_name, line_no))
    if error_type is not None:
        print(error_type)
    print(error_msg)
    exit(1)
