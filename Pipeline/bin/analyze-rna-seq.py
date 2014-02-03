## Version 1.0
## Author: Matthew Suderman
## Date: 2013-09-04

import ConfigParser
import io
import os
import argparse
from util import *
import traceback
import tracks

parser = argparse.ArgumentParser(description='Align rna-seq paired end read data.')
parser.add_argument("fastq_dir", help="directory containing FASTQ files")
parser.add_argument("output_dir", help="directory to place resulting BAM files")
parser.add_argument("log", help="file to send updates and error messages")
parser.add_argument("-p", "--cores", help="number of cpu cores to use for read mapping", type=int, default=4)
parser.add_argument("-c", "--config", help="configuration file", default="config.txt")

args = parser.parse_args()

log = open_log(args.log)
config = open_config(args.config)

try:
    mkdir_p(args.output_dir)
except:
    tee_error("could not create directory '" + args.output_dir + "'", log)

if not os.path.exists(args.fastq_dir):
    tee_error(args.fastq_dir + " doesn't exist", log)

check_command_exists("gunzip --version".split(), log)
check_command_exists("nice --version".split(), log)

try:
    samtools = config.get("third","samtools")
    tophat_dir = config.get("third","tophat")
    cufflinks_dir = config.get("third","cufflinks")
    bowtie = config.get("third", "bowtie2")
    bowtie_build = config.get("third", "bowtie2-build")
    fasta = config.get("genome", "sequence")
    assembly = config.get("genome", "assembly")
    gtf = config.get("genome","gtf")
    build_dir = config.get("genome", "bowtie2-build-dir")
except Exception as error:
    tee_error("in configuration file '" + args.config + "'\n" + error.message, log)

mkdir_p(build_dir)

if not os.path.isfile(fasta):
    tee_error(fasta + " doesn't exist", log)

system_command(["nice", bowtie_build, fasta, os.path.join(build_dir, assembly)],
               targets=[os.path.join(build_dir, assembly + ".1.bt2")],
               log=log) ## takes about 4 hours

files = recursive_fnmatch(args.fastq_dir, "*_R1.fastq.gz")
if len(files) == 0:
    tee_error("the directory '" + fastq_dir + "' contains no *_R1.fastq.gz files", log)

for file1 in files:
    file2=file1.replace("_R1", "_R2")
    name=strip_suffix(os.path.basename(file1), "_R1.fastq.gz")
    output_dir = os.path.join(args.output_dir, os.path.dirname(os.path.relpath(file1, args.fastq_dir)), name)
    local1=os.path.join(args.output_dir, os.path.basename(strip_suffix(file1, ".gz"))) ## bowtie needs input files in output directory
    local2=os.path.join(args.output_dir, os.path.basename(strip_suffix(file2, ".gz")))
    bam=os.path.join(output_dir, "accepted_hits.bam")
    try:
        if not os.path.isfile(bam):
            mkdir_p(output_dir)
            system_command(["cp", file1,local1+".gz"], local1+".gz", log)
            system_command(["cp", file2,local2+".gz"], local2+".gz", log)
            system_command(["gunzip", local1+".gz"], local1, log)
            system_command(["gunzip", local2+".gz"], local2, log)
            os.environ['PATH'] = os.environ['PATH'] \
                                 + ":" + os.path.dirname(bowtie) \
                                 + ":" + os.path.dirname(samtools)
            system_command(["nice", os.path.join(tophat_dir, "tophat2"),
                            "--mat-inner-dist", "150",
                            "--mate-std-dev", "40",
                            "--library-type", "fr-unstranded",
                            "--no-coverage-search",
                            "--num-threads", str(args.cores),
                            "-o", output_dir,
                            os.path.join(build_dir, assembly),
                            local1,
                            local2],
                           [bam],
                           log)

        system_command([os.path.join(cufflinks_dir, "cufflinks"),
                        "-G", gtf,
                        "-p", str(args.cores),
                        "-o", output_dir,
                        bam],
                       [os.path.join(output_dir, "genes.fpkm_tracking")],
                       log)

        ### tracks.readcount(bam, os.path.join(output_dir, name + ".read_counts"), log, config)

    except Exception as error:
        print traceback.format_exc()
        tee_error(error.message, log)

log.close()

