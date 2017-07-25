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
        self.name = name
        self.dependiences = {}
        self.dependents = {}


class DependencyNavigator(CMD.DynamicCmd):
    """Command line interface for navigating and constructing a complex tree.

    This tree represetns a database dependency structure.  Each tree node, a
    Table, can have multiple children and multiple parents.  Where the children
    are that table's dependencies and the parents are objects that are dependent
    on that table.

    Attributes:
        NULL_TABLE (str): The reserved string that represents a null table or
            no table selected.
        SAVED_SESSION (str): The file name for the current saved session.
        SAVED_SESSION_OLD (str): The file name for the pervious saved session.
            This is done because the q command creates an empty SAVED_SESSION,
            so with this file an acidentally deleted session can be restored.
        tables (dict): A dictionary containing all of the instanciated tables.
            The key (str) is the table name, and the value (Table) is the table
            instance.
        history (list): A stack that represents the path through the tree
            nodes (tables) that the user has taken.
        current_table (str): The table name of the current table that the
            user is at.  NOTE: When this is set to NULL_TABLE it means that
            the user is not currently at a table.
    """

    NULL_TABLE = "__NULL__TABLE__NAME__"
    SAVED_SESSION = ".saved_session"
    SAVED_SESSION_OLD = ".saved_session_old"
    tables = {}
    history = []
    current_table = NULL_TABLE

    def __init__(self, command_path: str, tables={}) -> None:
        """DependencyNavigator initialization function

        This function initilizes the Dependency Navigator and its parent class.
        It sets some of the DynamicCmd's callable variables to its methods.

        Args:
            command_path (str): The filepath to the folder that contains the
                command files.
            tables (dict(Table)): A starting list of tables with relations to
                each other.  Defualts to and empty dictionary.

        Returns:
            None
        """
        super().__init__(command_path, start_callback=self.__start_callback, \
            pre_callback=self.__pre_cmd_callback, post_callback=self.__post_cmd_callback)
        self.tables = tables
        self.data = self


    def __pre_cmd_callback(self, args: list) -> None:
        pass


    def __post_cmd_callback(self, args: list) -> None:
        self.shorten_history()


    def __start_callback(self) -> None:
        if not self.load(self.SAVED_SESSION):
            self.save(self.SAVED_SESSION)


    def create_header(self) -> str:
        s = ""
        for t in self.history:
            if t == self.NULL_TABLE:
                continue
            s = "{}[{}]".format(s, t)
        if self.current_table != self.NULL_TABLE:
            s = "{}[{}]".format(s, self.current_table)
        return s


    def display_all_tables(self) -> None:
        """Displays all of the tables in self.tables

        This method will display all of the tables in self.tables if any
        exist, else it will print out that ther are currently no tables.

        Args:
            None

        Return:
            None
        """
        if not self.tables:
            print("There are currently no tables")
            return
        print("All Tables:")
        self.display_list(sorted(self.tables), "   ")


    def shorten_history(self) -> None:
        """Removes any circular paths in self.history

        This will traverse self.history and remove any circular segments
        that exist.  Without this method is circular paths were being
        continuously traversed through the length of the history string
        would become absurdly long.

        Args:
            None

        Returns:
            None
        """
        history = self.history[:]
        history.append(self.current_table)
        for h_i in range(0, len(history) - 1):
            if CO.list_contains(history[h_i + 1:], history[h_i]):
                for h_j in range(h_i + 1, len(history)):
                    if history[h_i] == history[h_j]:
                        history = history[:h_i] + history[h_j:]
                        self.history = history[:-1]
                        return self.shorten_history()


    def add_dependency(self, p_name: str, c_name: str) -> bool:
        """Adds dependency relationship between two tables

        This method will add a dependency to the table p_name and a dependent
        to the table c_name.  This will update the table instances in
        self.tables.  If neither of the tables exist they will be created and
        added to self.tables.  NOTE: If p_name or c_name is equal to
        NULL_TABLE this function will just serve as a method to create the
        other table if it is not equal to NULL_TABLE as well.

        Args:
            p_name (str): The table name of the parent table
            c_name (str): The table name of the child table

        Returns:
            bool: True if the child table already existed and was just
                updated.  False if the child table was created.  This
                result signals wether the child table was found.
        """

        # Return value
        found = False

        # Check if c_name is null
        if c_name != self.NULL_TABLE:
            # Check if child table exists
            if not c_name in self.tables:
                # If not create it
                table = Table(c_name)
                # And add it to self.tables
                self.tables[c_name] = table
            else:
                # Else pull the table into local variable from self.tables
                table = self.tables[c_name]
                # Set return value to True
                found = True

        # Check if p_name is null
        if p_name != self.NULL_TABLE:
            # Check if parent table exists
            if not p_name in self.tables:
                # If not create it
                p_table = Table(p_name)
                # And add it to self.tables
                self.tables[p_name] = p_table
            else:
                # Else pull the table into local variable from self.tables
                p_table = self.tables[p_name]

        # If both tables aren't null create dependency relation
        if p_name != self.NULL_TABLE and c_name != self.NULL_TABLE:
            # Set the child table as a dependency of the parent table
            p_table.dependiences[c_name] = table
            # Set the parent table as a dependent of the child table
            table.dependents[p_name] = p_table

        return found


    def add_dependent(self, c_name: str, p_name: str) -> bool:
        """Adds dependency relationship between two tables

        This method will add a dependency to the table p_name and a dependent
        to the table c_name.  This will update the table instances in
        self.tables.  If neither of the tables exist they will be created and
        added to self.tables.  NOTE: If c_name or p_name is equal to
        NULL_TABLE this function will just serve as a method to create the
        other table if it is not equal to NULL_TABLE as well.

        Args:
            c_name (str): The table name of the child table
            p_name (str): The table name of the parent table

        Returns:
            bool: True if the child table already existed and was just
                updated.  False if the child table was created.  This
                result signals wether the child table was found.
        """

        # This operation is the same as adding a dependency, just in reverse
        return self.add_dependency(p_name, c_name)


    def delete_dependency(self, p_name: str, t_name: str) -> None:
        if p_name == self.NULL_TABLE:
            return self.delete_table(t_name)
        table = self.tables[t_name]
        del table.dependents[p_name].dependiences[t_name]
        del table.dependents[p_name]


    def delete_dependent(self, c_name: str, t_name: str) -> None:
        if c_name == self.NULL_TABLE:
            return self.delete_table(t_name)
        table = self.tables[t_name]
        del table.dependencies[c_name].dependents[t_name]
        del table.dependencies[c_name]


    def delete_table(self, t_name: str) -> None:
        table = self.tables[t_name]
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
            l = self.tables
        else:
            l = self.tables[t_name].dependiences
        deps = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def get_dependents(self, t_name: str) -> list:
        if t_name == self.NULL_TABLE:
            l = self.tables
        else:
            l = self.tables[t_name].dependents
        deps = []
        for t_d in sorted(l):
            deps.append(t_d)
        return deps


    def display_list(self, l: list(str(object)), prefix: str) -> None:
        idx = 0
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


    def load_sql_tmp(self, filepath: str) -> tuple:
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


    def load(self, filepath: str, sql=False) -> bool:
        try:
            if not sql:
                new, dep = self.load_tmp(filepath)
            else:
                new, dep = self.load_sql_tmp(filepath)
            for n in new:
                self.add_dependency(self.NULL_TABLE, n)
            for p, c in dep:
                self.add_dependency(p, c)
            return True
        except IOError:
            return False


    def remove_circular_dependencies(self, forward=True) -> None:
        cir = self.get_circular_dependencies()
        while len(cir) > 0:
            if forward:
                self.delete_dependency(cir[0][-1], cir[0][-2])
                print("Removed dependency: {} <- {}".format(cir[0][-2], cir[0][-1]))
            else:
                self.delete_dependent(cir[0][:1], cir[0][2])
                print("Removed dependency: {} <- {}".format(cir[0][1], cir[0][2]))
            cir = self.get_circular_dependencies()


    def get_circular_dependencies(self) -> list:
        paths = []
        tmp = []
        for t_name in self.tables:
            pths_tmp = self.__detect_circular(self.tables[t_name])
            for cir_path in pths_tmp:
                cir_path = self.__truncate_circular_list(cir_path)
                if cir_path != [] and cir_path != None:
                    paths.append(cir_path)
        return CO.list_leave_distinct(paths)


    def __detect_circular(self, table: Table, history=[]) -> list:
        output = []
        # This is a post order recursive function
        if CO.list_contains(history, table.name):
            history.append(table.name)
            output.append(history)
            return output
        history.append(table.name)
        for dep in sorted(table.dependents):
            h = self.__detect_circular(table.dependents[dep], history[:])
            for c in h:
                output.append(c)
        history.pop()
        return output

    def __truncate_circular_list(self, lst: list) -> list:
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
