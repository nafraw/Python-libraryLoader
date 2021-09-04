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
from typing import List
from natsort import natsorted
from libraryLoader import formattedFileName
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

def filesep(fullname):
    dirname = os.path.dirname(fullname)
    filename = os.path.basename(fullname)
    filename, ext = os.path.splitext(filename)
    return dirname, filename, ext

def get_file_begin_with(flist: [], prefix: List[str]):
    # can be used for example to screen out files begin with one or a list of targeted subject ID
    flist_screened = []
    assert(isinstance(prefix, list))
    for f in flist:
        _, file_name, _ = filesep(f)
        for p in prefix:
            n = len(p)
            if file_name[0:n] == p:
                flist_screened.append(f)        
    return flist_screened

def remove_target_str(name: str, target_str) -> str:
    if isinstance(target_str, str):
        target_str = [target_str]
    for target in target_str:
        idx = name.find(target)
        l = len(target)
        if idx > -1:
            name = name[: idx] + name[idx+l: ]
    return name

def make_folder_if_necessary(filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except FileExistsError:            
            pass # directory already exists by maybe other threads or programs

def save_data_as_file(filename, **kwargs):
    saved_vars = {}
    if filename[-4:] != '.pkl':
        print(f'adding extension (.pkl) to {filename}')
        filename += '.pkl'        
    for key, value in kwargs.items():
        saved_vars[key] = value
    make_folder_if_necessary(filename)
    with open(filename, 'wb') as f:  # Overwrites any existing file.
        pickle.dump(saved_vars, f, pickle.HIGHEST_PROTOCOL)

def load_data_file(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data

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
        keywords = ['name_purpose', 'root_path', 'prefix', 'postfix', 'ext']
        d = {}
        count = 0
        for l in lines:         
            if len(l) > 0 and l[0] == '#': # begin with a comments, skip this line
                continue
            idx_comment = str.find(l, '#') # remove strings from the # symbol
            if idx_comment != -1:
                l = l[0: idx_comment]
            l = l.rstrip() # remove white space at the end
            d[keywords[count]] = l
            count += 1
            if count == 5:
                self.add_path(**d)
                count = 0
        ''' old way to read a config file without comments
        for i in range(0, len(lines), 5):
            name_purpose = lines[i]
            root_path = lines[i+1]
            prefix = lines[i+2]
            postfix = lines[i+3]
            ext = lines[i+4]
            self.add_path(name_purpose, root_path, prefix, postfix, ext)        
        '''
    
    def add_path(self, name_purpose, root_path, prefix='', postfix='', ext=''):        
        self.paths[name_purpose] = (root_path, prefix, postfix, ext)
    
    def get_full_path(self, name_purpose, folder_name, filename):
        name_set = self.paths[name_purpose]
        full_filename = filename
        if name_set[1] != '':
            full_filename = name_set[1] + '_' + full_filename
        if name_set[2] != '':
            full_filename += '_' + name_set[2]
        full_filename += '.' + name_set[3]
        full_path = os.path.join(name_set[0], folder_name, full_filename)
        return full_path
    
    def get_files(self, name, only_at_root=False, verbose=False):
        root_path, prefix, postfix, ext = self.paths[name]
        if ext[0] == '.':
            ext = '\\' + ext
        elif ext[0] != '\\':
            ext = '\.' + ext
        if prefix.strip() == '':
            expression = '.*' + postfix + ext
        else:
            expression = '^' + prefix + '.*' + postfix + ext
        if only_at_root:
            files_matched = search_files_at_root_folder(root_path, expression, verbose)
        else:
            files_matched = search_files_from_root_folder(root_path, expression, verbose)
        return files_matched
    
    def get_name(self, name, filename, use_prefix=False, delimiter=''):
        root_path, prefix, postfix, ext = self.paths[name]
        if use_prefix:
            fn = prefix + delimiter + filename + delimiter + postfix + ext[1:] # to skip the '\\' char
        else:
            fn = filename + delimiter + postfix + ext[1:] # to skip the '\\' char
        return os.path.join(root_path, fn)
    
    def __getitem__(self, name):
        return self.paths[name]
    
if __name__ == '__main__':    
    fo = FileOrganizer('./data_path_sample.cfg')
    fo.load_config_with_formatted_name(proj_name='sample', file_format=['proj'])
    files = fo.get_files('prog')
    print('----Listing all exe that has prefix---')
    print(files)
    print('----Listing all exe that begin with install or uninstall---')
    flist = get_file_begin_with(files, ['install', 'uninstall'])
    print(flist)
    print(fo.get_name('prog', 'testname', '_'))