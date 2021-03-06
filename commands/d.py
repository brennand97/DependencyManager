
__syntax__ = "d [ [<-c | --child> | <-p | --parent> | <-h | --hard> ] <table name | index>]..."

__help__ = ("  Name:         Delete\n"
            "  Syntax:       {}\n"
            "  Description:  Deletes tables and dependency relations".format(__syntax__))

__arg_list__ = {
    "-c"       : 1,
    "--child"  : 1,
    "-p"       : 1,
    "--parent" : 1,
    "-h"       : 1,
    "--hard"   : 1
}

# TODO: Make subfunctions for this code as there is a lot of large complex repeating segments.

def cmd(data, arg_lst):
    dependents = data.get_dependents(data.current_table)
    dependencies = data.get_dependencies(data.current_table)
    new_names = []
    if not arg_lst:
        child = True
        in_cp = ""
        while in_cp == "":
            in_cp = data.py_cmd.input("Removing a (c)hild or a (p)arent [(q)uit]: ")
            if in_cp == "c":
                child = True
            elif in_cp == "p":
                child = False
            elif in_cp == "q":
                return
            else:
                in_cp = ""
        tmp_t_n = data.py_cmd.input("Table: ")
        try:
            idx = int(tmp_t_n)
            lst = (dependencies if child else dependents)
            if idx < 0 or idx >= len(lst):
                print("That index doesn't exist")
                print("The index of the dependent must be entered.")
                return
            else:
                tmp_t_n = lst[idx]
        except ValueError:
            #The input was not a number
            pass
        new_names.append((child, tmp_t_n))
    else:
        for arg in arg_lst:
            if len(arg) >= 1 and (arg[0] == "-c" or arg[0] == "--child"):
                child = True
                new_name = ""
                if len(arg) == 1 and len(arg_lst) == 1:
                    new_name = data.py_cmd.input("Table name: ")
                elif len(arg) == 2:
                    new_name = arg[1]
                else:
                    print("Multiple table entry only works with the syntax:")
                    print("   {}".format(__syntax__))
                    return
                try:
                    idx = int(new_name)
                    lst = (dependencies if child else dependents)
                    if idx < 0 or idx >= len(lst):
                        print("That index doesn't exist")
                        print("The index of the dependent must be entered.")
                        return
                    else:
                        new_name = lst[idx]
                except ValueError:
                    #The input was not a number
                    pass
                new_names.append((child, new_name))
            elif len(arg) >= 1 and (arg[0] == "-p" or arg[0] == "--parent"):
                child = False
                new_name = ""
                if len(arg) == 1 and len(arg_lst) == 1:
                    new_name = data.py_cmd.input("Table name: ")
                elif len(arg) == 2:
                    new_name = arg[1]
                else:
                    print("Multiple table entry only works with the syntax:")
                    print("   {}".format(__syntax__))
                    return
                try:
                    idx = int(new_name)
                    lst = (dependencies if child else dependents)
                    if idx < 0 or idx >= len(lst):
                        print("That index doesn't exist")
                        print("The index of the dependent must be entered.")
                        return
                    else:
                        new_name = lst[idx]
                except ValueError:
                    #The input was not a number
                    pass
                new_names.append((child, new_name))
            elif len(arg) > 1 and (arg[0] == "-h" or arg[0] == "--parent"):
                print("Hard option is not yet implmented...")
                # TODO: implement hard option
    for child, new_name in new_names:
        if child:
            if new_name in dependencies:
                data.delete_dependency(data.current_table, new_name)
                print("Successfully deleted [{}]{}".format(new_name, ("" if data.current_table == data.NULL_TABLE \
                    else " dependency from [{}]".format(data.current_table))))
            else:
                print("[{}] {}".format(new_name, ("does not exist" if data.current_table == data.NULL_TABLE \
                    else "is not a child of [{}]".format(data.current_table))))
                return
        else:
            if new_name in dependents:
                data.delete_dependent(data.current_table, new_name)
                print("Successfully deleted [{}]{}".format(new_name, ("" if data.current_table == data.NULL_TABLE \
                    else " dependency on [{}]".format(data.current_table))))
            else:
                print("[{}] {}".format(new_name, ("does not exist" if data.current_table == data.NULL_TABLE \
                    else "is not a parent of [{}]".format(data.current_table))))
                return
