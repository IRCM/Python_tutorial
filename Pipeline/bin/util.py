## Version 1.0
## Author: Matthew Suderman
## Date: 2013-06-20

import os
import errno
import fnmatch
import shutil
import subprocess
import sys
import datetime
import re

def stamp(): return(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def tee(text, log):
    text=stamp() + " " + text
    print >>log, text
    print text

def tee_error(text, log):
    tee("error: " + text, log)
    log.close()
    sys.exit(1)

def check_command_exists(command, log):
    if not command_exists(command):
        tee_error("installation missing " + " ".join(command), log)

def command_exists(command):
    try:
        with open(os.devnull, "w") as null:
            subprocess.call(command, stdout=null, stderr=null)
    except OSError as error:
        return False
    return True

def system_command(command, targets, log, stdout=None):
    msg = " ".join(command)
    if not isinstance(targets, list): 
        targets = [targets]
    if are_files(targets): 
        tee("skipping: " + msg, log)
        return
    tee("running: " + msg, log)

    if stdout is None:
        stdout_stream = log
    else:
        if isinstance(stdout, basestring):
            stdout_stream = open(stdout, 'w')
        else:
            stdout_stream = stdout

    try:
        ret=subprocess.call(command, stdout=stdout_stream, stderr=log)        
    except OSError:
        tee_error("could not run " + msg, log)

    if isinstance(stdout, basestring):
        stdout_stream.close()
        
    if ret != 0:
        tee_error(msg, log)
    else:
        tee("finished: " + msg, log)

def recursive_fnmatch(rootdir='.', pattern='*'):
    return [os.path.join(rootdir, filename)
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)]

def mkdir_p(path): ## for Python >= 3.2, os.makedirs(path,exist_ok=True)
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def strip_suffix(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:-len(suffix)]

def strip_prefix(text, prefix):
    if not text.startswith(prefix):
        return text
    return text[len(prefix):]

def are_files(filenames):
    if not isinstance(filenames, list): 
        filenames = [filenames]
    for filename in filenames:
        if not os.path.isfile(filename):
            return False
    return True

def remove_files(filenames):
    for filename in filenames:
        if os.path.isfile(filename):
            os.remove(filename)

## http://stackoverflow.com/questions/9178305/reading-formatted-text-using-python
def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('#'):
            yield line
