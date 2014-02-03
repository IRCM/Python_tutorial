## Version 1.0
## Author: Matthew Suderman
## Date: 2013-06-20

import ConfigParser
import io
import os
import argparse
from util import *
import traceback

parser = argparse.ArgumentParser(description='Apply Trimmomatic to all fastq files.')
parser.add_argument("fastq_dir", help="directory containing FASTQ files")
parser.add_argument("output_dir", help="directory to place Trimmomatic output")
parser.add_argument("log", help="file to send updates and error messages")
parser.add_argument("-t", "--trimmomatic", \
                        help="trimmomatic input (in quotes), see http://www.usadellab.org/cms/index.php?page=trimmomatic", \
                        default="ILLUMINACLIP:data/fastq/illumina.fa:2:40:15 MINLEN:16")
parser.add_argument("-p", "--cores", help="number of cpu cores to use for read mapping", type=int, default=4)
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
    trimmomatic = config.get("third", "trimmomatic").split()
except Exception as error:
    tee_error("in configuration file '", args.config + "'\n", error.message, log)

if not os.path.exists(args.fastq_dir): 
    tee_error(args.fastq_dir + " doesn't exist", log)

files = recursive_fnmatch(args.fastq_dir, "*_R1.fastq.gz")
if len(files) == 0:
    tee_error("the directory '" + fastq_dir + "' contains no *_R1.fastq.gz files", log)

for file1 in files:
    try:
        file2=file1.replace("_R1", "_R2") ## should make sure this file exists 
        output_dir = os.path.join(args.output_dir, os.path.dirname(os.path.relpath(file1, args.fastq_dir)))
        mkdir_p(output_dir)
        name=strip_suffix(os.path.basename(file1), "_R1.fastq.gz")
        output1=os.path.join(output_dir, os.path.basename(file1))
        output2=os.path.join(output_dir, os.path.basename(file2))
        unpaired1=strip_suffix(output1, "_R1.fastq.gz") + "_R1.unpaired.fastq.gz"
        unpaired2=strip_suffix(output2, "_R2.fastq.gz") + "_R1.unpaired.fastq.gz"
        targets = [output1, unpaired1, output2, unpaired2]
        system_command(trimmomatic + ["-threads", str(args.cores), file1, file2] + targets + args.trimmomatic.split(), targets, log)
    except Exception as error:
        print traceback.format_exc()
        tee_error(error.message, log)

log.close()



