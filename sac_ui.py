from Clases.App import App
from tkinter import messagebox
from Utils.Metadata import *
from Utils.GlobalFunctions import *
import sys

if __name__ == '__main__':
    if (len(sys.argv) >= 2):
        user = sys.argv[1]
    else:
        user = 'SERVIDOR'
    createCacheFile(user=user, script=VISUALIZING_ACTIVITY)
    app = App(user=user)