import os

directories = os.listdir('.')

for d in directories:
    os.chdir(d)
    os.rename("accepted_hits_sorted_by_read_name.bam.bam", "accepted_hits_sorted_by_read_name.bam")
    os.chdir('..')
