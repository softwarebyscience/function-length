# Importing library
import os
import csv
from matplotlib import pyplot as plt

# Getting all the csv files from the current directory
files = [f for f in os.listdir('.') if f.endswith(".csv")]

tot = 0

'''

methods
 FOUT Number of method calls (fan out) avg, max, total avg, max, total
 MLOC Method lines of code avg, max, total avg, max, total
 NBD Nested block depth avg, max, total avg, max, total
 PAR Number of parameters avg, max, total avg, max, total
 VG McCabe cyclomatic complexity avg, max, total avg, max, total
classes
 NOF Number of fields avg, max, total avg, max, total
 NOM Number of methods avg, max, total avg, max, total
 NSF Number of static fields avg, max, total avg, max, total
 NSM Number of static methods
files
 ACD Number of anonymous type declarations value avg, max, total
 NOI Number of interfaces value avg, max, total
 NOT Number of classes value avg, max, total
 TLOC Total lines of code 

'pre': The number of non-trivial defects that were reported in the last six months before release
'post': Same but for post-release, in the first six months

'''

buckets = [0.0] * 1000
cnt_buckets = [0] * 1000

method_lines_tot = 0
methods_tot = 0

for filename in files:
	with open(filename) as csvfile:
		reader = csv.reader(csvfile)
		headers = None
		for row in reader:
			if headers is None:
				headers = row
				continue
			pre_idx = headers.index('pre')
			post_idx = headers.index('post')
			NOM_idx = headers.index('NOM_sum')
			MLOC_idx = headers.index('MLOC_sum')
			TLOC_idx = headers.index('TLOC')
			if float(row[NOM_idx]) == 0: continue
			if float(row[MLOC_idx]) == 0: continue
			defects = float(row[post_idx]) + float(row[pre_idx])
			locs = float(row[MLOC_idx])
			defect_density = defects/locs
			num_methods = float(row[NOM_idx])
			lines_per_method = locs/num_methods
			bucket_idx = int(lines_per_method)
			buckets[bucket_idx] += defect_density
			cnt_buckets[bucket_idx] += 1
			method_lines_tot += locs
			methods_tot += num_methods

print('Average length of methods:', method_lines_tot/methods_tot)

MAX_LINES = 25
ans = [defect_total/cnt for defect_total, cnt in zip(buckets[:MAX_LINES], cnt_buckets[:MAX_LINES])]

plt.bar(list(range(MAX_LINES)), ans)
plt.xlabel("Average method length in class")
plt.ylabel("Average defect density of classes")
plt.show()
