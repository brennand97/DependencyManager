
__help__ = "  Name:         Dump Structure\n" \
           "  Syntax:       ds\n" \
           "  Description:  Dump the current structure"
__arg_list__ = {}

def cmd(data, arg_lst):
    for t in sorted(data.tables):
        del data.tables[t]
