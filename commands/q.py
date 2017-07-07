
__help__ = "  Name:         Quit\n" \
           "  Syntax:       q\n" \
           "  Description:  Quit the tool"
__arg_list__ = {}

import os

def cmd(data, arg_lst):
    if os.path.isfile(data.SAVED_SESSION_OLD):
        os.remove(data.SAVED_SESSION_OLD) 
    if os.path.isfile(data.SAVED_SESSION):
        os.rename(data.SAVED_SESSION, data.SAVED_SESSION_OLD)
    if "ds" in data.commands:
        data.commands["ds"].cmd()
    data._DependencyNavigator__ACTION__save(data.SAVED_SESSION)
    data._DependencyNavigator__ACTION__quit()
