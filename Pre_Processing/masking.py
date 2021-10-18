"""
Different kinds of masking functions to be used with laser pulses.
"""

import numpy as np
from ase.units import Bohr

###########################
# Main class
###########################

class Mask:
   """
       Defines the mask functions with laser pulses and related methods
       Input requires a dictionary with the following:
       Type: "None" or "Plane" or "Sphere"
             "Plane" - refers to the use of a diving plane to define
                     the mask. The plane can currently be only
                     perpendicular to one of the cartesian axes given by 
                     "Axis" and located at "X0". For X < X0, the region is
                     illuminated while for X >= X0 it is not.
              "Sphere" - refers to the use of a spherical region to illuminate
       Axis: 0,1 or 2. Refers to the cartesian axes to which the dividing plane
                     is perpendicular
       X0  : (float)     Refers to the location of the dividing plane (in cell parameter
                     units).
       Radius: (float) Refers to radius (in Angstroms) of the spherical region to be illuminated
       Centre: (float list) Refers to coordinates (in cell parameter units) of the centre
                     of the Sphere used
       Boundary: "Abrupt" or "Smooth"
              "Abrupt" - refers to an abrupt division of cell i.e. using a Heaviside function
              "Smooth" - refers to the boundary region being defined through an error function
       Rsig: (float)   Refers to sigma (in Angstroms) of the error function to be used.              
   """

   def __init__(self, mask):

        if not mask:
                self.Type="None"
        else:
                keys = list(mask)
                if "Type" not in keys:
                        self.Type = "None"
                else:
                        if mask["Type"] == "Plane":
                             self.Type = "Plane"
                             self.X0 = 0.5
                             self.Axis = 0
                             if "X0" in keys:
                                     self.X0 = mask["X0"]
                             if "Axis" in keys:
                                     self.Axis = mask["Axis"]
                        elif mask["Type"] == "Sphere":
                             self.Type = "Sphere"
                             self.Radius = 0.0 
                             self.Centre = [0.5, 0.5, 0.5]
                             if "Radius" in keys:
                                     self.Radius = mask["Radius"]/Bohr 
                             if "Centre" in keys:
                                     self.Centre = mask["Centre"]

                self.Boundary = "Abrupt"
                if "Boundary" in keys:
                        self.Boundary = mask["Boundary"]
                        if mask["Boundary"] == "Smooth":
                                self.Rsig = 1.0 ## Default is 1.0 Bohr
                                if "Rsig" in keys:
                                        self.Rsig = mask["Rsig"]/Bohr

   def eligible(self,v,acell):

        from scipy.special import erfc 
        eps = 1.e-6
        fval = 0.0

        if self.Type == "Plane":
                x0 = acell[self.Axis]*self.X0
                if self.Boundary == "Abrupt" and v[self.Axis] < x0:
                        fval = 1.0       
                elif self.Boundary == "Smooth":
                        #rsig = acell[self.Axis]*self.Rsig
                        rsig = self.Rsig 
                        x = (v[self.Axis]-x0)/np.sqrt(2.0)/rsig
                        fval = 0.5*erfc(x)

        elif self.Type == "Sphere":
                r0 = self.Radius
                centre = self.Centre*acell
                vd = v - centre
                r = np.sqrt(np.dot(vd,vd))              
                if self.Boundary == "Abrupt" and r < r0:
                        fval = 1.0
                elif self.Boundary == "Smooth":
                        #rsig = acell[self.Axis]*self.Rsig
                        rsig = self.Rsig 
                        x = (r-r0)/rsig/np.sqrt(2.0)
                        fval = 0.5*erfc(x)

        else:
                fval = 1.0

        return fval
                     
   def create(self,gd):
       
        n_c = gd.n_c

        if self.Type == "None":
           mfn = np.ones(n_c, dtype="float")
           return mfn

        mfn = np.zeros(n_c, dtype="float")
        for i in range(n_c[0]):
                x = (i + gd.beg_c[0]) * gd.h_cv[0, 0]
                for j in range(n_c[1]):
                        y = (j + gd.beg_c[1]) * gd.h_cv[1, 1]
                        for k in range(n_c[2]):              
                                z = (k + gd.beg_c[2]) * gd.h_cv[2, 2]
                                mfn[i,j,k] = self.eligible([x,y,z],gd.cell_cv.diagonal())

        return mfn
