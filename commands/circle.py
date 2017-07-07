
__help__ = "  Name:         Circluar\n" \
           "  Syntax:       circle [-df | --delete-forward] [-db | --delete-backward]\n" \
           "  Description:  Displays/Deletes existing circler references"
__arg_list__ = {
    "-df"               : 0,
    "--delete-forward"  : 0,
    "-db"               : 0,
    "--delete-backward" : 0
}

def cmd(data, arg_lst):
    if len(arg_lst) == 0:
        paths = data.get_circular_dependencies()
        for cp in paths:
            s = ""
            for n in cp:
                s = "{}{}".format(s, "{} <- ".format(n))
            s = s[:-4]
            print("Circular path found: {}".format(s))
    else:
        if arg_lst[0][0] == "-df" or arg_lst[0][0] == "--delete-forward":
            data.remove_circular_dependencies(True)
        elif arg_lst[0][0] == "-db" or arg_lst[0][0] == "--delete-backward":
            data.remove_circular_dependencies(False)
