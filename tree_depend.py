# Author:      Brennan Douglas
# Date:        6/14/2017
# Description: This command line tool is used to map dependency relations
#              for a database's tables.

import py_cmd as CMD
import copy_order as CO
import sys
import os

class Table:

    def __init__(self, name):
        self.name = name
        self.dependiences = {}
        self.dependents = {}

class DependencyNavigator:

    NULL_TABLE = "__NULL__TABLE__NAME__"
    SAVED_SESSION = ".saved_session"
    SAVED_SESSION_OLD = ".saved_session_old"
    tables = {}
    history = []
    current_table = NULL_TABLE

    def __init__(self, tables = {}):
        self.tables = tables
        self.py_cmd = CMD.PyCMD()

    def run(self):
        if not self.__ACTION__load(self.SAVED_SESSION):
            self.__ACTION__save(self.SAVED_SESSION)
        self.py_cmd.run(self.handle_command, self.__PY_CMD__create_header)


    def __PY_CMD__create_header(self):
        s = ""
        for t in self.history:
            if t == self.NULL_TABLE:
                continue
            s = "{}[{}]".format(s, t)
        if self.current_table != self.NULL_TABLE:
            s = "{}[{}]".format(s, self.current_table)
        return s


    def __CMD__display_all_tables(self, args):
        if len(self.tables) == 0:
            print("There are currently no tables")
            return
        print("All Tables:")
        idx = 0
        self.__ACTION__display_list(
            sorted(self.tables),
            "   "
        )


    def __CMD__display_current_dependencies(self, args):
        if self.current_table == self.NULL_TABLE:
            print("No table seleteced, displaying all tables...")
            return self.__CMD__display_all_tables([])
        table = self.tables[self.current_table]
        if len(table.dependiences) == 0:
            print("There are no dependencies for {}".format(self.current_table))
            return
        print("Table [{}] depends on (->):".format(self.current_table))
        self.__ACTION__display_list(
            self.__ACTION__get_dependencies(self.current_table),
            " -> "
        )


    def __CMD__display_current_dependents(self, args):
        if self.current_table == self.NULL_TABLE:
            print("No table seleteced, displaying all tables...")
            return self.__CMD__display_all_tables([])
        table = self.tables[self.current_table]
        if len(table.dependents) == 0:
            print("There are no dependents for {}".format(self.current_table))
            return
        print("Table [{}] is a dependency of (<-):".format(self.current_table))
        self.__ACTION__display_list(
            self.__ACTION__get_dependents(self.current_table),
            " <- "
        )


    def __CMD__add(self, args):
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "-c"       : 1,
                "--child"  : 1,
                "-p"       : 1,
                "--parent" : 1
            })
        except ValueError:
            print("Invalid syntax: a [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...")
            arg_lst = []
        new_names = []
        if len(arg_lst) == 0:
            child = True
            in_cp = ""
            while in_cp == "":
                in_cp = self.py_cmd.input("Is this table a (c)hild or a (p)arent [(q)uit]: ")
                if in_cp == "c":
                    child = True
                elif in_cp == "p":
                    child = False
                elif in_cp == "q":
                    return
                else:
                    in_cp = ""
            new_names.append((child, self.py_cmd.input("Table name: ")))
        else:
            for arg in arg_lst:
                if len(arg) >= 1 and (arg[0] == "-c" or arg[0] == "--child"):
                    child = True
                    if len(arg) == 1 and len(arg_lst) == 1:
                        new_names.append((child, self.py_cmd.input("Table name: ")))
                    elif len(arg) == 2:
                        new_names.append((child, arg[1]))
                    else:
                        print("Multiple table entry only works with the syntax:")
                        print("   a [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...")
                        return
                elif len(arg) >= 1 and (arg[0] == "-p" or arg[0] == "--parent"):
                    child = False
                    if len(arg) == 1 and len(arg_lst) == 1:
                        new_names.append((child, self.py_cmd.input("Table name: ")))
                    elif len(arg) == 2:
                        new_names.append((child, arg[1]))
                    else:
                        print("Multiple table entry only works with the syntax:")
                        print("   a [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...")
                        return
        for child, new_name in new_names:
            if child:
                dependencies = self.__ACTION__get_dependencies(self.current_table)
                if not new_name in dependencies:
                    found = self.__ACTION__add__dependency(self.current_table, new_name)
                    if found:
                        print("[{}] already existed and has been linked".format(new_name))
                    else:
                        print("Successfully created [{}]".format(new_name))
                else:
                    print("[{}] is already a child".format(new_name))
                    return
            else:
                dependents = self.__ACTION__get_dependents(self.current_table)
                if not new_name in dependents:
                    found = self.__ACTION__add__dependent(self.current_table, new_name)
                    if found:
                        print("[{}] already existed and has been linked".format(new_name))
                    else:
                        print("Successfully created [{}]".format(new_name))
                else:
                    print("[{}] is already a parent".format(new_name))
                    return


    def __CMD__delete(self, args):
        dependents = self.__ACTION__get_dependents(self.current_table)
        dependencies = self.__ACTION__get_dependencies(self.current_table)
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "-c"       : 1,
                "--child"  : 1,
                "-p"       : 1,
                "--parent" : 1
            })
        except ValueError:
            print("Invalid syntax: d [ [<-c | --child> <table name | index>] [<-p | --parent> <table name | index>] ]...")
            arg_lst = []
        new_names = []
        if len(arg_lst) == 0:
            child = True
            in_cp = ""
            while in_cp == "":
                in_cp = self.py_cmd.input("Removing a (c)hild or a (p)arent [(q)uit]: ")
                if in_cp == "c":
                    child = True
                elif in_cp == "p":
                    child = False
                elif in_cp == "q":
                    return
                else:
                    in_cp = ""
            tmp_t_n = self.py_cmd.input("Table: ")
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
                        new_name = self.py_cmd.input("Table name: ")
                    elif len(arg) == 2:
                        new_name = arg[1]
                    else:
                        print("Multiple table entry only works with the syntax:")
                        print("   d [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...")
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
                        new_name = self.py_cmd.input("Table name: ")
                    elif len(arg) == 2:
                        new_name = arg[1]
                    else:
                        print("Multiple table entry only works with the syntax:")
                        print("   d [ [<-c | --child> <table name>] [<-p | --parent> <table name>] ]...")
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
        for child, new_name in new_names:
            if child:
                if new_name in dependencies:
                    self.__ACTION__delete_dependency(self.current_table, new_name)
                    print("Successfully deleted [{}]{}".format(new_name, ("" if self.current_table == self.NULL_TABLE \
                        else " dependency from [{}]".format(self.current_table))))
                else:
                    print("[{}] {}".format(new_name, ("does not exist" if self.current_table == self.NULL_TABLE \
                        else "is not a child of [{}]".format(self.current_table))))
                    return
            else:
                if new_name in dependents:
                    self.__ACTION__delete_dependent(self.current_table, new_name)
                    print("Successfully deleted [{}]{}".format(new_name, ("" if self.current_table == self.NULL_TABLE \
                        else " dependency on [{}]".format(self.current_table))))
                else:
                    print("[{}] {}".format(new_name, ("does not exist" if self.current_table == self.NULL_TABLE \
                        else "is not a parent of [{}]".format(self.current_table))))
                    return


    def __CMD__move_up(self, args):
        dependents = self.__ACTION__get_dependents(self.current_table)
        if len(args) == 0:
            name = self.py_cmd.input("Dependent: ")
        elif len(args) == 1:
            name = args[0]
        elif len(args) == 2:
            if args[0] == "-n":
                name = args[1]
            else:
                print("Unkown argument flag")
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
        if name in self.__ACTION__get_dependents(self.current_table):
            self.history.append(self.current_table)
            self.current_table = name
        else:
            print("[{}] {}".format(name, ("does not exist" if self.current_table == self.NULL_TABLE \
                        else "is not a parent of [{}]".format(self.current_table))))


    def __CMD__move_in(self, args):
        dependencies = self.__ACTION__get_dependencies(self.current_table)
        if len(args) == 0:
            name = self.py_cmd.input("Dependency: ")
        elif len(args) == 1:
            name = args[0]
        elif len(args) == 2:
            if args[0] == "-n":
                name = args[1]
            else:
                print("Unkown argument flag")
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
        if name in self.__ACTION__get_dependencies(self.current_table):
            self.history.append(self.current_table)
            self.current_table = name
        else:
            print("[{}] {}".format(name, ("does not exist" if self.current_table == self.NULL_TABLE \
                        else "is not a child of [{}]".format(self.current_table))))


    def __CMD__history_back(self, args):
        if len(self.history) > 0:
            self.current_table = self.history.pop()
        else:
            print("There is no histroy to move up through.")
        return


    def __CMD__full_list(self, args):
        #Clear the history list
        del self.history[:]
        #Set the current table to null
        self.current_table = self.NULL_TABLE


    def __CMD__view_copy_order(self, args):
        order = CO.to_copy_order_v2(sorted(self.tables), self.tables)
        print("Group-Index  Name\n")
        g_index = 0
        for g in order:
            index = 0
            for i in g:
                print("{:<13}{}".format("{}-{}".format(g_index, index), i))
                index = index + 1
            g_index = g_index + 1
            print("")

        print("Total tables: {}".format(CO.D2_list_length(order)))
        print("Number of Groups: {}".format(len(order)))


    def __CMD__save_copy_order(self, args):
        order = CO.to_copy_order_v2(sorted(self.tables), self.tables)
        #Save to file
        filename = self.py_cmd.input("Savepath: ")
        with open(filename, "w") as f:
            g_index = 0
            for g in order:
                f.write("Group {}:\n\n".format(g_index))
                f.write("group,index,title\n")
                index = 0
                for i in g:
                    f.write("{},{},{}\n".format(g_index, index, i))
                    index = index + 1
                g_index = g_index + 1
                f.write("\n")
            f.close()


    def __CMD__dump_structure(self, args):
        for t in sorted(self.tables):
            del self.tables[t]


    def __CMD__help(self, args):
        print("Command                            Description")
        print("-------                            -----------")
        print("[Add: a]                           - Adds tables and dependency relations")
        print("[Delete: d]                        - Deletes tables and dependency relations")
        print("[Move Up: u]                       - Move to a dpendent of the current table")
        print("[Move In: i]                       - Move to a dependency of the current table")
        print("[History Back: hb]                 - Move backwards through your table path (history)")
        print("[Full List: fl]                    - Move back to the base, all tables")
        print("[Save: s]                          - Save the current structure")
        print("[Save Session: ss]                 - Save the current session")
        print("[Load: l]                          - Load new structure from a dependecy save file")
        print("[Dump Structure: ds]               - Dump the current structure")
        print("[Quit: q]                          - Quit the tool")
        print("[Save + Quit: sq]                  - Save session then quit the tool")
        print("[View Copy Order: co]              - Displays the copy order to the screen")
        print("[Save Copy Order: sco]             - Saves the structure in csv format, in copy order")
        print("[Circluar: circle]                 - Displays/Deletes existing circler references")
        print("[Difference: dif]                  - Shows the difference between two save files")
        print("[List Children (Dependencies): lc] - View current table's dependencies")
        print("[List Parents (Dependents): lp]    - View current table's dependents")
        print("[Clear: clear]                     - Clears the screen")
        print("[Help: help | h]                   - Displays this")


    def __CMD__save(self, args):
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "-f"     : 1,
                "--file" : 1
            })
        except ValueError:
            print("Invalid syntax: s [<-f | --file> <filepath>]")
            arg_lst = []
        if len(arg_lst) == 0:
            filepath = self.py_cmd.input("Filepath to save to: ")
        else:
            for arg in arg_lst:
                if (arg[0] == "-f" or arg[0] == "--file") and len(arg) == 2:
                    filepath = arg[1]
        self.__ACTION__save(filepath)
        print("Saved structre to {}".format(filepath))


    def __CMD__save_session(self, args):
        self.__ACTION__save(self.SAVED_SESSION)


    def __CMD__load(self, args):
        dump = False
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "-d"     : 0,
                "--dump" : 0,
                "--sql"  : 0
            })
        except ValueError:
            print("Invalid syntax: l [-d | --dump] [--sql] <filepath>")
            arg_lst = []
        filepath = ""
        sql = False
        if len(arg_lst) == 0:
            q_dump = self.py_cmd.input("Would you like to dump the current structure? (n): ")
            q_dump.lower()
            if q_dump.strip():
                if q_dump == "y" or q_dump == "yes":
                    dump = True
            filepath = self.py_cmd.input("Filepath to depency structure file: ")
        else:
            for arg in arg_lst:
                if arg[0] == "-d" or arg[0] == "--dump":
                    dump = True
                elif arg[0] == "--sql":
                    sql = True
                else:
                    filepath = arg[0]
            if filepath == "":
                filepath = self.py_cmd.input("Filepath to depency structure file: ")
        if dump:
            self.__CMD__dump_structure([])
            print("Dumped current structure")
        success = self.__ACTION__load(filepath, True) if sql else self.__ACTION__load(filepath, False)
        if success:
            print("Loaded structure from {}".format(filepath))
        else:
            print("\"{}\" does not exist".format(filepath))


    def __CMD__quit(self, args):
        if os.path.isfile(self.SAVED_SESSION_OLD):
            os.remove(self.SAVED_SESSION_OLD) 
        if os.path.isfile(self.SAVED_SESSION):
            os.rename(self.SAVED_SESSION, self.SAVED_SESSION_OLD)
        self.__CMD__dump_structure([])
        self.__ACTION__save(self.SAVED_SESSION)
        self.__ACTION__quit()


    def __CMD__save_and_quit(self, args):
        self.__ACTION__save(self.SAVED_SESSION)
        self.__ACTION__quit()


    def __CMD__clear(self, args):
        os.system('cls' if os.name=='nt' else 'clear')


    def __CMD__circle(self, args):
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "-df"               : 0,
                "--delete-forward"  : 0,
                "-db"               : 0,
                "--delete-backward" : 0
            })
        except ValueError:
            print("Invalid syntax: circle [-df | --delete-forward] [-db | --delete-backward]")
            arg_lst = []
        if len(arg_lst) == 0:
            paths = self.__ACTION__get_circular_dependencies()
            for cp in paths:
                s = ""
                for n in cp:
                    s = "{}{}".format(s, "{} <- ".format(n))
                s = s[:-4]
                print("Circular path found: {}".format(s))
        else:
            if arg_lst[0][0] == "-df" or arg_lst[0][0] == "--delete-forward":
                self.__ACTION__remove_circular_dependencies(True)
            elif arg_lst[0][0] == "-db" or arg_lst[0][0] == "--delete-backward":
                self.__ACTION__remove_circular_dependencies(False)


    def __CMD__difference(self, args):
        try:
            arg_lst = self.py_cmd.create_arg_lists(args, {
                "--sql" : 1
            })
        except ValueError:
            print("Invalid syntax: dif [--sql] <filepath1> [--sql] <filepath2>")
            arg_lst = []
            return
        files = []
        if not len(arg_lst) == 2:
            print("Invalid syntax: dif [--sql] <filepath1> [--sql] <filepath2>")
            return
        else:
            for arg in arg_lst:
                if len(arg) == 2 and arg[0] == "--sql":
                    files.append((arg[1], True))
                elif len(arg) == 1:
                    files.append((arg[0], False))
                else:
                    print("Invalid syntax: dif [--sql] <filepath1> [--sql] <filepath2>")
                    return
        f1_new, f1_dep = self.__ACTION__load_sql_tmp(files[0][0]) if files[0][1] else self.__ACTION__load_tmp(files[0][0])
        f2_new, f2_dep = self.__ACTION__load_sql_tmp(files[1][0]) if files[1][1] else self.__ACTION__load_tmp(files[1][0])
        for t_dif in list(set(f1_new) - set(f2_new)):
            if CO.list_contains(f1_new, t_dif):
                # This table exists in file1 and not file2
                print("\"{}\" Table: {}".format(files[0][0], t_dif))
            else:
                # This table exists in file2 and not file1
                print("\"{}\" Table: {}".format(files[1][0], t_dif))
        for t_dif in list(set(f2_new) - set(f1_new)):
            if CO.list_contains(f1_new, t_dif):
                # This table exists in file1 and not file2
                print("\"{}\" Table: {}".format(files[0][0], t_dif))
            else:
                # This table exists in file2 and not file1
                print("\"{}\" Table: {}".format(files[1][0], t_dif))
        for p_n, t_n in list(set(f1_dep) - set(f2_dep)):
            if CO.list_contains(f1_dep, (p_n, t_n)):
                # This dependency exists in file1 and not file2
                print("\"{}\" Dependency: {} -> {}".format(files[0][0], p_n, t_n))
            else:
                # This dependency exists in file2 and not file1
                print("\"{}\" Dependency: {} -> {}".format(files[1][0], p_n, t_n))
        for p_n, t_n in list(set(f2_dep) - set(f1_dep)):
            if CO.list_contains(f1_dep, (p_n, t_n)):
                # This dependency exists in file1 and not file2
                print("\"{}\" Dependency: {} -> {}".format(files[0][0], p_n, t_n))
            else:
                # This dependency exists in file2 and not file1
                print("\"{}\" Dependency: {} -> {}".format(files[1][0], p_n, t_n))


    def __ACTION__shorten_history(self):
        history = self.history[:]
        history.append(self.current_table)
        for h_i in range(0, len(history) - 1):
            if CO.list_contains(history[h_i + 1:], history[h_i]):
                for h_j in range(h_i + 1, len(history)):
                    if history[h_i] == history[h_j]:
                        history = history[:h_i] + history[h_j:]
                        self.history = history[:-1]
                        return self.__ACTION__shorten_history()


    def __ACTION__add__dependency(self, p_name, t_name):
        found = False
        if not t_name in self.tables:
            table = Table(t_name)
            self.tables[t_name] = table
        else:
            table = self.tables[t_name]
            found = True
        if p_name != self.NULL_TABLE:
            p_table = self.tables[p_name]
            p_table.dependiences[t_name] = table
            table.dependents[p_name] = p_table
        return found


    def __ACTION__add__dependent(self, c_name, t_name):
        found = False
        if not t_name in self.tables:
            table = Table(t_name)
            self.tables[t_name] = table
        else:
            table = self.tables[t_name]
            found = True
        if c_name != self.NULL_TABLE:
            c_table = self.tables[c_name]
            c_table.dependents[t_name] = table
            table.dependiences[c_name] = c_table
        return found


    def __ACTION__delete_dependency(self, p_name, t_name):
        if p_name == self.NULL_TABLE:
            return self.__ACTION__delete_table(t_name)
        table = self.tables[t_name]
        del table.dependents[p_name].dependiences[t_name]
        del table.dependents[p_name]


    def __ACTION__delete_dependent(self, c_name, t_name):
        if c_name == self.NULL_TABLE:
            return self.__ACTION__delete_table(t_name)
        table = self.tables[t_name]
        del table.dependencies[c_name].dependents[t_name]
        del table.dependencies[c_name]


    def __ACTION__delete_table(self, t_name):
        table = self.tables[t_name]
        #Delete table reference from the dependents array of each dependency
        for t_d in table.dependiences:
            del table.dependiences[t_d].dependents[t_name]
        #Delete table reference from the dependiences array of each dependent
        for t_d in table.dependents:
            del table.dependents[t_d].dependiences[t_name]
        #Delete table from table list
        del self.tables[t_name]


    def __ACTION__quit(self):
        self.py_cmd.stop()


    def __ACTION__get_dependencies(self, t_name):
        if t_name == self.NULL_TABLE:
            l = self.tables
        else:
            l = self.tables[t_name].dependiences
        deps = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def __ACTION__get_dependents(self, t_name):
        if t_name == self.NULL_TABLE:
            l = self.tables
        else:
            l = self.tables[t_name].dependents
        deps = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def __ACTION__display_list(self, l, prefix):
        idx = 0
        for e in l:
            print("{}{:<6} [{}]".format(prefix, "({})".format(idx), e))
            idx = idx + 1


    def __ACTION__save(self, filepath):
        with open(filepath, "w") as f:
            for t in sorted(self.tables):
                f.write("NEW,{}\n".format(self.tables[t].name))
            for t in sorted(self.tables):
                for t_d in sorted(self.tables[t].dependiences):
                    f.write("DEPENDENCY,{},{}\n".format(self.tables[t].name, self.tables[t].dependiences[t_d].name))
            f.close()


    def __ACTION__load_tmp(self, filepath):
        o_new = []
        o_dep = []
        with open(filepath, "r") as f:
            for line in f:
                if not line.strip():
                    break
                if line[:1] == "#":
                    continue
                cmd_struct = (line[:-1]).split(",")
                if cmd_struct[0] == "NEW":
                    o_new.append(cmd_struct[1])
                elif cmd_struct[0] == "DEPENDENCY":
                    o_dep.append((cmd_struct[1], cmd_struct[2]))
            f.close()
        return o_new, o_dep


    def __ACTION__load_sql_tmp(self, filepath):
        o_new = []
        o_dep = []
        with open(filepath, "r") as f:
            for line in f:
                if not line.strip():
                    break
                cmd_struct = (line[:-1]).split(",")
                database = cmd_struct[0]
                table = cmd_struct[1]
                o_new.append(table)
                if cmd_struct[2] != "NULL":    
                    for dependency in cmd_struct[2].split(";"):
                        if dependency == table:
                            continue
                        o_dep.append((table, dependency))
            f.close()
        return o_new, o_dep


    def __ACTION__load(self, filepath, sql = False):
        try:
            if not sql:
                new, dep = self.__ACTION__load_tmp(filepath)
            else:
                new, dep = self.__ACTION__load_sql_tmp(filepath)
            for n in new:
                self.__ACTION__add__dependency(self.NULL_TABLE, n)
            for p, c in dep:
                self.__ACTION__add__dependency(p, c)
            return True
        except IOError:
            return False


    def __ACTION__remove_circular_dependencies(self, forward = True):
        cir = self.__ACTION__get_circular_dependencies()
        while len(cir) > 0:
            if forward:
                self.__ACTION__delete_dependency(cir[0][-1], cir[0][-2])
                print("Removed dependency: {} <- {}".format(cir[0][-2], cir[0][-1]))
            else:
                self.__ACTION__delete_dependent(cir[0][:1], cir[0][2])
                print("Removed dependency: {} <- {}".format(cir[0][1], cir[0][2]))
            cir = self.__ACTION__get_circular_dependencies()


    def __ACTION__get_circular_dependencies(self):
        paths = []
        tmp = []
        for t_name in self.tables:
            pths_tmp = self.detect_circular(self.tables[t_name])
            for cir_path in pths_tmp:
                cir_path = self.truncate_circular_list(cir_path)
                if cir_path != [] and cir_path != None:
                    paths.append(cir_path)
        return CO.list_leave_distinct(paths)


    def detect_circular(self, table, history = []):
        output = []
        # This is a post order recursive function
        if CO.list_contains(history, table.name):
            history.append(table.name)
            output.append(history)
            return output
        history.append(table.name)
        for dep in sorted(table.dependents):
            h = self.detect_circular(table.dependents[dep], history[:])
            for c in h:
                output.append(c)
        history.pop()
        return output


    def truncate_circular_list(self, lst):
        if len(lst) == 0:
            return []
        name = lst[-1]
        for i in range(len(lst[:-1]) - 1, -1, -1):
            if lst[i] == name:
                return lst[i:]


    def handle_command(self, args):
        action = args[0]
        action.lower()
        if action == "a":
            self.__CMD__add(args[1:])
        elif action == "d":
            self.__CMD__delete(args[1:])
        elif action == "u":
            self.__CMD__move_up(args[1:])
        elif action == "i":
            self.__CMD__move_in(args[1:])
        elif action == "hb":
            self.__CMD__history_back(args[1:])
        elif action == "fl":
            self.__CMD__full_list(args[1:])
        elif action == "ds":
            self.__CMD__dump_structure(args[1:])
        elif action == "s":
            self.__CMD__save(args[1:])
        elif action == "ss":
            self.__CMD__save_session(args[1:])
        elif action == "l":
            self.__CMD__load(args[1:])
        elif action == "q":
            self.__CMD__quit(args[1:])
        elif action == "sq":
            self.__CMD__save_and_quit(args[1:])
        elif action == "co":
            self.__CMD__view_copy_order(args[1:])
        elif action == "sco":
            self.__CMD__save_copy_order(args[1:])
        elif action == "lc":
            self.__CMD__display_current_dependencies(args[1:])
        elif action == "lp":
            self.__CMD__display_current_dependents(args[1:])
        elif action == "help" or action == "h":
            self.__CMD__help(args[1:])
        elif action == "clear":
            self.__CMD__clear(args[1:])
        elif action == "circle":
            self.__CMD__circle(args[1:])
        elif action == "dif":
            self.__CMD__difference(args[1:])
        else:
            print("Invaild command")
        self.__ACTION__shorten_history()


if __name__ == "__main__":
    sys.setrecursionlimit(512)
    nav = DependencyNavigator({})
    if len(sys.argv) == 2:
        nav.load(sys.argv[1])
    nav.run()
