
__help__ = "  Name:         List Parents\n" \
           "  Syntax:       lp\n" \
           "  Description:  View current table's dependents"
__arg_list__ = {}

def cmd(data, arg_lst):
    if data.current_table == data.NULL_TABLE: 
        print("No table seleteced, displaying all tables...") 
        return data.display_all_tables()
    table = data.tables[data.current_table] 
    if len(table.dependents) == 0: 
        print("There are no dependents for {}".format(data.current_table)) 
        return 
    print("Table [{}] is a dependency of (<-):".format(data.current_table)) 
    data.display_list( 
        data.get_dependents(data.current_table), 
        " <- " 
    ) 
