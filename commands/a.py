
__help__ = "  Name:         Add\n" \
           "  Syntax:       a [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...\n" \
           "  Description:  Adds tables and dependency relations"
__arg_list__ = {
    "-c"       : 1,
    "--child"  : 1,
    "-p"       : 1,
    "--parent" : 1
}

def cmd(data, arg_lst):
    new_names = []
    if len(arg_lst) == 0:
        child = True
        in_cp = ""
        while in_cp == "":
            in_cp = data.py_cmd.input("Is this table a (c)hild or a (p)arent" \
                                      " [(q)uit]: ")
            if in_cp == "c":
                child = True
            elif in_cp == "p":
                child = False
            elif in_cp == "q":
                return
            else:
                in_cp = ""
        new_names.append((child, data.py_cmd.input("Table name: ")))
    else:
        for arg in arg_lst:
            if len(arg) >= 1 and (arg[0] == "-c" or arg[0] == "--child"):
                child = True
                if len(arg) == 1 and len(arg_lst) == 1:
                    new_names.append((child, data.py_cmd.input("Table name: ")))
                elif len(arg) == 2:
                    new_names.append((child, arg[1]))
                else:
                    print("Multiple table entry only works with the syntax:")
                    print("   a [ [<-c | --child> <table name>] " \
                          "[<-p | --parent> <table name>] ]...")
                    return
            elif len(arg) >= 1 and (arg[0] == "-p" or arg[0] == "--parent"):
                child = False
                if len(arg) == 1 and len(arg_lst) == 1:
                    new_names.append((child, data.py_cmd.input("Table name: ")))
                elif len(arg) == 2:
                    new_names.append((child, arg[1]))
                else:
                    print("Multiple table entry only works with the syntax:")
                    print("   a [ [<-c | --child> <table name>] "\
                          "[<-p | --parent> <table name>] ]...")
                    return
    for child, new_name in new_names:
        if child:
            dependencies = data._DependencyNavigator__ACTION__get_dependencies( \
                data.current_table)
            if not new_name in dependencies:
                found = data._DependencyNavigator__ACTION__add__dependency( \
                    data.current_table, new_name)
                if found:
                    print("[{}] already existed and has been linked".format(new_name))
                else:
                    print("Successfully created [{}]".format(new_name))
            else:
                print("[{}] is already a child".format(new_name))
                return
        else:
            dependents = data._DependencyNavigator__ACTION__get_dependents( \
                data.current_table)
            if not new_name in dependents:
                found = data._DependencyNavigator__ACTION__add__dependent( \
                    data.current_table, new_name)
                if found:
                    print("[{}] already existed and has been linked".format(new_name))
                else:
                    print("Successfully created [{}]".format(new_name))
            else:
                print("[{}] is already a parent".format(new_name))
                return
