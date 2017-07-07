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


class DependencyNavigator (CMD.DynamicCmd):

    NULL_TABLE = "__NULL__TABLE__NAME__"
    SAVED_SESSION = ".saved_session"
    SAVED_SESSION_OLD = ".saved_session_old"
    tables = {}
    history = []
    current_table = NULL_TABLE

    def __init__(self, command_path, tables = {}):
        super().__init__(command_path,
            start_callback=self.start_callback,
            pre_callback=self.pre_cmd_callback,
            post_callback=self.post_cmd_callback)
        self.tables = tables
        self.data = self


    def pre_cmd_callback(self, args):
        pass


    def post_cmd_callback(self, args):
        self.__ACTION__shorten_history()


    def start_callback(self):
        if not self.__ACTION__load(self.SAVED_SESSION):
            self.__ACTION__save(self.SAVED_SESSION)


    def create_header(self):
        s = ""
        for t in self.history:
            if t == self.NULL_TABLE:
                continue
            s = "{}[{}]".format(s, t)
        if self.current_table != self.NULL_TABLE:
            s = "{}[{}]".format(s, self.current_table)
        return s

    
    def __ACTION__display_all_tables(self):
        if len(self.tables) == 0:
            print("There are currently no tables")
            return
        print("All Tables:")
        idx = 0
        self.__ACTION__display_list(
            sorted(self.tables),
            "   "
        )


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


if __name__ == "__main__":
    sys.setrecursionlimit(512)
    nav = DependencyNavigator("commands")
    nav.run()
