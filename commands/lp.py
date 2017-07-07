
__help__ = "  Name:         List Parents\n" \
           "  Syntax:       lp\n" \
           "  Description:  View current table's dependents"
__arg_list__ = {}

def cmd(data, arg_lst):
    if data.current_table == data.NULL_TABLE:
        print("No table seleteced, displaying all tables...")
        return data._DependencyNavigator2__ACTION__display_all_tables()
    table = data.tables[data.current_table]
    if len(table.dependiences) == 0:
        print("There are no dependencies for {}".format(data.current_table))
        return
    print("Table [{}] depends on (->):".format(data.current_table))
    data._DependencyNavigator2__ACTION__display_list(
        data._DependencyNavigator2__ACTION__get_dependencies(data.current_table),
        " -> "
    )
