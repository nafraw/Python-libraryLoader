# -*- coding: utf-8 -*-
"""
Created on Sun May  2 22:05:38 2021

@author: Ping-Keng Jao

Purpose of file:
    For adding paths from a config file, suitable for lazy persons :)
    
    When to use:
        You have some self developed codes/package that will be used in different projects or machines.
        Your codes are not in the search path nor installed. Then, you will need to add the path manually before running your script.
        However, you will need to have this .py in a searchable folder or the same folder as your script to import and run it.
    
        Scenario 1:
            Running the same project on different machines with different library path.
            The script can run the formattedLoader to load a corresponding config file based on the information of the machine.
            
        Scenario 2:
            You don't want to write so many path information in a .py file when importing.
            Run add_path_from_file() and remember to set verbose=False if wish not to see the info on the terminal.
        
    How should a config file looks like:
        Each line is a path to your library folder. The path can be absolute or relative, depends on your need.
        E.g:
            C:\Python\MyLibraries\tool1
        
"""

import os
import sys
import platform
import getpass

def formattedFileName(prefix='', proj_name='', file_format=['proj', 'OS'], verbose=True):
    # This function will generates a config file name
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
    if verbose:
        print(f'selected config: {filename}')
    return filename
    

def formattedLoader(prefix='library_path', proj_name='', file_format=['proj', 'OS'], priority=1, verbose=True):
    # This function will find a config file and add the written lines as a system path with a high priority
    # config file should be named with at least one of the keyword below:
    # OS, computer name, user, or project name
    # The filename ends with .cfg and a underscore between each keyword above
    # e.g.: {prefix}_{proj}_{OS}.cfg
    filename = formattedFileName(prefix=prefix, proj_name=proj_name, file_format=file_format, verbose=False)
    add_path_from_file(filename, priority=priority, verbose=verbose)

def add_path_from_file(file: str, priority=1, verbose=True):
    with open(file) as f:
        lines = f.read().splitlines()
    print(f'\x1b[42mLoading: {file}\x1b[0m')
    for l in lines:        
        if l not in sys.path: # no need to add multiple times
            if not os.path.isdir(l):
                print(f'\x1b[41mConfig file contains a non-folder line and will be skipped: {l}\x1b[0m')                
                continue
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
    for s in synonym.keys():
        if kl in synonym[s]:
            return s
    # if not found in synonyms, it is an error
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