#!/bin/bash
# A bash script to update the other modules for an experiment
# Takes in argument:
#	$ sh make_new_experiment.sh -n <name of experiment>

code_file='core_code.py'
o_mod_dir='_modules_other'

# Parse arguments
while getopts n: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
	esac
done

# Generate datetime string
DATETIME=`date +"%m-%d_%Hh%M"`

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No experiment name specified. Aborting script"
	exit 1
fi

###############################################################################
echo ''
echo '--Updating other modules--'
echo ''
# Check if experiment directory exists
if [ -e ${o_mod_dir} ]
then
	echo 'Found other modules'
else
	echo 'Other modules not found. Aborting script'
fi
# Check if an experiment under this name has already been generated
if [ -e _experiments/${NAME} ]
then
	echo 'Experiment found'
else
	echo "Experiment ${NAME} not found. Aborting script"
	exit 1
fi
# Check if there is an old other module directory
if [ -e _experiments/${NAME}/${o_mod_dir} ]
then
	echo 'Removing old other modules'
	rm -rf _experiments/${NAME}/${o_mod_dir}
	cp -r ${o_mod_dir} _experiments/${NAME}
	echo "Copied new other modules to ${NAME}"
else
	echo 'Old other modules not found. Aborting script'
	exit 1
fi

echo "Done updating other modules for ${NAME}"
