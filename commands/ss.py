
__help__ = "  Name:         Save Session\n" \
           "  Syntax:       ss\n" \
           "  Description:  Save the current session"
__arg_list__ = {}

def cmd(data, arg_lst):
    data.save(data.SAVED_SESSION)
