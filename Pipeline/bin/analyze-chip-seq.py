## Version 1.0
## Author: Matthew Suderman
## Date: 2013-07-07

## Given a paired-end chip-seq experiment with paired treatment and controls, create the MACS fold-change matrix.

import ConfigParser
import io
import os
import argparse
import traceback
import csv
from util import *
import homer

parser = argparse.ArgumentParser(description='Given a paired-end chip-seq experiment with paired treatment and controls, create the MACS fold-change matrix.')
parser.add_argument("samples", help="spreadsheet describing samples (id,treatment,control); file format can be bam or sam")
parser.add_argument("output_dir", help="directory to place output files")
parser.add_argument("log", help="file to send updates and error messages")
parser.add_argument("-p", "--p_threshold", help="Poisson p-value threshold for identifying peaks", type=float, default=0.001)
parser.add_argument("-f", "--fold_increase", help="Read count fold increase of treated over control for identifying peaks", type=float, default=4)
parser.add_argument("-c", "--config", help="configuration file", default="config.txt")

args = parser.parse_args()

if not os.path.dirname(args.log) == "":
    mkdir_p(os.path.dirname(args.log))
log=open(args.log, "a", 0)

try:
    mkdir_p(args.output_dir)
except:
    tee_error("could not create directory '" + args.output_dir + "'", log)

config = ConfigParser.RawConfigParser(allow_no_value=True)
try:
    config.readfp(open(args.config))
except:
    tee_error("opening configuration file " + args.config, log)

try:
    assembly = config.get("genome", "assembly")
    homer_dir = config.get("third", "homer")
except Exception as error:
    tee_error("in configuration file '" + args.config + "'\n" + error.message, log)

def tag_dir(filename):
    return os.path.join(args.output_dir, os.path.basename(filename) + "-tags-homer")

try:
    homer.check_assembly(assembly, homer_dir, log)

    xls_files = []
    reader = csv.DictReader(open(args.samples,'r'), fieldnames=('id','treated','control'), delimiter=',')
    reader.next() ## skip header line
    for row in reader:
        treated_tag_dir = tag_dir(row["treated"])
        system_command([os.path.join(homer_dir, "bin", "makeTagDirectory"), treated_tag_dir, "-format", "sam", "-unique", "-single", "-genome", assembly, "-checkGC", row['treated']],
                       [os.path.join(treated_tag_dir, "tagCountDistribution.txt")],
                       log)

        control_tag_dir = tag_dir(row["control"])
        system_command([os.path.join(homer_dir, "bin", "makeTagDirectory"), control_tag_dir, "-format", "sam", "-unique", "-single", "-genome", assembly, "-checkGC", row['control']],
                       [os.path.join(control_tag_dir, "tagCountDistribution.txt")],
                       log)

        peaks_filename = os.path.join(args.output_dir, row["id"] + "-peaks.csv")
        system_command([os.path.join(homer_dir, "bin", "findPeaks"), treated_tag_dir,
                        "-style", "factor", "-center", "-fdr", "0.2", "-F", str(args.fold_increase), "-P", str(args.p_threshold),
                        "-o", peaks_filename, "-i", control_tag_dir],
                       [peaks_filename],
                       log)

        xls_files = xls_files + [peaks_filename]

    if len(xls_files) > 1:
        merged_peaks = os.path.join(args.output_dir, "merged-peaks-homer.csv")
        system_command([os.path.join(homer_dir, "bin", "mergePeaks"), "-d", "100"] + xls_files, [merged_peaks], log, stdout=merged_peaks)

        xls_files = []

        reader = csv.DictReader(open(args.samples,'r'), fieldnames=('id','treated','control'), delimiter=',')
        reader.next() ## skip header line
        for row in reader:
            treated_tag_dir = tag_dir(row["treated"])
            control_tag_dir = tag_dir(row["control"])

            peaks_filename = os.path.join(args.output_dir, row["id"] + "-merged-peaks.csv")
            system_command([os.path.join(homer_dir, "bin", "getDifferentialPeaks"), merged_peaks, treated_tag_dir, control_tag_dir,
                            "-F", "0", "-P", "1"],
                           [peaks_filename],
                           log,
                           stdout=peaks_filename)

            xls_files = xls_files + [peaks_filename]

        p_matrix_filename = os.path.join(args.output_dir, "peak-p-value-matrix.csv")
        fc_matrix_filename = os.path.join(args.output_dir, "peak-fold-change-matrix.csv")
        fieldnames = ("id","chromosome","start","end","strand","score","focus_ratio","total_tags","background_tags", "fold_change","p")
        reader = csv.DictReader(skip_comments(open(xls_files[0], "r")), fieldnames=fieldnames, delimiter="\t")
        p_readers = [csv.DictReader(skip_comments(open(filename, "r")), fieldnames=fieldnames, delimiter="\t") for filename in xls_files]
        fc_readers = [csv.DictReader(skip_comments(open(filename, "r")), fieldnames=fieldnames, delimiter="\t") for filename in xls_files]
        names = [ strip_suffix(os.path.basename(filename), "-merged-peaks.csv") for filename in xls_files]
        p_writer = csv.writer(open(p_matrix_filename, "w"))
        p_writer.writerow(["id","chromosome","start","end","strand"] + names)
        fc_writer = csv.writer(open(fc_matrix_filename, "w"))
        fc_writer.writerow(["id","chromosome","start","end","strand"] + names)
        for row in reader:
            fc = [ row["id"], row["chromosome"], row["start"], row["end"], row["strand"] ] + [ reader.next()["fold_change"] for reader in fc_readers ]
            fc_writer.writerow(fc)
            p = [ row["id"], row["chromosome"], row["start"], row["end"], row["strand"] ] + [ reader.next()["p"] for reader in p_readers ]
            p_writer.writerow(p)

except Exception as error:
        print traceback.format_exc()
        tee_error(error.message, log)

log.close()




# bedgraph_filename = "...."

# sizes_filename = os.path.join(args.output_dir, "chromosome-sizes-" + assembly + ".txt")
# system_command([os.path.join(homer_dir, "bin", "fetchChromSizes"), assembly], [sizes_filename], log, stdout=sizes_filename)

# bedgraph = log=open(bedgraph.filename, "a", 0)
# p1 = subprocess.Popen([os.path.join(bedtools_dir, "bedtools"), "bamtobed", "-bedpe", "-i", bam_filename], stdout=subprocess.PIPE)
# p2 = subprocess.Popen(["awk", '{print $1 "\t" $2 "\t" $6 "\t" $7 "\t" $8 "\t" $9}'], stdin=p1.stdout, stdout=subprocess.PIPE)
# p3 = subprocess.Popen(["sort", "--temporary-directory=.", "-k", "1,1"], stdin=p2.stdout, stdout=subprocess.PIPE)
# p4 = subprocess.Popen([os.path.join(bedtools_dir, "bedtools"), "genomecov", "-bg", "-i", "stdin", "g-", sizes_filename], stdin=p3.stdout, stdout=bedgraph)
# p1.stdout.close()
# p2.stdout.close()
# p3.stdout.close()
# p4.stdout.close()
# bedgraph.close()

# .....
# BIGWIG=${OUTPUT}/${NAME}-raw-read-counts.bw
# CMD="bedGraphToBigWig ${BEDGRAPH} ${SIZES} ${BIGWIG}"
# ./bin/cmd.sh "${CMD}" ${BIGWIG}










