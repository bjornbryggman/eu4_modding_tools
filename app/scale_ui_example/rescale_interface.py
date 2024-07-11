#!/usr/bin/env python

import logging
import os
import signal
import sys
import traceback

logging.basicConfig(filename='debug.log',level=logging.INFO)
logger = logging.getLogger("rescale_interface.py")

if os.path.exists("scale_ui.cfg"):
	myvars = {}
	with open("scale_ui.cfg") as cfg_file:
		for line in cfg_file:
			name, var = line.strip('\n').split("=")
			myvars[name.strip()] = var
	INPUT_GUI_HOME = myvars['GAME_HOME'] + "/interface/"
	OUTPUT_GUI_HOME = myvars['MOD_DIR'] + "/interface/"
	scale_factor = float(myvars['SCALE_FACTOR'])
else:
	msg = "No scale_ui.cfg file found.  Run install_scale_ui_mod.bat"
	print msg
	logger.error(msg)
	sys.exit()

def scale(string_data):
	global scale_factor
	string_list = string_data.split()
	logger.debug(string_data)
	ss = string_data
	index = 0
	for sstr in string_list:
		index += ss[index:].find(sstr)
		if (sstr == '{x=') or (sstr == 'x=') or (sstr == 'y=') or (sstr == '=') or (sstr == '{width=') or (sstr == 'width=') or (sstr == 'height=') or (sstr.find('%') != -1) or (sstr.find('@') != -1) or (sstr.find('10s') != -1):
			continue
		elif (sstr.find('{width=') != -1):
			kv = sstr.strip('{width=')
			sstr_new = "{width=" + str(int(round(int(kv) * scale_factor)))
			ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('width=') != -1):
			kv = sstr.strip('width=')
			sstr_new = "width=" + str(int(round(int(kv) * scale_factor)))
			ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('height=') != -1):
			kv_list = sstr.split('height=')
			if kv_list[1].find('}') != -1:
				kv = kv_list[1].strip('}')
				sstr_new = "height=" + str(int(round(int(kv) * scale_factor))) + '}'
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
			else:
				sstr_new = "height=" + str(int(round(int(kv_list[1]) * scale_factor)))
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('{x=') != -1):
			kv = sstr.strip('{x=')
			sstr_new = "{x=" + str(int(round(int(kv) * scale_factor)))
			ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('x=') != -1):
			kv_list = sstr.split('x=')
			sstr_new = "x=" + str(int(round(int(kv_list[1]) * scale_factor)))
			ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('y=') != -1):
			kv_list = sstr.split('y=')
			if kv_list[1].find('}') != -1:
				kv = kv_list[1].strip('}')
				sstr_new = "y=" + str(int(round(int(kv) * scale_factor))) + '}'
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
			else:
				sstr_new = "y=" + str(int(round(int(kv_list[1]) * scale_factor)))
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		elif (sstr.find('=') != -1):
			kv = sstr.strip('=')
			if kv.find('}') != -1:
				kv = kv.strip('}')
				try:
					int(kv)
				except ValueError:
					continue
				sstr_new = "=" + str(int(round(int(kv) * scale_factor))) + '}'
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
			else:
				try:
					int(kv)
				except ValueError:
					continue
				sstr_new = "=" + str(int(round(int(kv) * scale_factor)))
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
		else:
			if sstr.find('}') != -1:
				kv = sstr.strip('}')
				try:
					int(kv)
				except ValueError:
					continue
				sstr_new = str(int(round(int(kv) * scale_factor))) + '}'
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]
			else:
				try:
					int(sstr)
				except ValueError:
					continue
				sstr_new = str(int(round(int(sstr) * scale_factor)))
				ss = ss[0:index] + sstr_new + ss[index+len(sstr):]

	logger.debug(ss)
	return ss

def scale_gui_file(infile, outfile):
	output = str()
	changed = False
	with open(infile, "r") as fr:
		for data in fr:
			if ((data.find('position') != -1) or \
					(data.find('size') != -1) or \
					(data.find('spacing') != -1) or \
					(data.find('borderSize') != -1) or \
					(data.find('maxHeight') != -1) or \
					(data.find('maxheight') != -1) or \
					(data.find('maxWidth') != -1) or \
					(data.find('maxwidth') != -1) or \
					(data.find('pos_x') != -1)):
				scaled_data = scale(data)
				if data != scaled_data:
					data = scaled_data
					changed = True
			output += data
		fr.close()
		if changed:
			with open(outfile, "w") as ff:
				ff.write(output)
				ff.close()

def ls(pathStr, optionsStr, filterStr):
        assert optionsStr == 'tr' or optionsStr == ''
        fileLst = [fname for fname in os.listdir(pathStr) if (filterStr in fname) and (fname[0] != '.')]
        if optionsStr == '':
                return sorted(fileLst)
        return sorted(fileLst, None, lambda f: os.stat(pathStr + '/' + f).st_mtime)

def recursive_scale(src_dir, dest_dir, orig_dir=None):
	if not os.path.exists(dest_dir):
		try:
			os.makedirs(dest_dir)
		except:
			pass
	if os.path.isdir(src_dir):
		filenames = ls(src_dir, '', '')
		for filename in filenames:
			if os.path.isdir(src_dir + filename):
				recursive_scale(src_dir + filename + "/", dest_dir + filename + "/")
			src_stat = os.stat(src_dir + filename)
			if orig_dir:
				src_stat = os.stat(orig_dir + filename)
			dest_file = dest_dir + filename
			if os.path.exists(dest_file):
				if int(os.stat(dest_file).st_mtime) >= int(src_stat.st_mtime):
					continue
			if os.path.splitext(filename)[1] == '.gui' or os.path.splitext(filename)[1] == '.gfx':
				try:
					scale_gui_file(src_dir + filename, dest_dir + filename)
				except:
					logger.exception()
				if os.path.exists(dest_file):
					os.utime(dest_file, (src_stat.st_atime, src_stat.st_mtime))

recursive_scale(INPUT_GUI_HOME, OUTPUT_GUI_HOME)