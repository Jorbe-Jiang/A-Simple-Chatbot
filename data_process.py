# -*- coding: utf-8 -*-
import os
import sys
import chardet

dataset = 'conv.dat'
format_dataset = 'format_conv.dat'

def process_data():
	fp = open(dataset, 'r')
	format_fp = open(format_dataset, 'w')

	i = 0
	for index, line in enumerate(fp.readlines()):
		line = line.strip()
		if line == 'E':
			continue
		else:
			line = line[1:].strip().replace('/', '')
			i += 1
		if i % 2 == 0:
			line.decode('utf-8')
			format_fp.write('U2 '+line+'\n')
		else:
			line.decode('utf-8')
			#print chardet.detect(line)
			#exit()
			#line = unicode(line)
			format_fp.write('U1 '+line+'\n')

	fp.close()
	format_fp.close()


if __name__ == "__main__":
	process_data()