"""
Litesoph File Management  

Available tags:
----------------
file_relevance: <very_impt, impt, least_impt>
file_type: <'redirected_outfile','scipt_generated_outfile','input_file','property_file','checkpoint_file' > 
transfer_method: <method :'direct_transfer','compress_transfer','split_transfer', 'compress_method','split_size'>
"""

# dictionary of available compression algorithm used in litesoph file management module
compression_algo_dict={'lz4':'.lz4', 'zstd':'.zst', 'lzop':'.lzo', 'gzip':'.gz', 'bzip2':'.bz2','p7zip':'.7z',
            'xz':'.xz','pigz':'.gz','plzip':'.lz','pbzip2':'.bz2','lbzip2':'.bz2'}


# list of Tags
very_impt=['.out','.xyz','.sh','.py', '.nwi']
impt=[]
least_impt=[]

input_file=['.xyz','.sh','.py', '.nwi']
redirected_outfile=['.log']
script_generated_outfile=['.nwo','.gpw','.out']
property_file=['.dat']
checkpoint_file=['.db','.movecs','gridpts.0']

direct_transfer=['.out','.log','.xyz','.sh','.py', '.nwi']
compress_transfer=[]
split_transfer=[]

list_of_files=[very_impt,impt,least_impt,input_file,redirected_outfile,script_generated_outfile,property_file,
checkpoint_file,direct_transfer,compress_transfer,split_transfer]

List_set_of_files = list({i for lst in list_of_files for i in lst})

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = {}
    dict[key] = value

def lfm_file_info_dict():
    """
    function to generate a dictionary database of containing metadata information of all the possible files
    """

    lfm_file_info={}

    for file in List_set_of_files:
        if file not in lfm_file_info:
            lfm_file_info[file] = {}

        if (file in very_impt):
            add_element(lfm_file_info[file], 'file_relevance', 'very_impt')
        elif (file in impt):
            add_element(lfm_file_info, 'file_relevance', 'impt')
        elif (file in least_impt):
            add_element(lfm_file_info, 'file_relevance', 'least_impt')
        else:
            add_element(lfm_file_info, 'file_relevance',None)
      
        if (file in input_file):
            add_element(lfm_file_info[file], 'file_type', 'input_file')
        elif (file in redirected_outfile):
            add_element(lfm_file_info[file], 'file_type', 'redirected_outfile')
        elif (file in script_generated_outfile):
            add_element(lfm_file_info[file], 'file_type', 'script_generated_outfile')
        elif (file in property_file):
            add_element(lfm_file_info[file], 'file_type', 'property_file')
        elif (file in checkpoint_file):
            add_element(lfm_file_info[file], 'file_type', 'checkpoint_file')
        else:
            add_element(lfm_file_info[file], 'file_type', None)
                
        if (file in direct_transfer):
            add_element(lfm_file_info[file], 'transfer_method', 'direct_transfer')
        elif (file in compress_transfer):
            add_element(lfm_file_info[file], 'transfer_method', 'compress_transfer')
        elif (file in split_transfer):
            add_element(lfm_file_info[file], 'transfer_method', 'split_transfer')
        else:
            add_element(lfm_file_info[file], 'transfer_method', None)

    return lfm_file_info

if __name__ == "__main__":
    lfm_file_info_dict()

def keys_exists(dictionary, keys):
    nested_dict = dictionary

    for key in keys:
        try:
            nested_dict = nested_dict[key]
        except KeyError:
            return False
    return True

result = keys_exists(lfm_file_info_dict(), ['x'])
print(result)



# print(lfm_file_info_dict())

# lfm_file_info={ 
#                 '.out':{'file_relevance':'very_impt','file_type':'', 'transfer_method':{'method':'compress_transfer','compress_method':'zstd','split_size':'500k'}},
#                 '.log':{'file_relevance':'very_impt','transfer_method':{'method':'direct_transfer','compress_method':'zstd','split_size':''}},
#                 '.cube':{'file_relevance':'very_impt','transfer_method':{'method':'compress_transfer','compress_method':'zstd','split_size':''}},
#                 '.ulm':{'file_relevance':'very_impt','transfer_method':{'method':'split_transfer','compress_method':'zstd','split_size':'200M'}},
#                  }

# from pathlib import Path
# import glob
# import os

# dir_path='/home/anandsahu/myproject/aitg/ls/sample_ls_project/RuntimeQuery'

# res = []
# # Iterate directory
# for path in os.listdir(dir_path):
#     # check if current path is a file
#     if os.path.isfile(os.path.join(dir_path, path)):
#         res.append(path)
# # print(res)

# from os import walk

# # list to store files name
# res = []
# for (dir_path, dir_names, file_names) in walk(dir_path):
#     res.extend(file_names)
# print(res)

# s = set(res)
# print(s)
