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
####################

# file_relevance
very_impt=['.out','.log','.xyz','.sh','.py', '.nwi']
impt=['.dat','.db','.movecs','gridpts.0']
least_impt=[]

#file_type
input_file={'.xyz':{'subfiletype':'coordinate_file'},'.sh':{'subfiletype':'bash_file'},'.py':{'subfiletype':None}, '.nwi':{'subfiletype':None}}
redirected_outfile=['.log']
script_generated_outfile=['.nwo','.gpw','.out']
checkpoint_file=['.db','.movecs','gridpts.0']

##############################################
input_script_file=['.nwi']
property_file=['.dat']
coordinate_file=['coordinate.xyz','*.xyz']
dipole_file=['dm*.dat','multipoles*','dm_masked*']
energy_coupling=['energy_coupling*.dat']
spectrum_file=['spec*.dat']
script_output_file=['g*.out','g.nwo','*.txt']

# add the filetype to the dictionary 
file_type_combobox={'coordinate_file':coordinate_file,'dipole_file':dipole_file,'energy_coupling':energy_coupling,'spectrum_file':spectrum_file,'script_output_file':script_output_file,'input_script_file':input_script_file}
##############################################

#transfer_method
direct_transfer=['.out','.log','.xyz','.sh','.py', '.nwi']
compress_transfer={'.dat':{'compress_method':None},'.cube':{'compress_method':None} }
split_transfer={'.test':{'split_size':None}}

list_of_files=[very_impt,impt,least_impt,input_file,redirected_outfile,script_generated_outfile,property_file,
checkpoint_file,direct_transfer,compress_transfer,split_transfer]

List_set_of_files = list({i for lst in list_of_files for i in lst})

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = {}
    dict[key] = value

def keys_exists(dictionary, keys):
    nested_dict = dictionary

    for key in keys:
        try:
            nested_dict = nested_dict[key]
        except KeyError:
            return False
    return True
    
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
            add_element(lfm_file_info[file], 'file_relevance', 'impt')
        elif (file in least_impt):
            add_element(lfm_file_info[file], 'file_relevance', 'least_impt')
        else:
            add_element(lfm_file_info[file], 'file_relevance',None)

        if (file in input_file):
            add_element(lfm_file_info[file], 'file_type', 'input_file')
            add_element(lfm_file_info[file], 'subfiletype', input_file[file]['subfiletype'])

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
                        
        if (file in compress_transfer):
            add_element(lfm_file_info[file], 'transfer_method', 'compress_transfer')
            add_element(lfm_file_info[file], 'compress_method', compress_transfer[file]['compress_method'])
        elif (file in split_transfer):
            add_element(lfm_file_info[file], 'transfer_method', 'split_transfer')
            add_element(lfm_file_info[file], 'split_size', split_transfer[file]['split_size'])
        else:
            add_element(lfm_file_info[file], 'transfer_method', 'direct_transfer')
    return lfm_file_info

if __name__ == "__main__":
    lfm_file_info_dict()