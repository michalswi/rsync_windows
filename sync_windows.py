#!/usr/bin/env python

import os
import hashlib
import sys
from multiprocessing import Process, Queue
import time
from shutil import copy2

#windows: without raw string -> error
#dir_base = r'C:\Users\szp\Desktop\backup_files'
#dir_base = r'C:\Users\szp\Desktop\New_folder'
dir_usb = r'E:\backup_files'

dir_base = r'{}'.format(sys.argv[1])
dir_usb = r'{}'.format(sys.argv[2])

def f_base(q):
    """ add local files (as a key) and their checksum (as a value) to dict """
    base_dict = {}
    
	#count should be equal to the number of items in base_dict.
    count = 0
    #https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    for path, dirs, files in os.walk(dir_base):
        for f in files:
            #if os.path.isfile(path + r'\{}'.format(f)):        # windows \
            if os.path.isfile(path + r'/{}'.format(f)):         # linux /
                count += 1
                #with open(path + r'\{}'.format(f), 'rb') as of:
                with open(path + r'/{}'.format(f), 'rb') as of:
                    fc = of.read()
                    #base_dict[path + r'\{}'.format(f)]=( hashlib.md5(fc).hexdigest() )
                    base_dict[path + r'/{}'.format(f)]=( hashlib.md5(fc).hexdigest() )
                    
    print("base dict:", len(base_dict.items()))
    print("base:", count)
    q.put(base_dict)
    

def f_usb(q2):
    """ add usb files (as a key) and their checksum (as a value) to dict """

    usb_dict = {}
    
    #count should be equal to the number of items in base_dict.
    count = 0
    for path, dirs, files in os.walk(dir_usb):
        for f in files:
            if os.path.isfile(path + r'/{}'.format(f)):
                count += 1
                with open(path + r'/{}'.format(f), 'rb') as of:
                    fc = of.read()
                    usb_dict[path + r'/{}'.format(f)]=( hashlib.md5(fc).hexdigest() )
                    
    print("usb dict:", len(usb_dict.items()))
    print("usb:", count)
    q2.put(usb_dict) 


to_be_changed = {}


def compare_dicts():
    """ compare both dictionaries and find updated/new files"""
    
    print("=== start checking ===")
    for key, value in a_usb_dict.items():
        if value not in a_base_dict.values():
            print(key, value)
            to_be_changed[key] = value
    print("=== checked ===")
    
    if to_be_changed:
        return 1
    else:
        return 0

#  SHOULD CHECK IF DIRECTORY EXIST BEFORE COPYING
def update_files():
    
    print("=== updating ===")
    #https://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
    for key, value in to_be_changed.items():
        print(key)
        copy2(key, '/home/miswierc/Desktop/backup_files/')    
    print("=== updated ===")

def fire():
    """ run... """
    global a_base_dict, a_usb_dict
    
    q = Queue()
    q2 = Queue()
    
    p1 = Process(target=f_base, args=(q,))
    p1.start()
    p2 = Process(target=f_usb, args=(q2,))
    p2.start()    
    
    a_base_dict = q.get()
    a_usb_dict = q2.get()
    
    
    p1.join()
    p2.join()
    
    #print(len(a_base_dict))
    #print(len(a_usb_dict))

    #time.sleep(10)
    
    # 'if' statement is needed to not run 'update_files()' if there are no files to be updated
    if compare_dicts():
        update_files()
    else:
        print("=== completed ===")

#https://stackoverflow.com/questions/17927173/collecting-result-from-different-process-in-python
if __name__=='__main__':
    fire()
  
    
