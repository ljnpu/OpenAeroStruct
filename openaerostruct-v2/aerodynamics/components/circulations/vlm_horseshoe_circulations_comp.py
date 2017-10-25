from __future__ import print_function
import numpy as np
from scipy.linalg import lu_factor, lu_solve
from scipy.sparse import csc_matrix

from openmdao.api import ExplicitComponent


class VLMHorseshoeCirculationsComp(ExplicitComponent):

    def initialize(self):
        self.metadata.declare('lifting_surfaces', type_=list)

    def setup(self):
        lifting_surfaces = self.metadata['lifting_surfaces']

        system_size = 0

        for lifting_surface_name, lifting_surface_data in lifting_surfaces:
            num_points_x = lifting_surface_data['num_points_x']
            num_points_z = 2 * lifting_surface_data['num_points_z_half'] - 1

            system_size += (num_points_x - 1) * (num_points_z - 1)

        self.system_size = system_size

        self.add_input('circulations', shape=system_size)
        self.add_output('horseshoe_circulations', shape=system_size)

        data = [np.ones(system_size)]
        rows = [np.arange(system_size)]
        cols = [np.arange(system_size)]

        ind_1 = 0
        ind_2 = 0
        for lifting_surface_name, lifting_surface_data in lifting_surfaces:
            num_points_x = lifting_surface_data['num_points_x']
            num_points_z = 2 * lifting_surface_data['num_points_z_half'] - 1
            num = (num_points_x - 1) * (num_points_z - 1)

            ind_2 += num

            arange = np.arange(num).reshape((num_points_x - 1), (num_points_z - 1))

            data_ = -np.ones((num_points_x - 2) * (num_points_z - 1))
            rows_ = ind_1 + arange[1:, :].flatten()
            cols_ = ind_1 + arange[:-1, :].flatten()

            data.append(data_)
            rows.append(rows_)
            cols.append(cols_)

            ind_1 += num

        data = np.concatenate(data)
        rows = np.concatenate(rows)
        cols = np.concatenate(cols)

        self.mtx = csc_matrix((data, (rows, cols)), shape=(system_size, system_size))

        self.declare_partials('horseshoe_circulations', 'circulations', val=data, rows=rows, cols=cols)

    def compute(self, inputs, outputs):
        outputs['horseshoe_circulations'] = self.mtx.dot(inputs['circulations'])
