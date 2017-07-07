
__help__ = "  Name:         Full List\n" \
           "  Syntax:       fl\n" \
           "  Description:  Move back to the base, all tables"
__arg_list__ = {}

def cmd(self, arg_lst):
    #Clear the history list
    del self.history[:]
    #Set the current table to null
    self.current_table = self.NULL_TABLE
