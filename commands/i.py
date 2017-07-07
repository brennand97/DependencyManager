
__help__ = "  Name:         Move In\n" \
           "  Syntax:       i [table name | table index]\n" \
           "  Description:  Move to a dependency of the current table"
__arg_list__ = {}

def cmd(data, arg_lst):
    dependencies = data.get_dependencies(data.current_table)
    if len(arg_lst) == 0:
        name = data.py_cmd.input("Dependency: ")
    elif len(arg_lst) == 1:
        name = arg_lst[0][0]
    try:
        idx = int(name)
        if idx < 0 or idx >= len(dependencies):
            print("That index doesn't exist")
            print("The index of the dependency must be entered.")
            return
        else:
            name = dependencies[idx]
    except ValueError:
        #The input was not a number
        pass
    if name in data.get_dependencies(data.current_table):
        data.history.append(data.current_table)
        data.current_table = name
    else:
        print("[{}] {}".format(name, ("does not exist" if data.current_table == data.NULL_TABLE \
                    else "is not a child of [{}]".format(data.current_table))))
