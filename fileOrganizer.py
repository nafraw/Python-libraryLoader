# -*- coding: utf-8 -*-
"""
Created on Sat May  8 14:49:06 2021

@author: Ping-Keng Jao

Purpose of file:
    1. Provide functions to search some files at or under a folder.
    2. Provide a class to organize files saved for different purposes at different folders (or even at different machines)
        a. For different machines, the class can automatically load a config with only a few parameters given.
        b. For different purposes, the class can easily retrieve related files by using the get_files function.
    
"""


import os
import re
from natsort import natsorted
from libraryLoader import formattedFileName

def search_files_from_root_folder(root, expression, verbose=False):
    # using regular expression to search all files at and below the root folder
    files_matched = []
    for path_folder, subfolder, files in os.walk(root):
        for f in files:
            match = re.search(expression, f)
            if match:
                to_add = os.path.join(path_folder, f)
                files_matched.append(to_add)
                if verbose:
                    print('match: ', to_add)
    files_matched = natsorted(files_matched)
    return files_matched

def search_files_at_root_folder(root, expression, verbose=False):
    # using regular expression to search all files at the root folder
    files_matched = []
    for f in os.listdir(root):
        match = re.search(expression, f)
        if match:
            to_add = os.path.join(root, f)
            files_matched.append(to_add)
            if verbose:
                print('match: ', to_add)
    files_matched = natsorted(files_matched)
    return files_matched


class FileOrganizer:
    def __init__(self, name_config=None, root_path='.', proj_name='', file_format=['proj', 'cname'], verbose=True):
        self.config = name_config
        self.paths = {}
        if name_config:
            self.load_config(name_config)
        else:
            self.load_config_with_formatted_name(root_path, proj_name, file_format, verbose)
    
    def load_config_with_formatted_name(self, root_path='.', proj_name='', file_format=['proj', 'cname'], verbose=True):
        name_config = formattedFileName(prefix='data_path', proj_name=proj_name, file_format=file_format, verbose=verbose)
        self.load_config(os.path.join(root_path, name_config))
    
    def load_config(self, config):
        print(f'Loading config: {config}')
        self.config = config
        with open(config) as f:
            lines = f.read().splitlines()
        for i in range(0, len(lines), 5):
            name_purpose = lines[i]
            root_path = lines[i+1]
            prefix = lines[i+2]
            postfix = lines[i+3]
            ext = lines[i+4]
            self.add_path(name_purpose, root_path, prefix, postfix, ext)            
    
    def add_path(self, name_purpose, root_path, prefix='', postfix='', ext=''):
        if ext[0] == '.':
            ext = '\\' + ext
        elif ext[0] != '\\':
            ext = '\.' + ext
        self.paths[name_purpose] = (root_path, prefix, postfix, ext)
    
    def get_files(self, name, only_at_root=False, verbose=False):
        root_path, prefix, postfix, ext = self.paths[name]
        expression = prefix + '.*' + postfix + ext
        if only_at_root:
            files_matched = search_files_at_root_folder(root_path, expression, verbose)
        else:
            files_matched = search_files_from_root_folder(root_path, expression, verbose)
        return files_matched
    
    def get_name(self, name, filename, delimiter=''):
        root_path, prefix, postfix, ext = self.paths[name]
        fn = prefix + delimiter + filename + delimiter + postfix + ext[1:] # to skip the '\\' char
        return os.path.join(root_path, fn)
    
    def __getitem__(self, name):
        return self.paths[name]
    
if __name__ == '__main__':    
    fo = FileOrganizer('./data_path_EEG_G20-PK.cfg')
    fo.load_config_with_formatted_name(proj_name='EEG')
    files = fo.get_files('high lv')
    print(files)
    print(fo.get_name('high lv', 'testname', '_'))