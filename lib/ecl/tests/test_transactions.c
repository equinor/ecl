
/*
   Copyright (C) 2017  Statoil ASA, Norway.

   The file 'test_transactions.c' is part of ERT - Ensemble based Reservoir Tool.

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
#include <unistd.h>

#include <ert/util/test_util.h>
#include <ert/util/util.h>
#include <ert/util/test_work_area.h>

#include <ert/ecl/ecl_util.h>
#include <ert/ecl/fortio.h>
#include <ert/ecl/ecl_endian_flip.h>
#include <ert/ecl/ecl_file.h>
#include <ert/ecl/ecl_file_view.h>
#include <ert/ecl/ecl_kw.h>
#include <ert/ecl/transaction.h>


void transact() {
  //x: create testfile w/ 3 kw added
  //x: create an ecl_file_view object
  //x: access 2 kw
  //x: create a start transaction object t1
  //x: access 1 kw three times
  //x: create a start transaction object t2
  //x: access 2 kw 1 time each
  //end transaction t2 and assert
  //end transaction t1 and assert
  //free ecl_file_kw object

  test_work_area_type * work_area = test_work_area_alloc("ecl_file_index_testing");
  {
     char * file_name = "data_file";
     fortio_type * fortio = fortio_open_writer(file_name, false, ECL_ENDIAN_FLIP);

      //creating the data file
     size_t data_size = 10;
     ecl_kw_type * kw1 = ecl_kw_alloc("TEST1_KW", data_size, ECL_INT);
     for(int i = 0; i < data_size; ++i)
        ecl_kw_iset_int(kw1, i, 537 + i);
     ecl_kw_fwrite(kw1, fortio); 
     
     data_size = 5;
     ecl_kw_type * kw2 = ecl_kw_alloc("TEST2_KW", data_size, ECL_FLOAT);
     for(int i = 0; i < data_size; ++i)
        ecl_kw_iset_float(kw2, i, 0.15 * i);
     ecl_kw_fwrite(kw2, fortio);

     data_size = 3;
     ecl_kw_type * kw3 = ecl_kw_alloc("TEST3_KW", data_size, ECL_FLOAT);
     for(int i = 0; i < data_size; i++)
        ecl_kw_iset_float(kw3, i, 0.45 * i);
     ecl_kw_fwrite(kw3, fortio);

     fortio_fclose(fortio); 
     //finished creating data file
     
     ecl_file_type * file = ecl_file_open(file_name, 0);
     ecl_file_view_type * file_view = ecl_file_get_global_view(file);
     ecl_file_kw_type * file_kw2 = ecl_file_view_iget_file_kw( file_view , 1);

     ecl_file_view_iget_kw(file_view, 1);
     ecl_file_view_iget_kw(file_view, 1);
     test_assert_int_equal( ecl_file_kw_get_ref_count(file_kw2) , 2);
     
     transaction_type * t1 = transaction_start(file_view);
       ecl_file_view_iget_kw(file_view, 0);
       ecl_file_view_iget_kw(file_view, 0);
       ecl_file_view_iget_kw(file_view, 0);

       transaction_type * t2 = transaction_start(file_view);
         ecl_file_view_iget_kw(file_view, 1);
         ecl_file_view_iget_kw(file_view, 2);

       transaction_end(t2);
       test_assert_int_equal( transaction_iget_value(t2, 0), 0);
       test_assert_int_equal( transaction_iget_value(t2, 1), 1);
       test_assert_int_equal( transaction_iget_value(t2, 2), 1);
       transaction_free(t2);
     
     transaction_end(t1);
     test_assert_int_equal( transaction_iget_value(t1, 0), 3);
     test_assert_int_equal( transaction_iget_value(t1, 1), 1);
     test_assert_int_equal( transaction_iget_value(t1, 2), 1);
     transaction_free(t1);

     ecl_file_close(file);

   }
   test_work_area_free( work_area );
}



int main( int argc , char ** argv) {
  util_install_signals();
  transact();
  exit(0);
}