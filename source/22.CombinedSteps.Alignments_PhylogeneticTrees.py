#!/usr/bin/python

"""
  phylomizer - automated phylogenetic reconstruction pipeline - it resembles the
  steps followed by a phylogenetist to build a gene family tree with error-control
  of every step

  Copyright (C) 2014 - Salvador Capella-Gutierrez, Toni Gabaldon

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

desc = """
  --
  phylomizer - Copyright (C) 2014  Salvador Capella-Gutierrez, Toni Gabaldon
  [scapella, tgabaldon]_at_crg.es

  This program comes with ABSOLUTELY NO WARRANTY;
  This is free software, and you are welcome to redistribute it
  under certain conditions;
  --

  Script which combines the last two steps of the main pipeline in order to
  perform the reconstruct a MULTIPLE SEQUENCE ALIGNMENT (MSA) for the input
  sequences provided and to infer a PHYLOGENETIC TREE using as input the
  generated MSA
"""

import os
import sys
import argparse
from module_alignments import alignment
from module_trees import phylogenetic_trees
from module_utils import readConfig, lookForDirectory, lookForFile, printConfig

## Get dinamically version
#~ from _version import get_versions
#~ __version = get_versions()['version']
#~ del get_versions

__version = "1.0.0"

if __name__ == "__main__":

  usage = ("\n\npython %(prog)s -i (--in) multifasta sequence file -c (--config"
    + ") config_file -o (--out) output_directory [other_options]\n")

  parser = argparse.ArgumentParser(description = desc, usage = usage,
    formatter_class = argparse.RawTextHelpFormatter)

  parser.add_argument("-i", "--in", dest = "inFile", type = str, default = None,
    help = "Input file containing the query sequence/s")

  parser.add_argument("--cds", dest = "cdsFile", type = str, default = None,
    help = "Input file containing CDS corresponding to input protein seqs")

  parser.add_argument("-c", "--config", dest = "configFile", default = None, \
    type = str, help = "Input configuration file")

  parser.add_argument("-o", "--out", dest = "outFolder", type = str, default = \
    ".", help = "Output folder where all generated files will be dumped")

  parser.add_argument("-p", "--prefix", dest = "prefix", type = str, default = \
    "", help = "Set the prefix for all output files generated by the pipeline")

  parser.add_argument("-r", "--replace", dest = "replace", default = False, \
    action = "store_true", help = "Over-write any previously generated file")

  parser.add_argument("--version", action = "version", version ='%(prog)s \"' \
    + __version + "\"")

  ## If no arguments are given, just show the help and finish
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()

  ## Assign input parameters directly to the dictionary which will contain all
  ## current run configuration.
  parameters = {}
  parameters.setdefault("replace", args.replace)

  ## Assign which step is being executed. It is useful to know whether the log
  ## file should be replaced or not - even when the flag "replace" is set
  parameters.setdefault("step", 0)

  ## Check parameters related to files / directories
  if not lookForFile(args.inFile):
    sys.exit(("ERROR: Check input QUERY SEQUENCE/s file '%s'") % (args.inFile))
  parameters.setdefault("in_file", os.path.abspath(args.inFile))

  if args.cdsFile:
    if not lookForFile(args.cdsFile):
      sys.exit(("ERROR: Check input CDS file '%s'") % (args.cdsFile))
    parameters.setdefault("cds", os.path.abspath(args.cdsFile))

  if not lookForFile(args.configFile):
    sys.exit(("ERROR: Check input CONFIG file '%s'") % (args.configFile))
  parameters.setdefault("config_file", os.path.abspath(args.configFile))

  if not lookForDirectory(args.outFolder):
    sys.exit(("ERROR: Check output folder '%s'") % (args.outFolder))
  parameters.setdefault("out_directory", os.path.abspath(args.outFolder))

  ## Set output files prefix name depending on input user selection
  tag = os.path.split(args.inFile)[1].split(".")[0]
  parameters.setdefault("prefix", args.prefix if args.prefix else tag)

  ## Read the other parameters from the input config file
  parameters.update(readConfig(parameters["config_file"]))

  ## Check whether alignment will be reconstructed in one or two directions, i.e
  ## head and tails.
  if not "both_direction" in parameters:
    parameters["both_direction"] = True

  ## Print all set-up parameters
  printConfig(parameters)

  ## Reconstruct the Multiple Sequence Alignment for the selected sequences
  parameters.update(alignment(parameters))

  ## Assign which step is being executed. It is useful to know whether the log
  ## file should be replaced or not - even when the flag "replace" is set
  parameters["step"] = 1

  ## Reconstruct the Multiple Sequence Alignment for the input Sequences
  phylogenetic_trees(parameters)
