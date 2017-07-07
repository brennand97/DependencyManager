
__help__ = "  Name:         Save\n" \
           "  Syntax:       s [<-f | --file> <filepath>]\n" \
           "  Description:  Save the current structure"
__arg_list__ = {
    "-f"     : 1,
    "--file" : 1
}

def cmd(data, arg_lst):
    if len(arg_lst) == 0:
        filepath = data.py_cmd.input("Filepath to save to: ")
    else:
        for arg in arg_lst:
            if (arg[0] == "-f" or arg[0] == "--file") and len(arg) == 2:
                filepath = arg[1]
    data._DependencyNavigator__ACTION__save(filepath)
    print("Saved structre to {}".format(filepath))
