
import os

find_what = "is_local"

def do_file(path):
    root, ext = os.path.splitext(path)
    if ext == '.py' or ext == '.html' or ext == '.css':
        f = open(path)
        for i, line in enumerate(f.readlines()):
            if line.find(find_what) >= 0:
                print 'file %s, line %s' % (path, i+1)
        f.close()

def do_path(path):
    for what in os.listdir(path):
        path1 = os.path.join(path, what)
        if os.path.isdir(path1):
            do_path(path1)
        else:
            do_file(path1)

if __name__ == '__main__':
    start = os.getcwd()
    for folder in ['controllers', 'models', 'views', 'static']:
        path = os.path.join(start, folder)
        do_path(path)

