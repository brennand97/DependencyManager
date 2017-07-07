"""
Author:      Brennan Douglas
Date:        6/14/2017
Description: This command line tool is used to map dependency relations
             for a database's tables.
"""

import sys
import py_cmd as CMD
import copy_order as CO

class Table:

    def __init__(self, name: str):
        self.name: str = name
        self.dependiences: dict = {}
        self.dependents: dict = {}


class DependencyNavigator (CMD.DynamicCmd):

    NULL_TABLE: str = "__NULL__TABLE__NAME__"
    SAVED_SESSION: str = ".saved_session"
    SAVED_SESSION_OLD: str = ".saved_session_old"
    tables: dict = {}
    history: list = []
    current_table: str = NULL_TABLE

    def __init__(self, command_path: str, tables={}) -> None:
        """
        This function initilizes the Dependency Navigator and its parent class.
        It sets some of the DynamicCmd's callable variables to its methods.

        Args:
            command_path (str): The filepath to the folder that contains the command files
            tables (dict(Table)):
        """
        super().__init__(command_path, start_callback=self.start_callback, \
            pre_callback=self.pre_cmd_callback, post_callback=self.post_cmd_callback)
        self.tables = tables
        self.data: DependencyNavigator = self


    def pre_cmd_callback(self, args: list) -> None:
        pass


    def post_cmd_callback(self, args: list) -> None:
        self.shorten_history()


    def start_callback(self) -> None:
        if not self.load(self.SAVED_SESSION):
            self.save(self.SAVED_SESSION)


    def create_header(self) -> str:
        s: str = ""
        for t in self.history:
            if t == self.NULL_TABLE:
                continue
            s = "{}[{}]".format(s, t)
        if self.current_table != self.NULL_TABLE:
            s = "{}[{}]".format(s, self.current_table)
        return s


    def display_all_tables(self) -> None:
        if len(self.tables) == 0:
            print("There are currently no tables")
            return
        print("All Tables:")
        idx: int = 0
        self.display_list(
            sorted(self.tables),
            "   "
        )


    def shorten_history(self) -> None:
        history: list = self.history[:]
        history.append(self.current_table)
        for h_i in range(0, len(history) - 1):
            if CO.list_contains(history[h_i + 1:], history[h_i]):
                for h_j in range(h_i + 1, len(history)):
                    if history[h_i] == history[h_j]:
                        history = history[:h_i] + history[h_j:]
                        self.history = history[:-1]
                        return self.shorten_history()


    def add__dependency(self, p_name: str, t_name: str) -> bool:
        found: bool = False
        if not t_name in self.tables:
            table: Table = Table(t_name)
            self.tables[t_name] = table
        else:
            table: Table = self.tables[t_name]
            found = True
        if p_name != self.NULL_TABLE:
            p_table: Table = self.tables[p_name]
            p_table.dependiences[t_name] = table
            table.dependents[p_name] = p_table
        return found


    def add__dependent(self, c_name: str, t_name: str) -> bool:
        found: bool = False
        if not t_name in self.tables:
            table: Table = Table(t_name)
            self.tables[t_name] = table
        else:
            table: Table = self.tables[t_name]
            found = True
        if c_name != self.NULL_TABLE:
            c_table: Table = self.tables[c_name]
            c_table.dependents[t_name] = table
            table.dependiences[c_name] = c_table
        return found


    def delete_dependency(self, p_name: str, t_name: str) -> None:
        if p_name == self.NULL_TABLE:
            return self.delete_table(t_name)
        table: Table = self.tables[t_name]
        del table.dependents[p_name].dependiences[t_name]
        del table.dependents[p_name]


    def delete_dependent(self, c_name: str, t_name: str) -> None:
        if c_name == self.NULL_TABLE:
            return self.delete_table(t_name)
        table: Table = self.tables[t_name]
        del table.dependencies[c_name].dependents[t_name]
        del table.dependencies[c_name]


    def delete_table(self, t_name: str) -> None:
        table: Table = self.tables[t_name]
        #Delete table reference from the dependents array of each dependency
        for t_d in table.dependiences:
            del table.dependiences[t_d].dependents[t_name]
        #Delete table reference from the dependiences array of each dependent
        for t_d in table.dependents:
            del table.dependents[t_d].dependiences[t_name]
        #Delete table from table list
        del self.tables[t_name]


    def quit(self) -> None:
        self.py_cmd.stop()


    def get_dependencies(self, t_name: str) -> list:
        if t_name == self.NULL_TABLE:
            l: list = self.tables
        else:
            l: list = self.tables[t_name].dependiences
        deps: list = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def get_dependents(self, t_name: str) -> list:
        if t_name == self.NULL_TABLE:
            l: list = self.tables
        else:
            l: list = self.tables[t_name].dependents
        deps: list = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def display_list(self, l: list(str(object)), prefix: str) -> None:
        idx: int = 0
        for e in l:
            print("{}{:<6} [{}]".format(prefix, "({})".format(idx), e))
            idx = idx + 1


    def save(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            for t in sorted(self.tables):
                f.write("NEW,{}\n".format(self.tables[t].name))
            for t in sorted(self.tables):
                for t_d in sorted(self.tables[t].dependiences):
                    f.write("DEPENDENCY,{},{}\n".format(self.tables[t].name, self.tables[t].dependiences[t_d].name))
            f.close()


    def load_tmp(self, filepath: str) -> tuple:
        o_new: list = []
        o_dep: list = []
        with open(filepath, "r") as f:
            for line in f:
                if not line.strip():
                    break
                if line[:1] == "#":
                    continue
                cmd_struct: list = (line[:-1]).split(",")
                if cmd_struct[0] == "NEW":
                    o_new.append(cmd_struct[1])
                elif cmd_struct[0] == "DEPENDENCY":
                    o_dep.append((cmd_struct[1], cmd_struct[2]))
            f.close()
        return o_new, o_dep


    def load_sql_tmp(self, filepath: str) -> tuple:
        o_new: list = []
        o_dep: list = []
        with open(filepath, "r") as f:
            for line in f:
                if not line.strip():
                    break
                cmd_struct: list = (line[:-1]).split(",")
                database: str = cmd_struct[0]
                table: str = cmd_struct[1]
                o_new.append(table)
                if cmd_struct[2] != "NULL":    
                    for dependency in cmd_struct[2].split(";"):
                        if dependency == table:
                            continue
                        o_dep.append((table, dependency))
            f.close()
        return o_new, o_dep


    def load(self, filepath: str, sql=False) -> bool:
        try:
            if not sql:
                new, dep = self.load_tmp(filepath)
            else:
                new, dep = self.load_sql_tmp(filepath)
            for n in new:
                self.add__dependency(self.NULL_TABLE, n)
            for p, c in dep:
                self.add__dependency(p, c)
            return True
        except IOError:
            return False


    def remove_circular_dependencies(self, forward=True) -> None:
        cir: list = self.get_circular_dependencies()
        while len(cir) > 0:
            if forward:
                self.delete_dependency(cir[0][-1], cir[0][-2])
                print("Removed dependency: {} <- {}".format(cir[0][-2], cir[0][-1]))
            else:
                self.delete_dependent(cir[0][:1], cir[0][2])
                print("Removed dependency: {} <- {}".format(cir[0][1], cir[0][2]))
            cir = self.get_circular_dependencies()


    def get_circular_dependencies(self) -> list:
        paths: list = []
        tmp: list = []
        for t_name in self.tables:
            pths_tmp: list = self.detect_circular(self.tables[t_name])
            for cir_path in pths_tmp:
                cir_path = self.truncate_circular_list(cir_path)
                if cir_path != [] and cir_path != None:
                    paths.append(cir_path)
        return CO.list_leave_distinct(paths)


    def detect_circular(self, table: Table, history=[]) -> list:
        output: list = []
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


    def truncate_circular_list(self, lst: list) -> list:
        if len(lst) == 0:
            return []
        name: str = lst[-1]
        for i in range(len(lst[:-1]) - 1, -1, -1):
            if lst[i] == name:
                return lst[i:]


if __name__ == "__main__":
    sys.setrecursionlimit(512)
    nav = DependencyNavigator("commands")
    nav.run()
