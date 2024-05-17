from Clases.App import App
from Utils.Metadata import *
import sys

if __name__ == '__main__':
    if (len(sys.argv) >= 2):
        user = sys.argv[1]
    else:
        user = 'SERVIDOR'
    app = App(user=user)