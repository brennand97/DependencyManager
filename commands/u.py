
__help__ = "  Name:         Move Up\n" \
           "  Syntax:       u [table name | table index]\n" \
           "  Description:  Move to a dpendent of the current table"
__arg_list__ = {}

def cmd(data, arg_lst):
    dependents = data._DependencyNavigator2__ACTION__get_dependents(data.current_table)
    if len(arg_lst) == 0:
        name = data.py_cmd.input("Dependent: ")
    elif len(arg_lst) == 1:
        name = arg_lst[0][0]
    try:
        idx = int(name)
        if idx < 0 or idx >= len(dependents):
            print("That index doesn't exist")
            print("The index of the dependent must be entered.")
            return
        else:
            name = dependents[idx]
    except ValueError:
        #The input was not a number
        pass
    if name in data._DependencyNavigator2__ACTION__get_dependents(data.current_table):
        data.history.append(data.current_table)
        data.current_table = name
    else:
        print("[{}] {}".format(name, ("does not exist" if data.current_table == data.NULL_TABLE \
                    else "is not a parent of [{}]".format(data.current_table))))
