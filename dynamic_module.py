""" Dynamic module loader """

import importlib

def update_cmds(commands, path, remove=False):
    """ This function will load all the new modules found in
        path into commands that are not currently in commands """
    # Load module folder
    cmds = importlib.import_module(path)

    # Update modules
    for mod in cmds.__all__:
        if mod in commands:
            # Old module
            del commands[mod]
        commands[mod] = importlib.import_module("{}.{}".format(path, mod))

    if remove:
        # Check for old commands
        for cmd in commands:
            if cmd not in cmds.__all__:
                del commands[cmd]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("A path needs to be provided")
        print("Exiting...")
        sys.exit(1)
    G_COMMANDS = {}
    update_cmds(G_COMMANDS, sys.argv[1])
    print("Loaded Modules: {}".format(G_COMMANDS))
    sys.exit(0)
