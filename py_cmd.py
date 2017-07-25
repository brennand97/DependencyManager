"""
Author:      Brennan Douglas
Date:        6/14/2017
Description: TODO
"""

import sys
import importlib
import abc

class PyCMD:

    header_end = "~ "
    quit = False


    def __init__(self):
        self.cmd_callback = None
        self.header_callback = None


    def run(self, cmd_callback, header_callback):
        self.cmd_callback = cmd_callback
        self.header_callback = header_callback
        while not self.quit:
            cmd_callback(self.__split_input__(self.__get_input__()))


    def stop(self):
        self.quit = True


    def __get_input__(self):
        return self.input("{}{}".format(self.header_callback(), self.header_end))


    def input(self, s):
        if (sys.version_info > (3, 0)):
            return input(s)
        else:
            return raw_input(s)


    def __split_input__(self, cmd):
        return cmd.split(" ")


    def create_arg_lists(self, args, flag_arg_count):
        arg_lst = []
        a_i = 0
        while a_i < len(args):
            a = args[a_i]
            if a[:1] == "-":
                if any(a in s for s in flag_arg_count):
                    a_t = []
                    for f_i in range(0, flag_arg_count[a] + 1):
                        if a_i >= len(args):
                            raise ValueError
                        if f_i != 0 and args[a_i][:1] == "-":
                            raise ValueError
                        a_t.append(args[a_i])
                        a_i += 1
                    a_i -= 1
                    # Create tuple and append to the output list
                    arg_lst.append(a_t)
                else:
                    arg_lst.append([a])
            else:
                arg_lst.append([a])
            a_i += 1
        return arg_lst


class DynamicCmd:

    __metadata__ = abc.ABCMeta

    # Class dependencies
    dm = importlib.import_module("dynamic_module")


    def __init__(self, cmds_path,
                 start_callback=None,
                 pre_callback=None,
                 post_callback=None):
        self.py_cmd = PyCMD()
        self.commands = {}
        self.cmds_path = cmds_path
        self.dm.update_cmds(self.commands, self.cmds_path, False)
        self.pre_callback = pre_callback
        self.post_callback = post_callback
        self.start_callback = start_callback
        self.data = None


    def run(self):
        if self.start_callback != None:
            self.start_callback()
        self.py_cmd.run(self.handle_command, self.create_header)


    def handle_command(self, args):
        self.__update_commands()
        if self.pre_callback != None:
            self.pre_callback(args)
        action = args[0]
        action.lower()
        cmd_map = dict((c.lower(), c) for c in self.commands)

        if action == "help":
            if len(args) > 1:
                for a in args[1:]:
                    if a in cmd_map:
                        print("{}:".format(a))
                        print("{}".format(self.commands[cmd_map[a]].__help__))
                    else:
                        print("\"{}\" is an invalid command".format(a))
            else:
                for a in cmd_map:
                    print("{}:".format(a))
                    print("{}".format(self.commands[cmd_map[a]].__help__))
        elif action not in cmd_map:
            print("\"{}\" is an invalid command".format(action))
        else:
            a_cmd = self.commands[cmd_map[action]]
            try:
                arg_lst = self.py_cmd.create_arg_lists( \
                    args[1:], a_cmd.__arg_list__)
            except ValueError:
                print("Invalid syntax:\n{}".format(a_cmd.__help__))
                arg_lst = []
            a_cmd.cmd(self.data, arg_lst)

        if self.post_callback != None:
            self.post_callback(args)

            
    @abc.abstractmethod
    def create_header(self):
        return ""


    def __update_commands(self):
        self.dm.update_cmds(self.commands, self.cmds_path, True)


if __name__ == "__main__":
    dc = DynamicCmd("commands")
    dc.run()
