# Author:      Brennan Douglas
# Date:        6/14/2017
# Description: TODO

import sys

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
			
