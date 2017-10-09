import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tests
def run():
    print tests.__name__
    for key, value in tests.__dict__.items():
        print key
        print value
