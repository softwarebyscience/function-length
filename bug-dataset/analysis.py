import csv
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt

folders = ['Eclipse JDT core', 'Eclipse PDE UI', 'Equinox', 'Lucene', 'Mylyn']

# We only inspect classes where the average length of methods is below this due to lack of data
MAX_AVG_LINES_PER_METHOD = 25

classname_to_bug_cnt = {}
for folder in folders:
	bug_metrics = open(folder + '/bug-metrics.csv')
	reader = csv.reader(bug_metrics, delimiter=';')
	next(reader) # skip headers
	for l in reader:
		classname = l[0].rstrip()
		num_bugs = int(l[1])
		classname_to_bug_cnt[classname] = num_bugs

classname_to_postrelease_bug_cnt = {}
for folder in folders:
	change_metrics = open(folder + '/change-metrics.csv')
	reader = csv.reader(change_metrics, delimiter=';')
	next(reader) # skip headers
	for l in reader:
		classname = l[0].rstrip()
		num_postrelease_bugs = int(l[16])
		classname_to_postrelease_bug_cnt[classname] = num_postrelease_bugs

# classname_to_bug_cnt = classname_to_postrelease_bug_cnt

classname_to_avg_method_len = {}
classname_to_num_methods = {}
classname_to_num_lines = {}

for folder in folders:
	pth = folder + '/biweekly-oo-values'
	onlyfiles = [f for f in listdir(pth) if isfile(join(pth, f))]
	num_lines_csv = pth + '/' + next(f for f in onlyfiles if f.endswith('-numberOfLinesOfCode.csv'))
	num_methods_csv = pth + '/' + next(f for f in onlyfiles if f.endswith('-numberOfMethods.csv'))
	reader_num_lines = csv.reader(open(num_lines_csv), delimiter=';')
	reader_num_methods = csv.reader(open(num_methods_csv), delimiter=';')
	# Remove headers
	next(reader_num_lines)
	next(reader_num_methods)
	for l in reader_num_methods:
		classname = l[0].rstrip()
		methods = float(l[-1])
		classname_to_num_methods[classname] = methods
	for l in reader_num_lines:
		classname = l[0].rstrip()
		lines = float(l[-1])
		classname_to_num_lines[classname] = lines
		if lines == -1 or classname_to_num_methods[classname] == 0:
			continue
		classname_to_avg_method_len[classname] = lines/classname_to_num_methods[classname]

avg_method_len_to_bug_density = [0]*MAX_AVG_LINES_PER_METHOD
cnt = [0]*MAX_AVG_LINES_PER_METHOD

for classname, avg_method_len in classname_to_avg_method_len.items():
	# no bug data for one class, apparently because it's very new
	if classname == 'org::eclipse::mylyn::internal::wikitext::confluence::core::util::Options':
		continue
	bugs = classname_to_bug_cnt[classname]
	lines = classname_to_num_methods[classname]
	bugs_per_line = bugs/lines
	avg_method_len = int(classname_to_avg_method_len[classname])
	if avg_method_len >= MAX_AVG_LINES_PER_METHOD:
		continue
	avg_method_len_to_bug_density[avg_method_len] += bugs_per_line
	cnt[avg_method_len] += 1

ans = []
for tot_bug_density, count in zip(avg_method_len_to_bug_density, cnt):
	avg = f"{tot_bug_density/count:.2f}"
	ans.append(tot_bug_density/count)

moving_avg = []
for i in range(len(ans)):
	start = max(i - 1, 0)
	end = min(len(ans), i + 2)
	total = sum(ans[start:end])
	moving_avg.append(total / (end - start))

x_pos = list(range(len(ans)))
plt.bar(x_pos, ans)
plt.xlabel("Average method length in class")
plt.ylabel("Average defect density of classes")
plt.plot(x_pos, moving_avg, color='red')
plt.show()
