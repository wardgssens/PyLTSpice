#!/usr/bin/env python
# coding=utf-8

# -------------------------------------------------------------------------------
#    ____        _   _____ ____        _
#   |  _ \ _   _| | |_   _/ ___| _ __ (_) ___ ___
#   | |_) | | | | |   | | \___ \| '_ \| |/ __/ _ \
#   |  __/| |_| | |___| |  ___) | |_) | | (_|  __/
#   |_|    \__, |_____|_| |____/| .__/|_|\___\___|
#          |___/                |_|
#
# Name:        LTSteps.py
# Purpose:     Process LTSpice output files and align data for usage in a spread-
#              sheet tool such as Excel, or Calc.
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------

"""
This module allows to process data generated by LTSpice during simulation. There are three types of files that are
handled by this module.

    + log files - Files with the extension '.log' that are automatically generated during simulation, and that are
      normally accessible with the shortcut Ctrl+L after a simulation is ran.Log files are interesting for two reasons.

            1. If .STEP primitives are used, the log file contain the correspondence between the step run and the step
            value configuration.

            2. If .MEAS primitives are used in the schematic, the log file contains the measurements made on the output
            data.

      LTSteps.py can be used to retrieve both step and measurement information from log files.

    + txt files - Files exported from the Plot File -> Export data as text menu. This file is an text file where data is
      saved in the text format. The reason to use PyLTSpice instead of another popular lib as pandas, is because the data
      format when .STEPS are used in the simulation is not not very practical. The PyLTSpice LTSteps.py can be used to
      reformat the text, so that the run parameter is added to the data as an additional column instead of a table
      divider. Please Check LTSpiceExport class for more information.

    + mout files - Files generated by the Plot File -> Execute .MEAS Script menu. This command allows the user to run
      predefined .MEAS commands which create a .mout file. A .mout file has the measurement information stored in the
      following format:

      .. code-block:: text

            Measurement: Vout_rms
            step	RMS(V(OUT))	FROM	TO
             1	1.41109	0	0.001
             2	1.40729	0	0.001

            Measurement: Vin_rms
              step	RMS(V(IN))	FROM	TO
                 1	0.706221	0	0.001
                 2	0.704738	0	0.001

            Measurement: gain
              step	Vout_rms/Vin_rms
                 1	1.99809
                 2	1.99689


The LTSteps.py can be used directly from a command line by invoking python with the -m option as exemplified below.

.. code-block:: text

    $ python -m PyLTSpice.LTSteps <path_to_filename>

If `<path_to_filename>` is a log file, it will create a file with the same name, but with extension .tout that is a
tab separated value (tsv) file, which contains the .STEP and .MEAS information collected.

If `<path_to_filename>` is a txt exported file, it will create a file with the same name, but with extension .tsv a
tab separated value (tsv) file, which contains data reformatted with the step number as one of the columns. Please
consult the reformat_LTSpice_export() function for more information.

If `<path_to_filename>` is a mout file, it will create a file with the same name, but with extension .tmout that is a
tab separated value (tsv) file, which contains the .MEAS information collected, but adding the STEP run information
as one of the columns.

If `<path_to_filename>` argument is ommited, the script will automatically search for the newest .log/.txt/.mout file
and use it.

"""
import os
import sys

from .log.ltsteps import *


def valid_extension(filename):
    return filename.endswith('.txt') or filename.endswith('.log') or filename.endswith('.mout')


if len(sys.argv) > 1:
    filename = sys.argv[1]
    if not valid_extension(filename):
        print("Invalid extension in filename '%s'" % filename)
        print("This tool only supports the following extensions :'.txt','.log','.mout'")
        exit(-1)
else:
    filename = None
    newer_date = 0
    for f in os.listdir():
        date = os.path.getmtime(f)
        if date > newer_date and valid_extension(f):
            newer_date = date
            filename = f
if filename is None:
    print("File not found")
    print("This tool only supports the following extensions :'.txt','.log','.mout'")
    exit(-1)

fname_out = None
if filename.endswith('.txt'):
    fname_out = filename[:-len('txt')] + 'tsv'
elif filename.endswith('.log'):
    fname_out = filename[:-len('log')] + 'tlog'
elif filename.endswith('.mout'):
    fname_out = filename[:-len('mout')] + 'tmout'
else:
    print("Error in file type")
    print("This tool only supports the following extensions :'.txt','.log','.mout'")
    exit(-1)

if fname_out is not None:
    print("Processing File %s" % filename)
    print("Creating File %s" % fname_out)
    if filename.endswith('txt'):
        print("Processing Data File")
        reformat_LTSpice_export(filename, fname_out)
    elif filename.endswith("log"):
        data = LTSpiceLogReader(filename)
        data.split_complex_values_on_datasets()
        data.export_data(fname_out)
    elif filename.endswith(".mout"):
        log_file = filename[:len('mout')] + 'log'
        if os.path.exists(log_file):
            steps = LTSpiceLogReader(log_file, read_measures=False)
            data = LTSpiceLogReader(filename, step_set=steps.stepset)
            data.stepset = steps.stepset
        else:
            # just reformats
            data = LTSpiceLogReader(filename)
        data.split_complex_values_on_datasets()
        data.export_data(fname_out)
        data.export_data(fname_out)

# input("Press Enter to Continue")