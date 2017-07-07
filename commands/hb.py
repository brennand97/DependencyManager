
__help__ = "  Name:         History Back\n" \
           "  Syntax:       hb\n" \
           "  Description:  Move backwards through your table path (history)"
__arg_list__ = {}

def cmd(data, arg_lst):
    if len(data.history) > 0:
        data.current_table = data.history.pop()
    else:
        print("There is no histroy to move up through.")
    return