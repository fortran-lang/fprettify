import site, os, inspect
site.addsitedir(mypath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))), known_paths=None)
