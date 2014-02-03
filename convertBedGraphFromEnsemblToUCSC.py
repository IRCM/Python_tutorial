#!/usr/bin/env python

# Open bedgraph file
union_sleep_dep_and_Ctrl = open ("union_sleep-dep_and_Ctrl.bg")

# Open output file
union_sleep_dep_and_Ctrl_corrected = open("union_sleep-dep_and_Ctrl_corrected.bg", 'w')

# Just copy 1st line
line = union_sleep_dep_and_Ctrl.readline()

# Write header for difference file
union_sleep_dep_and_Ctrl_corrected.write(line)

for line in union_sleep_dep_and_Ctrl:
    line = line.replace("MT", "M")
    union_sleep_dep_and_Ctrl_corrected.write("chr" + line)

union_sleep_dep_and_Ctrl.close()
union_sleep_dep_and_Ctrl_corrected.close()