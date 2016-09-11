#!/usr/bin/python
"""
  prepare_data - auxiliary script aiming to prepare the data structure to
  reconstruct a number of gene trees i.e. a phylome

  Copyright (C) 2016 - Salvador Capella-Gutierrez, Toni Gabaldon

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
## To guarantee compatibility with python3.4
from __future__ import print_function

desc = """
  --
  phylomizer - Copyright (C) 2016  Salvador Capella-Gutierrez
  [salcagu_at_gmail.com], Toni Gabaldon [tgabaldon_at_crg.es]

  This program comes with ABSOLUTELY NO WARRANTY;
  This is free software, and you are welcome to redistribute it
  under certain conditions;
  --
  Auxiliary script to prepare the data struture for executing several times
  a given phylogenetic pipeline
"""

import os
import sys
import argparse

from Bio import SeqIO
from module_utils import splitSequence

from version import __version__, __revision__, __build__
__version = ("v%s rev:%s [BUILD:%s]") % (__version__, __revision__, __build__)

if __name__ == "__main__":

  usage = ("\n\npython %(prog)s -i seed_sequence/s -c config_file -d output_"
    + "directory -b sequences_db [other_options]\n")

  parser = argparse.ArgumentParser(description = desc, usage = usage,
    formatter_class = argparse.RawTextHelpFormatter)

  parser.add_argument("--folder", dest = "outDir", type = str, default = ".",
    help = "Set the ROOT directory for the whole data structure")

  parser.add_argument("--size", dest = "dirSize", type = int, default = 1000,
    help = "Set the number of seed proteins per subfolder in the DATA folder")

  ## Set species code to be detected from the input database. It could be either
  ## the first letter from the sequence ID, the tag after the first "_", or it
  ## could be empty to take all sequences in the input file
  parser.add_argument("--seed_sp", dest = "seed", type = str, default = "",
    help = "Species TAG to detect the seed species in the sequences database. "
    + "It could be 1) the first 3 letter of each sequence, the tag after the "
    + "1st \"_\", or it could be empty to take all sequences at the database")

  parser.add_argument("--script", dest = "script", required = True, type = str,
    help = "Set the absolute path for the reconstruction script")

  parser.add_argument("--interpreter", dest = "python", default = "python", \
    type = str, help = "Set the path to the PYTHON interpreter")

  ## We set some optional parameter which will be given to the scripts
  parser.add_argument("--min_seqs", dest = "minSeqs", type = str, default= None,
  help = "Set the minimum sequences number to reconstruct an alignment/tree."
  + "\nThis parameter overwrites whatever is set on the config file.")

  parser.add_argument("--max_hits", dest = "maxHits", type = str, default= None,
    help = "Set the maximum accepted homology hits after filtering for e-value/"
    + "coverage.\nThis parameter overwrites whatever is set on the config file.")

  parser.add_argument("-p", "--prefix", dest = "prefix", type = str, default = \
    "", help = "Set the prefix for all output files generated by the pipeline")

  parser.add_argument("-r", "--replace", dest = "replace", default = False, \
    action = "store_true", help = "Over-write any previously generated file")

  ## Some files will be copied to the data structure for ensuring all data is
  ## stored at the same ROOT directory
  parser.add_argument("-c", "--config", dest = "configFile", default = None, \
    type = str, help = "Input configuration file")

  parser.add_argument("-d", "--db", dest = "dbFile", type = str, default = None,
    help = "Input file containing the target sequence database")

  parser.add_argument("--cds", dest = "cdsFile", type = str, default = None,
    help = "Input file containing CDS corresponding to input protein seqs")

  parser.add_argument("--copy", dest = "copy", action = "store_false", default \
    = True, help = "Avoid copying database and configuration files to the ROOT "
    + "folder")

################################################################################
  ## Depending on the script to be used, set the steps to be executed - or let
  ## the script invokes the full pipeline with no specific steps.

  parser.add_argument("--steps", dest = "steps", type = str, default = ["all"],
    choices = ["all", "homology", "alignments", "trees"], nargs = "*", help = \
    "Set which step/s should be performed by the script")
################################################################################


  ## If no arguments are given, just show the help and finish
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()

  ## Get current directory - we will use this for normalizing input files and
  ## directories to their absolute paths
  current_directory = os.getcwd()

  ## Check parameters related to files / directories
  if not lookForFile(os.path.abspath(args.script)):
    sys.exit(("ERROR: Check input SCRIPT file '%s'") % (args.script))
  args.script = os.path.abspath(args.script)

  if not lookForFile(os.path.abspath(args.dbFile)):
    sys.exit(("ERROR: Check input TARGET SEQUENCES file '%s'") % (args.dbFile))
  args.dbFile = os.path.abspath(args.dbFile)

  ## Check some additional parameters
  if args.dirSize < 1:
    sys.exit(("ERROR: Check your subfolder DATA size \"%d\"") % (args.dirSize))

  ## Check whether the ROOT directory already exist or not ...
  if lookForDirectory(args.outDir):
    sys.exit(("ERROR: Output ROOT folder already exist '%s'") % (args.outDir))
    
  args.outFolder = os.path.abspath(args.outDir))
  ## ... and try to create it in case it doesn't exist 
  if not lookForDirectory(args.outDir, create = True):
    sys.exit(("ERROR: ROOT folder '%s' cannot be created") % (args.outDir))

  ## Read input BLAST DB file and check whether predefined seed species
  ## is in the database  
  proteome = {}
  for record in SeqIO.parse(args.dbFile, "fasta"):
    sp = record.id.split("_")[1] if record.id.find("_") != -1 else record.id[:3]

    ## If there is no TAG, take any sequence. Otherwise, try to detect the
    ## species TAG either from the first 3 letter of each sequence ID or from
    ## the tag after the 1st "_"
    if args.seed and args.seed != sp:
      continue

    ## Remove STOP codons located at the sequence last position
    seq = str(record.seq[:-1] if str(record.seq)[-1] == "*" else record.seq)
    proteome.setdefault(record.id, splitSequence(seq))

  ## Check whether there are sequences for the seed species
  if len(proteome) == 0:
    sys.exit(("\nERROR: Check Species TAG '%s'. No sequences detected") % \
      (seed_species))

  total = len(proteome)
  print (("INFO: '%d' sequences detected") % (total, file = sys.stderr)

  n = 0
  ## Dump sequences in the output directory
  for record in sorted(proteome):
    ## Create a subdirectory every N's sequences.
    if (n % args.dirSize) == 0:
      cDir = ("%s-%s") % (str(n + 1).zfill(5), str(n + args.dirSize).zfill(5))
      if not os.path.isdir(os.path.join(args.outDir, cDir)):
        os.makedirs(os.path.join(args.outDir, cDir))
      print (("INFO: Already processed %d/%d") % (n, total), file = sys.stderr)

    ## Get specific sequence folder
    oDirec = os.path.join(os.path.join(args.outDir, cDir), record)
    if not os.path.isdir(oDirec):
      os.makedirs(oDirec)

    ## Create FASTA file containing the sequence
    oFile = open(os.path.join(oDirec, ("%s.fasta") % (record)), "w")
    print ((">%s\n%s") % (record, proteome[record]), file = oFile)
    oFile.close()

    del proteome[record]

    ## Increase counter to ensure there are only 'args.dirSize' sequences
    ## for each folder
    n += 1
  print (("INFO: Already processed %d/%d") % (n, total), file = sys.stderr)


  ## print command-line
  ## Check incompatible options - and suboptions associated to them
  
