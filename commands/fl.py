
__help__ = ""
__arg_list__ = {}

def cmd(self, arg_lst):
    #Clear the history list
    del self.history[:]
    #Set the current table to null
    self.current_table = self.NULL_TABLE
