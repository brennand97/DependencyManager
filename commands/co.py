
__help__ = "  Name:         View Copy Order\n" \
           "  Syntax:       co\n" \
           "  Description:  Displays the copy order to the screen"
__arg_list__ = {}

import copy_order as CO

def cmd(data, arg_lst):
    order = CO.to_copy_order_v2(sorted(data.tables), data.tables)
    print("Group-Index  Name\n")
    g_index = 0
    for g in order:
        index = 0
        for i in g:
            print("{:<13}{}".format("{}-{}".format(g_index, index), i))
            index = index + 1
        g_index = g_index + 1
        print("")

    print("Total tables: {}".format(CO.D2_list_length(order)))
    print("Number of Groups: {}".format(len(order)))
