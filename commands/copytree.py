
__syntax__ = "copytree [table name]"
__help__ = "  Name:         Copy Tree\n" \
           "  Syntax:       copytree\n" \
           "  Description:  Displays the depents tree in of the given table in the copy order."
__arg_list__ = {}

import copy_order as CO

#TODO make circular reference proof
def cmd(data, arg_lst):
    if not arg_lst:
        print("Needs a table name:")
        print("    {}".format(__syntax__))
        return
    print("WARNING: This command will infinently stall on circular references.")
    yes = (input("Would you like to continue? (Y,n) ")).lower()
    if yes != "" and yes[0:1] == "n":
        return
    table_name = arg_lst[0][0]
    dependents = {}
    groups = {}
    order = CO.to_copy_order_v2(sorted(data.tables), data.tables)
    if not CO.D2_list_contains(order, table_name):
        print("ERROR: The copy order did not contain the table name \"{}\"".format(table_name))
        return
    get_dependents_list(data, order, dependents, groups, table_name)
    print("Copy Tree:")
    print_tree("  ", dependents, groups)


def get_dependents_list(data, order, dictionary, groups, table_name):
    depts = data.get_dependents(table_name)
    dictionary[table_name] = {}
    groups[table_name] = CO.D2_list_find(order, table_name)[0]
    for d in depts:
        if not CO.D2_list_contains(order, d):
            print("WARNING: \"{}\" is not in copy order".format(d))
        else:
            get_dependents_list(data, order, dictionary[table_name], groups, d)

def print_tree(tab, dictionary, groups):
    for name in dictionary:
        print("{}({}) - {}".format(tab, groups[name], name))
        print_tree("{}{}".format(tab, tab), dictionary[name], groups)