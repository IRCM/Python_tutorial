## Version 1.0
## Author: Matthew Suderman
## Date: 2013-08-09

import homer
from util import *

def readcount(bam_filename, output_filename, log, config):
    output_dir = os.path.dirname(output_filename)
    try:
        mkdir_p(output_dir)
    except:
        tee_error("could not create directory '" + output_dir + "'", log)

    try:
        assembly = config.get("genome", "assembly")
        homer_dir = config.get("third", "homer")
        bedtools_dir = config.get("third", "bedtools")
        ucsc_dir =  config.get("third", "ucsc")
    except Exception as error:
        tee_error("in configuration file '" + config + "'\n" + error.message, log)

    homer.check_assembly(assembly, homer_dir, log)

    sizes_filename = os.path.join(output_dir, "chromosome-sizes-" + assembly + ".txt")
    system_command([os.path.join(homer_dir, "bin", "fetchChromSizes"), assembly], [sizes_filename], log, stdout=sizes_filename)

    bedgraph_filename = output_filename + ".bedGraph"
    system_command([os.path.join("bin", "readcount-bedGraph.sh"), bam_filename, sizes_filename, bedgraph_filename, bedtools_dir],
                   [bedgraph_filename], log)

    bigwig_filename = output_filename + ".bw"
    system_command([os.path.join(".", ucsc_dir, "bedGraphToBigWig"), bedgraph_filename, sizes_filename, bigwig_filename], [bigwig_filename], log)
