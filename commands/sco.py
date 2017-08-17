
__help__ = "  Name:         Save Copy Order\n" \
           "  Syntax:       sco\n" \
           "  Description:  Saves the structure in csv format, in copy order"
__arg_list__ = {}

import copy_order as CO

def cmd(data, arg_lst):
    order = CO.to_copy_order_v2(sorted(data.tables), data.tables)
    #Save to file
    filename = data.py_cmd.input("Savepath: ")
    try:
        with open(filename, "w") as f:
            g_index = 0
            for g in order:
                f.write("Group {}:\n\n".format(g_index))
                f.write("group,index,title\n")
                index = 0
                for i in g:
                    f.write("{},{},{}\n".format(g_index, index, i))
                    index = index + 1
                g_index = g_index + 1
                f.write("\n")
            f.close()
    except Exception as e:
        print("Could not save file, error: ", e)
