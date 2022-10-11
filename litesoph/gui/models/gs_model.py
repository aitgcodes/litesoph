from tkinter import messagebox

def choose_engine(input_param:dict):
        basis = input_param.get('basis_type')
        boxshape = input_param.get('box shape')
        if boxshape:
                if basis == "nao":
                        if boxshape == "parallelepiped":
                                engine = "gpaw"
                                return engine
                        else:
                                messagebox.showinfo(message="Not Implemented")
                                return
                if basis == "fd":
                        if boxshape == "parallelepiped":
                                check = messagebox.askyesno(title = 'Message',message= "The default engine for the input is gpaw, please click 'yes' to proceed with it. If no, octopus will be assigned")
                                if check is True:
                                        engine = "gpaw"
                                elif check is False:
                                        engine = "octopus"
                        elif boxshape in ["minimum","sphere","cylinder"] : 
                                engine = "octopus"
                        return engine
        else:
                if basis == "pw":
                        engine = "gpaw"
                elif basis == "gaussian":
                        engine = "nwchem"
                return engine
