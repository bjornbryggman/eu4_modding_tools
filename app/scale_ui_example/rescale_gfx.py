#!/usr/bin/env python

import logging
import os
import shutil
import sys
import time
import traceback
import zipfile

from gimpfu import *

logging.basicConfig(filename='debug.log',level=logging.INFO)
logger = logging.getLogger("rescale_gfx.py")

if os.path.exists("scale_ui.cfg"):
	myvars = {}
	with open("scale_ui.cfg") as cfg_file:
		for line in cfg_file:
			name, var = line.strip('\n').split("=")
			myvars[name.strip()] = var
	INPUT_GFX_HOME = myvars['GAME_HOME'] + "/gfx/"
	INPUT_DLC_HOME = myvars['GAME_HOME'] + "/dlc/"
	DLC_GFX_HOME = myvars['MOD_DIR'] + "/dlc/gfx/"
	TEMP_GFX_HOME = os.getcwd() + "/temp_gfx/"
	OUTPUT_GFX_HOME = myvars['MOD_DIR'] + "/gfx/"
	scale_factor = float(myvars['SCALE_FACTOR'])
else:
	msg = "No scale_ui.cfg file found.  Run install_scale_ui_mod.bat"
	print(msg)
	logger.error(msg)
	sys.exit()

GFX_DIR_LIST = ['dlc_pictures/',
				'event_pictures/',
				'interface/']

trouble_list = list()

def ls(pathStr, optionsStr, filterStr):
	assert optionsStr == 'tr' or optionsStr == ''
	fileLst = [fname for fname in os.listdir(pathStr) if (filterStr in fname) and (fname[0] != '.')]
	if optionsStr == '':
		return sorted(fileLst)
	return sorted(fileLst, None, lambda f: os.stat(pathStr + '/' + f).st_mtime)

def rescale_dds(filename, INPUT_DIR, OUTPUT_DIR):
	global scale_factor

	input_file = INPUT_DIR + filename
	output_file = OUTPUT_DIR + filename
	logger.info("Load dds file = {}".format(filename))
	dds_image = pdb.file_dds_load(input_file, filename, 0, 0)
	width = round(pdb.gimp_image_width(dds_image) * scale_factor)
	height = round(pdb.gimp_image_height(dds_image) * scale_factor)
	pdb.gimp_context_set_interpolation(3)
	pdb.gimp_image_scale(dds_image, width, height)
	drawable = pdb.gimp_image_get_active_drawable(dds_image)
	#pdb.plug_in_sharpen(dds_image, drawable, 50)
	pdb.file_dds_save(dds_image, drawable, output_file, filename, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.2, 0, 0, 0.50)
	gimp.delete(dds_image)

def rescale_dds_wrapper(filename, INPUT_DIR, OUTPUT_DIR):
	global trouble_list

	try:
		rescale_dds(filename, INPUT_DIR, OUTPUT_DIR)
	except:
		#traceback.print_exc()
		logger.exception()
		# is file a tga hidden in a dds file
		rescale_tga_wrapper(filename, INPUT_DIR, OUTPUT_DIR)

def rescale_tga(filename, INPUT_DIR, OUTPUT_DIR):
	global scale_factor

	input_file = INPUT_DIR + filename
	output_file = OUTPUT_DIR + filename

	logger.info("Load tga file = {}".format(filename))
	tga_image = pdb.file_tga_load(input_file, "rescale tga")
	width = round(pdb.gimp_image_width(tga_image) * scale_factor)
	height = round(pdb.gimp_image_height(tga_image) * scale_factor)
	pdb.gimp_context_set_interpolation(3)
	pdb.gimp_image_scale(tga_image, width, height)
	drawable = pdb.gimp_image_get_active_drawable(tga_image)
	#pdb.plug_in_sharpen(tga_image, drawable, 50)
	pdb.file_tga_save(tga_image, drawable, output_file, "rescale tga", 0, 1)
	gimp.delete(tga_image)

def rescale_tga_wrapper(filename, INPUT_DIR, OUTPUT_DIR):
	try:
		rescale_tga(filename, INPUT_DIR, OUTPUT_DIR)
	except:
		#traceback.print_exc()
		logger.exception()
		trouble_list.append(INPUT_DIR + filename)

def unzip(source_filename, dest_dir):
	with zipfile.ZipFile(source_filename) as zf:
		for zi in zf.infolist():
			zf.extract(zi, dest_dir + '/')
			date_time = time.mktime(zi.date_time + (0, 0, -1))
			os.utime(dest_dir + '/' + zi.filename, (date_time, date_time))

def unzip_dlcs(src_dir, dest_dir):
	filenames = ls(src_dir, '', '.zip')
	for filename in filenames:
		try:
			unzip(src_dir + filename, dest_dir)
		except:
			#traceback.print_exc()
			logger.exception()

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
			if os.path.splitext(filename)[1] == '.dds':
				rescale_dds_wrapper(filename, src_dir, dest_dir)
				if os.path.exists(dest_file):
					os.utime(dest_file, (src_stat.st_atime, src_stat.st_mtime))
			elif os.path.splitext(filename)[1] == '.tga':
				rescale_tga_wrapper(filename, src_dir, dest_dir)
				if os.path.exists(dest_file):
					os.utime(dest_file, (src_stat.st_atime, src_stat.st_mtime))

DLC_DEST_DIR = DLC_GFX_HOME + os.pardir

# Remove temporary directory for extracted dlc files
shutil.rmtree(DLC_DEST_DIR, True)

if os.path.exists(INPUT_DLC_HOME):
	# Create temporary directory for extracted dlc files
	try:
		os.makedirs(DLC_DEST_DIR)
	except:
		pass

	unzip_dlcs(INPUT_DLC_HOME, DLC_DEST_DIR)
	directories = ls(INPUT_DLC_HOME, '', '')
	for directory in directories:
		DLC_SRC_DIR = INPUT_DLC_HOME + directory + "/"
		if os.path.isdir(DLC_SRC_DIR):
			unzip_dlcs(DLC_SRC_DIR, DLC_DEST_DIR)

try:
	for GFX_DIR in GFX_DIR_LIST:
		INPUT_PATH = INPUT_GFX_HOME + GFX_DIR
		OUTPUT_PATH = OUTPUT_GFX_HOME + GFX_DIR
		recursive_scale(TEMP_GFX_HOME + GFX_DIR, OUTPUT_PATH, INPUT_PATH)
		recursive_scale(INPUT_PATH, OUTPUT_PATH)
		recursive_scale(DLC_GFX_HOME + GFX_DIR, OUTPUT_PATH)
except:
	#traceback.print_exc()
	logger.exception()

# Remove temporary directory for extracted dlc files
shutil.rmtree(os.path.abspath(os.path.join(DLC_GFX_HOME, os.pardir)), True)

if trouble_list:
	logger.warning("Trouble files:")
	for trouble_file in trouble_list:
		logger.warning('\t' + trouble_file)