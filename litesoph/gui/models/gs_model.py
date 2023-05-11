from tkinter import messagebox

def choose_engine(input_param:dict):
    # for basis_key in ['basis_type:common','basis_type:extra']:
    for basis_key in ['basis_type']:
        if input_param.get(basis_key) is not None:                        
            basis = input_param.get(basis_key)
    if basis is None:
        raise KeyError("No match for basis key")

    boxshape = input_param.get('boxshape')
    if boxshape:
        if basis == "lcao":
            if boxshape == "parallelepiped":
                engine = "gpaw"
                return engine
            else:
                messagebox.showinfo(message="Not Implemented")
                return
        if basis == "fd":
            if boxshape == "parallelepiped":
                check = messagebox.askyesno(title = 'Message',message= "The default engine for the input is Octopus, please click 'yes' to proceed with it. If no, GPAW will be assigned")
                if check is True:
                    engine = "octopus"
                elif check is False:
                    engine = "gpaw"
            elif boxshape in ["minimum","sphere","cylinder"] : 
                engine = "octopus"
            return engine
    else:
        if basis == "pw":
            engine = "gpaw"
        elif basis == "gaussian":
            engine = "nwchem"
            return engine

def get_inp_summary(gui_input:dict):
        pass