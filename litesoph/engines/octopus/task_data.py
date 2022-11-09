from litesoph.common.data_sturcture.data_types import DataTypes as DT

xc_pseudo = {
    "lda":["lda_x + lda_c_pz_mod", "standard"],
    "pbe":["gga_x_pbe + gga_c_pbe", "pseudodojo_pbe"],
    "pbe0":[["hyb_gga_xc_pbeh","hyb_gga_xc_pbe0_13","hyb_gga_xc_pbe50"], None],
    "pbesol":["hyb_gga_xc_pbe_sol0", None],
    "blyp":[None, None],
    "b3lyp":[["hyb_gga_xc_b3lyp","hyb_gga_xc_mb3lyp_rc04","hyb_gga_xc_revb3lyp","hyb_gga_xc_b3lyps","hyb_gga_xc_b3lyp5"], None],
    "camy-blyp":["hyb_gga_xc_camy_blyp", None],
    "camy-b3lyp":["hyb_gga_xc_camy_b3lyp", None],
    "pw91":[["gga_x_pw91 + gga_c_pw91","gga_x_mpw91 + gga_c_pw91"], None],
    "cam-b3lyp":["hyb_gga_xc_cam_b3lyp", None],
    "lc-wpbe":[None, None],
    "hse03":["hyb_gga_xc_hse03", None],
    "hse06":["hyb_gga_xc_hse06", None],
}

ground_state = {
    "units": None,
    "charge":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.0},
    "multiplicity":{'type':DT.integer, 'min': None, 'max': None, 'default_value':1}, # dependency on charge, spin, extra states/bands
    "xc": {'type':DT.string, 'values':["LDA","PBE","PBE0","PBEsol","BLYP","B3LYP","CAMY-BLYP",
                                        "CAMY-B3LYP","PW91","CAM-B3LYP","LC-wPBE","HSE03","HSE06"], 
                            'default_value': 'LDA'},               
    "basis_type": {'type':DT.string, 'values':['fd'], 'default_value': 'fd'},  
    "basis": None,  
    "bands": {'type':DT.integer, 'min': None, 'max': None, 'default_value': 0},
    "spin": {'type':DT.string, 'values':['unpolarized', 'polarized'], 'default_value':'unpolarized'},
    "spacing": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
    "vacuum": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 6},
    "boxshape": {'type':DT.string, 'values':["parallelepiped", "sphere", "cylinder","minimum"], 'default_value':"minimum"},
    "box_dim" : {'type':None,
                'metadata':{
                        'parallelepiped':{
                            "xlength":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
                            "ylength":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
                            "zlength":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12}},
                        'sphere':{
                            "radius":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12}},
                        'cylinder':{
                            "xlength":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12},
                            "radius":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12}},
                        'minimum':{
                            "radius":{'type':DT.decimal, 'min': None, 'max': None, 'default_value': 12}}
                        },},      
    "max_iter":{'type':DT.integer, 'min': None, 'max': None, 'default_value': 300},
    "energy_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 5.0e-7} ,
    "density_conv": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 1e-6} ,
    "smearing_fun":{'type':DT.string, 'values':["semiconducting","fermi_dirac","cold_smearing","methfessel_paxton","spline_smearing",], 'default_value':"semiconducting"},
    "smearing_width": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.1},
    "mixing": {'type':DT.decimal, 'min': None, 'max': None, 'default_value': 0.3},
    }

time_dependent = {

}    