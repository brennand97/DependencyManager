
__help__ = "  Name:         Save and Quit\n" \
           "  Syntax:       sq\n" \
           "  Description:  Save session then quit the tool"
__arg_list__ = {}

def cmd(data, arg_lst):
    data._DependencyNavigator2__ACTION__save(data.SAVED_SESSION)
    data._DependencyNavigator2__ACTION__quit()