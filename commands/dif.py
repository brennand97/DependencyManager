
__help__ = "  Name:         Difference\n" \
           "  Syntax:       dif [--sql] <filepath1> [--sql] <filepath2>\n" \
           "  Description:  Shows the difference between two save files"
__arg_list__ = {
    "--sql" : 1
}

import copy_order as CO

def cmd(data, arg_lst):
    files = []
    if not len(arg_lst) == 2:
        print("Invalid syntax: dif [--sql] <filepath1> [--sql] <filepath2>")
        return
    else:
        for arg in arg_lst:
            if len(arg) == 2 and arg[0] == "--sql":
                files.append((arg[1], True))
            elif len(arg) == 1:
                files.append((arg[0], False))
            else:
                print("Invalid syntax: dif [--sql] <filepath1> [--sql] <filepath2>")
                return
    f1_new, f1_dep = data._DependencyNavigator__ACTION__load_sql_tmp(files[0][0]) if files[0][1] else data.__ACTION__load_tmp(files[0][0])
    f2_new, f2_dep = data._DependencyNavigator__ACTION__load_sql_tmp(files[1][0]) if files[1][1] else data.__ACTION__load_tmp(files[1][0])
    for t_dif in list(set(f1_new) - set(f2_new)):
        if CO.list_contains(f1_new, t_dif):
            # This table exists in file1 and not file2
            print("\"{}\" Table: {}".format(files[0][0], t_dif))
        else:
            # This table exists in file2 and not file1
            print("\"{}\" Table: {}".format(files[1][0], t_dif))
    for t_dif in list(set(f2_new) - set(f1_new)):
        if CO.list_contains(f1_new, t_dif):
            # This table exists in file1 and not file2
            print("\"{}\" Table: {}".format(files[0][0], t_dif))
        else:
            # This table exists in file2 and not file1
            print("\"{}\" Table: {}".format(files[1][0], t_dif))
    for p_n, t_n in list(set(f1_dep) - set(f2_dep)):
        if CO.list_contains(f1_dep, (p_n, t_n)):
            # This dependency exists in file1 and not file2
            print("\"{}\" Dependency: {} -> {}".format(files[0][0], p_n, t_n))
        else:
            # This dependency exists in file2 and not file1
            print("\"{}\" Dependency: {} -> {}".format(files[1][0], p_n, t_n))
    for p_n, t_n in list(set(f2_dep) - set(f1_dep)):
        if CO.list_contains(f1_dep, (p_n, t_n)):
            # This dependency exists in file1 and not file2
            print("\"{}\" Dependency: {} -> {}".format(files[0][0], p_n, t_n))
        else:
            # This dependency exists in file2 and not file1
            print("\"{}\" Dependency: {} -> {}".format(files[1][0], p_n, t_n))
