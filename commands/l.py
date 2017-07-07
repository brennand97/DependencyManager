
__help__ = "  Name:         Load\n" \
           "  Syntax:       l [-d | --dump] [--sql] <filepath>\n" \
           "  Description:  Load new structure from a dependecy save file"
__arg_list__ = {
    "-d"     : 0,
    "--dump" : 0,
    "--sql"  : 0
}

def cmd(data, arg_lst):
    dump = False
    filepath = ""
    sql = False
    if len(arg_lst) == 0:
        q_dump = data.py_cmd.input("Would you like to dump the current structure? (n): ")
        q_dump.lower()
        if q_dump.strip():
            if q_dump == "y" or q_dump == "yes":
                dump = True
        filepath = data.py_cmd.input("Filepath to depency structure file: ")
    else:
        for arg in arg_lst:
            if arg[0] == "-d" or arg[0] == "--dump":
                dump = True
            elif arg[0] == "--sql":
                sql = True
            else:
                filepath = arg[0]
        if filepath == "":
            filepath = data.py_cmd.input("Filepath to depency structure file: ")
    if dump:
        data.__CMD__dump_structure([])
        print("Dumped current structure")
    success = data._DependencyNavigator__ACTION__load(filepath, True) if sql else data.__ACTION__load(filepath, False)
    if success:
        print("Loaded structure from {}".format(filepath))
    else:
        print("\"{}\" does not exist".format(filepath))
