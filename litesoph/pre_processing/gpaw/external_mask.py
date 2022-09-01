from litesoph.pre_processing.gpaw.masking import Mask
from gpaw.external import ExternalPotential

import numpy as np
from ase.units import Bohr, Hartree


class MaskedElectricField(ExternalPotential):

    def __init__(self, strength, direction=[0, 0, 1], tolerance=1e-7,mask=None):

        """External constant electric field.
        strength: float
            Field strength in V/Ang.
        direction: vector
            Polarisation direction.
        """

        d_v = np.asarray(direction)
        self.field_v = strength * d_v / (d_v**2).sum()**0.5 * Bohr / Hartree
        self.tolerance = tolerance
        self.name = 'ConstantElectricField'

        self.masked = False
        self.mask = None
        self.vext_g = None


        if mask is not None:
           self.masked = True
           self.mask = Mask(mask)
#           self.mask = mask['sw']
#           self.masktype = mask['type']
#           self.maskparams = mask['params']
#           self.maskbound = mask['bound']

    def __str__(self):

        return ('Masked electric field: '
                '({:.3f}, {:.3f}, {:.3f}) V/Ang'
                .format(*(self.field_v * Hartree / Bohr)))


    def calculate_potential(self, gd):

        # Currently skipped, PW mode is periodic in all directions

        # d_v = self.field_v / (self.field_v**2).sum()**0.5

        # for axis_v in gd.cell_cv[gd.pbc_c]:

        #     if abs(np.dot(d_v, axis_v)) > self.tolerance:

        #         raise ValueError(

        #             'Field not perpendicular to periodic axis: {}'

        #             .format(axis_v))


        if self.masked and self.vext_g is None:
           self.maskgd = self.mask.create(gd)    

        center_v = 0.5 * gd.cell_cv.sum(0)
        r_gv = gd.get_grid_point_coordinates().transpose((1, 2, 3, 0))
        self.vext_g = np.dot(r_gv - center_v, self.field_v)

        if self.masked:
           self.vext_g = np.multiply(self.maskgd,self.vext_g)
