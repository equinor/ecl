#  Copyright (C) 2014  Equinor ASA, Norway.
#
#  The file 'fault_block_layer.py' is part of ERT - Ensemble based Reservoir Tool.
#
#  ERT is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
#  for more details.

from __future__ import print_function
from cwrap import BaseCClass

from ecl import EclDataType
from ecl import EclPrototype
from ecl.grid.faults import Fault

class FaultBlockLayer(BaseCClass):
    TYPE_NAME = "fault_block_layer"
    _alloc                = EclPrototype("void*           fault_block_layer_alloc(ecl_grid,  int)", bind = False)
    _free                 = EclPrototype("void            fault_block_layer_free(fault_block_layer)")
    _size                 = EclPrototype("int             fault_block_layer_get_size(fault_block_layer)")
    _iget_block           = EclPrototype("fault_block_ref fault_block_layer_iget_block(fault_block_layer, int)")
    _add_block            = EclPrototype("fault_block_ref fault_block_layer_add_block(fault_block_layer, int)")
    _get_block            = EclPrototype("fault_block_ref fault_block_layer_get_block(fault_block_layer, int)")
    _del_block            = EclPrototype("void            fault_block_layer_del_block(fault_block_layer, int)")
    _has_block            = EclPrototype("bool            fault_block_layer_has_block(fault_block_layer, int)")
    _scan_keyword         = EclPrototype("bool            fault_block_layer_scan_kw(fault_block_layer, ecl_kw)")
    _load_keyword         = EclPrototype("bool            fault_block_layer_load_kw(fault_block_layer, ecl_kw)")
    _get_k                 = EclPrototype("int             fault_block_layer_get_k(fault_block_layer)")
    _get_next_id          = EclPrototype("int             fault_block_layer_get_next_id(fault_block_layer)")
    _scan_layer           = EclPrototype("void            fault_block_layer_scan_layer(fault_block_layer, layer)")
    _insert_block_content = EclPrototype("void            fault_block_layer_insert_block_content(fault_block_layer, fault_block)")
    _export_kw            = EclPrototype("bool            fault_block_layer_export(fault_block_layer, ecl_kw)")
    _get_layer            = EclPrototype("layer_ref       fault_block_layer_get_layer(fault_block_layer)")


    def __init__(self, grid, k):
        c_ptr = self._alloc(grid, k)
        if c_ptr:
            super(FaultBlockLayer, self).__init__(c_ptr)
        else:
            raise ValueError("Invalid input - failed to create FaultBlockLayer")

        # The underlying C implementation uses lazy evaluation and
        # needs to hold on to the grid reference. We therefore take
        # references to it here, to protect against premature garbage
        # collection.
        self.grid_ref = grid


    def __len__(self):
        return self._size()


    def __repr__(self):
        return self._create_repr('size=%d, k=%d' % (len(self), self.get_k()))

    def __getitem__(self, index):
        """
        @rtype: FaultBlock
        """
        if isinstance(index, int):
            if index < 0:
                index += len(self)

            if 0 <= index < len(self):
                return self._iget_block(index).setParent(self)
            else:
                raise IndexError("Index:%d out of range: [0,%d)" % (index, len(self)))
        elif isinstance(index,tuple):
            i,j = index
            if 0 <= i < self.grid_ref.get_nx() and 0 <= j < self.grid_ref.get_ny():
                geo_layer = self.get_geo_layer()
                block_id = geo_layer[i,j]
                if block_id == 0:
                    raise ValueError("No fault block defined for location (%d,%d)" % (i,j))
                else:
                    return self.get_block(block_id)
            else:
                raise IndexError("Invalid i,j : (%d,%d)" % (i,j))
        else:
            raise TypeError("Index should be integer type")

    def __contains__(self, block_id):
        return self._has_block(block_id)


    def scan_keyword(self, fault_block_kw):
        """
        Will reorder the block ids, and ensure single connectedness. Assign block_id to zero blocks.
        """
        ok = self._scan_keyword(fault_block_kw)
        if not ok:
            raise ValueError("The fault block keyword had wrong type/size: type:%s  size:%d  grid_size:%d" % (fault_block_kw.type_name, len(fault_block_kw), self.grid_ref.get_global_size()))


    def load_keyword(self, fault_block_kw):
        """
        Will load directly from keyword - without reorder; ignoring zero.
        """
        ok = self._load_keyword(fault_block_kw)
        if not ok:
            raise ValueError("The fault block keyword had wrong type/size:  type:%s  size:%d  grid_size:%d" % (fault_block_kw.type_name(), len(fault_block_kw), self.grid_ref.get_global_size()))


    def get_block(self, block_id):
        """
        @rtype: FaultBlock
        """
        if block_id in self:
            return self._get_block(block_id).setParent(self)
        else:
            raise KeyError("No blocks with ID:%d in this layer" % block_id)


    def delete_block(self, block_id):
        if block_id in self:
            self._del_block(block_id)
        else:
            raise KeyError("No blocks with ID:%d in this layer" % block_id)

    def add_block(self, block_id=None):
        if block_id is None:
            block_id = self.get_next_id()

        if block_id in self:
            raise KeyError("Layer already contains block with ID:%s" % block_id)
        else:
            return self._add_block(block_id).setParent(self)

    def get_next_id(self):
        return self._get_next_id()


    def get_k(self):
        return self._get_k()

    @property
    def k(self):
        return self._get_k()

    def free(self):
        self._free()


    def scan_layer(self, layer):
        self._scan_layer(layer)


    def insert_block_content(self, block):
        self._insert_block_content(block)

    def export_keyword(self, kw):
        if len(kw) != self.grid_ref.get_global_size():
            msg = 'The size of the target keyword must be equal to the size of the grid.'
            msg += '  Got:%d Expected:%d.'
            raise ValueError(msg % (len(kw), self.grid_ref.get_global_size()))

        if not kw.data_type.is_int():
            raise TypeError("The target kewyord must be of integer type")

        self._export_kw(kw)


    def add_fault_barrier(self, fault, link_segments=False):
        layer = self.get_geo_layer()
        layer.add_fault_barrier(fault, self.get_k(), link_segments)


    def add_fault_link(self, fault1, fault2):
        if not fault1.intersects_fault(fault2, self.get_k()):
            layer = self.get_geo_layer()
            layer.add_ij_barrier(fault1.extend_to_fault(fault2, self.get_k()))


    def join_faults(self, fault1, fault2):
        if not fault1.intersects_fault(fault2, self.get_k()):
            layer = self.get_geo_layer()
            try:
                layer.add_ij_barrier(Fault.join_faults(fault1, fault2, self.get_k()))
            except ValueError:
                err = 'Failed to join faults %s and %s'
                names = (fault1.get_name(), fault2.get_name())
                print(err % names)
                raise ValueError(err % names)


    def add_polyline_barrier(self, polyline):
        layer = self.get_geo_layer()
        p0 = polyline[0]
        c0 = self.grid_ref.find_cell_corner_xy(p0[0],  p0[1], self.get_k())
        i,j = self.grid_ref.find_cell_xy(p0[0],  p0[1], self.get_k())
        print('%g,%g -> %d,%d   %d' % (p0[0], p0[1], i,j,c0))
        for index in range(1,len(polyline)):
            p1 = polyline[index]
            c1 = self.grid_ref.find_cell_corner_xy(p1[0],  p1[1], self.get_k())
            i,j = self.grid_ref.find_cell_xy(p1[0],  p1[1], self.get_k())
            layer.add_interp_barrier(c0, c1)
            print('%g,%g -> %d,%d   %d' % (p1[0], p1[1], i,j,c1))
            print('Adding barrier %d -> %d' % (c0, c1))
            c0 = c1


    def get_geo_layer(self):
        """Returns the underlying geometric layer."""
        return self._get_layer()


    def cell_contact(self, p1, p2):
        layer = self.get_geo_layer()
        return layer.cell_contact(p1,p2)
