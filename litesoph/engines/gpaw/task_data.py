from litesoph.common.data_sturcture.data_types import DataTypes as DT

gpaw_gs_param_data ={ 
        "xc": {'type':DT.string, 'values':["LDA",
                                            "PBE",
                                            "PBE0",
                                            "PBEsol",
                                            "BLYP",
                                            "B3LYP",
                                            "CAMY-BLYP",
                                            "CAMY-B3LYP"], 
                                            'default_value': 'LDA'},               
        "basis_type": {'type':DT.string, 'values':['lcao',
                                                     'fd', 
                                                     'pw'], 
                                                     'default_value': 'lcao'},  
        "basis": {'type':DT.string, 'metadata':{'basis_type': {'lcao' : {'values':["dzp","sz","dz","szp","pvalence.dz"], 'default_value': 'dzp'},
                                                'fd' : {'default_value': None},
                                                'pw': {'default_value': None}}}},  
        "bands": 0,
        "spin": None,
        "spacing": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
        "vacuum": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
        "boxshape": {'type':DT.string, 'values':['parallelepiped'], 'default_value':'parallelepiped'},
        "box_dim" : None,        
        "max_iter":{'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
        "energy_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7} ,
        "density_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6} ,
        "smearing_fun":{'type':DT.string, 'values':["","improved-tetrahedron-method","tetrahedron-method","fermi-dirac","marzari-vanderbilt",], 'default_value': ''},
        "smearing_width": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.0},
        "mixing": None,
        
}


