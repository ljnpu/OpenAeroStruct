from openmdao.api import Group
from openaerostruct.aerodynamics.assemble_aic import AssembleAIC
from openaerostruct.aerodynamics.circulations import Circulations
from openaerostruct.aerodynamics.forces import Forces

class VLMStates(Group):
    """ Group that contains the aerodynamic states. """

    def __init__(self, surfaces):
        super(VLMStates, self).__init__()

        tot_panels = 0
        for surface in surfaces:
            ny = surface['num_y']
            nx = surface['num_x']
            tot_panels += (nx - 1) * (ny - 1)

        self.add_subsystem('assembly',
                 AssembleAIC(surfaces=surfaces),
                 promotes=['*'])
        self.add_subsystem('circulations',
                 Circulations(tot_panels=tot_panels),
                 promotes=['*'])
        self.add_subsystem('forces',
                 Forces(surfaces=surfaces),
                 promotes=['*'])