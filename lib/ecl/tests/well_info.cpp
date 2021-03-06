/*
   Copyright (C) 2013  Equinor ASA, Norway.

   The file 'well_conn.c' is part of ERT - Ensemble based Reservoir Tool.

   ERT is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   ERT is distributed in the hope that it will be useful, but WITHOUT ANY
   WARRANTY; without even the implied warranty of MERCHANTABILITY or
   FITNESS FOR A PARTICULAR PURPOSE.

   See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
   for more details.
*/
#include <stdlib.h>
#include <stdbool.h>

#include <ert/util/test_util.hpp>
#include <ert/util/stringlist.hpp>
#include <ert/util/util.h>

#include <ert/ecl/ecl_util.hpp>
#include <ert/ecl/ecl_grid.hpp>

#include <ert/ecl_well/well_info.hpp>

int main(int argc, char **argv) {
    util_install_signals();
    const char *grid_file = argv[1];

    ecl_grid_type *grid = ecl_grid_alloc(grid_file);
    test_assert_not_NULL(grid);
    {
        well_info_type *well_info = well_info_alloc(grid);
        test_assert_not_NULL(well_info);
        if (argc >= 3)
            well_info_load_rstfile(well_info, argv[2], true);

        well_info_free(well_info);
    }
    ecl_grid_free(grid);
    exit(0);
}
