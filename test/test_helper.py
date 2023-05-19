import sys, os

def setup_dirs():
    # add abberition to the path
    abberition_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../abberition'))
    sys.path.append(abberition_path)