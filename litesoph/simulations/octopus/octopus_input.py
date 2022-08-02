
kw_types={"str": [ "FromScratch" ,"CalculationMode","UnitsOutput", 
            "ExperimentalFeatures","Spacing","BoxShape","Radius","Xlength","PseudopotentialSet",
            "ExtraStates","ExcessCharge","SpinComponents","Mixing",
            "MaximumIter","Eigensolver","Smearing","SmearingFunction",
            "ConvRelDens","ConvEnergy","ConvAbsEv","ConvRelEv","ConvAbsDens","TDPropagator","TDMaxSteps","TDTimeStep",
            "TDDeltaStrength","TDPolarizationDirection","TDOutputComputeInterval", "ParStates",
            "PropagationSpectrumEnergyStep","PropagationSpectrumMaxEnergy", "PropagationSpectrumMinEnergy"],
        "quoted_str": ["WorkDir","XYZCoordinates"],
        "boolean": [],
        "flag": ["XCFunctional"],
        "block": ["LSize","TDExternalFields","TDFunctions","TDPolarization", "TDOutput"]
}

block_types = {
            "calc":["WorkDir", "FromScratch" ,"CalculationMode"],
            "common": ["XYZCoordinates","UnitsOutput","ExperimentalFeatures","Spacing","BoxShape","Radius","Xlength", "LSize"],
            "scf":["Mixing","MaximumIter","Eigensolver","Smearing","SmearingFunction","ConvRelDens","ConvAbsDens","ConvAbsEv","ConvRelEv","ConvEnergy"],
            "states": ["ExtraStates","ExcessCharge","SpinComponents"],
            "xc_pseudo":["XCFunctional","PseudopotentialSet"],
            "td":["TDPropagator","TDMaxSteps","TDTimeStep"],
            "td_delta":["TDDeltaStrength","TDPolarizationDirection", "TDPolarization"],
            "td_laser": ["TDExternalFields","TDFunctions"],
            "td_out": ["TDOutput","TDOutputComputeInterval", "ParStates"],
            "spectrum": ["UnitsOutput", "PropagationSpectrumEnergyStep", 
            "PropagationSpectrumMaxEnergy", "PropagationSpectrumMinEnergy"]
            }

task_types = {
"ground_state": ["calc","common","scf","states","xc_pseudo"],
"unocc": ["calc","common","scf","states","xc_pseudo"],
"rt_tddft_delta": ["calc","common","states", "td", "td_delta", "td_out"],
"rt_tddft_laser": ["calc","common", "td", "td_laser", "td_out"],
"spectrum": ["spectrum"]
}

def key_value2line(key,value):
    """ ABC = abc"""

    line = []
    line.append('{} = {}'.format(key, value))
    return line

def key_value2str(key, value):
    """ ABC = 'abc' """

    line = []
    line.append('{} = "{}"'.format(key, value))
    return line

def list2sums(key, values:list):
    """ ABC = a + b + c """

    lines = []
    sum_string = ' ' + ' + '.join(str(value) for value in values)
    lines = key_value2line(key, sum_string)
    return lines
    
def list2block(name, rows:list):
    """Construct 'block' of Octopus input.

    convert a list of rows to a string with the format x | x | ....
    for the octopus input file"""

    lines = []
    lines.append('%' + name)
    for row in rows:
        lines.append(' ' + ' | '.join(str(obj) for obj in row))
    lines.append('%')

    return lines 

def format_lines(inp_dict:dict):
    """ formats lines from input dictionary structure"""

    func_types = {
        "str": key_value2line,
        "quoted_str": key_value2str,
        "boolean": key_value2line,
        "flag": list2sums,
        "block": list2block
    }

    lines = []
    for key, value in inp_dict.items():
        for k,v in kw_types.items():
            if key in v:
                type = k
       
        # if isinstance(value, tuple):
        #     try:
        #         var_value = value[0]
        #         var_dict = value[1]
        #     except IndexError:
        #         var_dict = []
        #     _line = func_types.get(type, key_value2line)(key, var_value)
        #     lines.extend(_line) 
        #     lines.extend(format_lines(var_dict)) 
        if isinstance(value, dict):
            try:
                var_value = value["name"]
                var_dict = value["param"]
            except IndexError:
                var_dict = []
            _line = func_types.get(type, key_value2line)(key, var_value)
            lines.extend(_line) 
            lines.extend(format_lines(var_dict))
        else:          
            value = value
            _line = func_types.get(type, key_value2line)(key, value)
            lines.extend(_line) 
    return lines 
                
def get_dependent_features(property_name):
    """Returns the dependent features(expt) corresponding to the property"""

    td_output = [("energy", "no"),
            ("multipoles", "no"),
            ("td_occup", "yes")]  
        
    for item in td_output:
        if item[0] == property_name:
            return item[1] 

def validate_gs_input(inp_dict:dict):
    pass

def validate_td_delta_input(inp_dict:dict):

    def check_property_dependency(property_list:list):
        """ Checks property dependency w/ ExptFeatures option"""

        for property in property_list:
            expt = get_dependent_features(property)   
            if expt == 'yes':
                value = expt
                break
            else:
                value = 'no'
        inp_dict["ExperimentalFeatures"] = value

        for property in property_list:
            if property == 'td_occup':
                inp_dict["ParStates"] = 'no'

    td_output_list = inp_dict.get("TDOutput", [["energy"], ["multipoles"]])
    # inp_dict["TDOutput"] = td_output_list

    _list = []  
    for item in td_output_list:
        _list.extend(item)
    _list.append(item for item in td_output_list)    

    check_property_dependency(_list) 

def validate_td_laser_input(inp_dict:dict):
    pass

def validate_spec_input(inp_dict:dict):
    pass

def get_block_dict(inp_dict:dict, block_name:str):
    """ Reads the input dictionary and returns the matched key-values for particular block type"""

    kw_list = block_types.get(block_name)

    block_dict = {}
    for key, value in inp_dict.items():        
        if key in kw_list:
            block_dict[key] = value

    return block_dict        

def get_task(inp_dict:dict):
    """ Returns the type of task to be performed """

    rt_tddft_delta = ["TDDeltaStrength"]
    rt_tddft_laser = ["TDExternalFields", "TDFunctions"]
    spectrum = ["PropagationSpectrumEnergyStep", 
            "PropagationSpectrumMaxEnergy", "PropagationSpectrumMinEnergy"]

    calc_mode = inp_dict.get("CalculationMode", "gs")
    gs_mode = (calc_mode == "gs")
    td_mode = (calc_mode == "td")   

    if gs_mode:
        if all(kw in inp_dict.keys() for kw in spectrum ):
            task = "spectrum"
        else:
            task = "ground_state"

    if td_mode:        
        if all(kw in inp_dict.keys() for kw in rt_tddft_delta ):
            task = "rt_tddft_delta"              
        elif all(kw in inp_dict.keys() for kw in rt_tddft_laser):
            task = "rt_tddft_laser" 
    
    return task
    

def generate_input(inp_dict:dict, check = True):
    """ Reads master dictionary, decides and returns the template format"""
        
    # gets task_name from inp_dict
    task = get_task(inp_dict)

    validate_func ={
        "ground_state": validate_gs_input,
        "unocc": validate_gs_input,
        "rt_tddft_delta": validate_td_delta_input,
        "rt_tddft_laser": validate_td_laser_input,
        "spectrum": validate_spec_input
    }
    
    validate_func.get(task)(inp_dict)
    list_of_blocks = task_types.get(task, [])

    lines = []
    if check:
        for block in list_of_blocks:
            block_dict = get_block_dict(inp_dict, block)
            _lines = format_lines(block_dict)
            lines.extend(_lines)
    else:
        _lines = format_lines(inp_dict) 
        lines.extend(lines)   

    _lines = """\n""".join(lines)

    return _lines    
