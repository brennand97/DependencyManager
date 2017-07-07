
__help__ = "  Name:         Clear\n" \
           "  Syntax:       clear\n" \
           "  Description:  Clears the screen"
__arg_list__ = {}

import os

def cmd(data, arg_lst):
    os.system('cls' if os.name=='nt' else 'clear')
