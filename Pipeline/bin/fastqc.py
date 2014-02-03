## Version 1.0
## Author: Matthew Suderman
## Date: 2013-06-20

import ConfigParser
import io
import os
import argparse
from util import *
import traceback

parser = argparse.ArgumentParser(description='Apply FASTQC to all fastq files.')
parser.add_argument("fastq_dir", help="directory containing FASTQ files")
parser.add_argument("output_dir", help="directory to place FASTQC output")
parser.add_argument("log", help="file to send updates and error messages")
parser.add_argument("-c", "--config", help="configuration file", default="config.txt")

args = parser.parse_args()

if not os.path.dirname(args.log) == "":
    mkdir_p(os.path.dirname(args.log))
log=open(args.log, "a", 0)

try:
    mkdir_p(args.output_dir)
except:
    tee_error("could not create directory '", args.output_dir, "'", log)

config = ConfigParser.RawConfigParser(allow_no_value=True)
try:
    config.readfp(open(args.config))
except:
    tee_error("opening configuration file " + args.config, log)

try:
    fastqc = "." + os.path.sep + config.get("third", "fastqc")
except Exception as error:
    tee_error("in configuration file '", args.config + "'\n", error.message, log)

if not os.path.exists(args.fastq_dir): 
    tee_error(args.fastq_dir + " doesn't exist", log)

files = recursive_fnmatch(args.fastq_dir, "*.fastq.gz")
if len(files) == 0:
    tee_error("the directory '" + fastq_dir + "' contains no *.fastq.gz files", log)

for fastq_file in files:
    try:
        output_dir = os.path.join(args.output_dir, os.path.dirname(os.path.relpath(fastq_file, args.fastq_dir)))
        mkdir_p(output_dir)
        qc_file = os.path.join(output_dir, strip_suffix(os.path.basename(fastq_file), ".fastq.gz") + "_fastqc.zip")
        system_command([fastqc, "-o", output_dir, "-f", "fastq", fastq_file], qc_file, log)
    except Exception as error:
        print traceback.format_exc()
        tee_error(error.message, log)

log.close()

