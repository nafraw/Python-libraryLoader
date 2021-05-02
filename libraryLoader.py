# -*- coding: utf-8 -*-
"""
Created on Sun May  2 22:05:38 2021

@author: Ping-Keng Jao

Purpose of file:
    for adding paths from a config file, suitable for lazy persons :)
    
    Example of scenario 1:
        Running the same project on different machines with different library path.
        The script can run the formattedLoader to load a corresponding config file based on the information of the machine.
        
    Example of scenario 2:
        You don't want to see so many path information in a .py file when importing.
        Run add_path_from_file() and remember to set verbose=False if wish not to see the info on the terminal.
"""

import os
import sys
import platform
import getpass

def formattedLoader(prefix='library_path', proj_name='', file_format=['proj', 'OS'], priority=1, verbose=True):
    # This function will find a config file and add the written lines as a system path with a high priority
    # config file should be named with at least one of the keyword below:
    # OS, computer name, user, or project name
    # The filename ends with .cfg and a underscore between each keyword above
    # e.g.: {prefix}_{proj}_{OS}.cfg
    
    # collect essential information
    OS = get_OS()
    cname = get_computer_name()
    user = get_user()
    
    # get config
    info = {'OS': OS, 'Computer Name': cname, 'User': user, 'Project': proj_name}
    filename = prefix
    for f in file_format:
        f = remap_keyword(f)
        filename += '_' + info[f]
    filename += '.cfg'
    
    add_path_from_file(filename, priority=priority, verbose=verbose)

def add_path_from_file(file: str, priority=1, verbose=True):
    with open(file) as f:
        lines = f.readlines()
    print(f'\x1b[42mLoading: {file}\x1b[0m')
    for l in lines:        
        if l not in sys.path: # no need to add multiple times
            if not os.isdir(l):
                print(f'\x1b[41mConfig file contains a non-folder line: {l}\x1b[0m')
            sys.path.insert(priority, l)
            if verbose:
                print(f"adding path: {l}", end='')
    print('')

def remap_keyword(k: str) -> str:
    kl = k.lower() # convert to lower case
    synonym = {'OS': ['os', 'operating system'], 
               'Computer Name': ['cname', 'computer name', 'com', 'computer', 'name', 'c name'],
               'User': ['user', 'uid', 'id'],
               'Project': ['proj', 'project', 'pro', 'project name', 'pname', 'p name']
              }
    if kl in synonym['OS']:
        return 'OS'
    elif kl in synonym['Computer Name']:
        return 'Computer Name'
    elif kl in synonym['User']:
        return 'User'
    elif kl in synonym['Project']:
        return 'Project'
    else:
        print(f'\x1b[41mUnknown keyword: {k}\x1b[0m')
        print('\x1b[41mPlease find the supported case-insensitive keyword from the list below:\x1b[0m')
        print(f'\x1b[41m{synonym}\x1b[0m')

def get_OS() -> str:
    s = platform.system() # Linux, Darwin, Windows
    r = platform.release()
    return s+r

def get_computer_name() -> str:
    return platform.node()

def get_user() -> str:
    return getpass.getuser()


if __name__ == '__main__':
    OS = get_OS()
    cname = get_computer_name()
    user = get_user()
    
    print(f"OS is: {OS}")
    print(f"computer name is: {cname}")
    print(f"user name is: {user}")
    
    add_path_from_file(f'library_path_EEG_{cname}.cfg')
    
    formattedLoader(proj_name='EEG', file_format=['proj', 'cname'])
    
    print('will return an error message below')
    formattedLoader(proj_name='EEG', file_format=['no such format'])