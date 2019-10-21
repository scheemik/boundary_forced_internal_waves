#!/bin/bash
# A bash script to run the Dedalus python code for a certain experiment
# Takes in arguments:
#	$ sh run.sh -n <name of experiment> <- not optional
#				-c <cores>
#				-l <local(1) or Niagara(0)>
#				-v <version: what scripts to run>

# if:
# VER = 0 (Full)
#	-> run the script, merge, plot frames, create gif, create mp4, etc
# VER = 1
#	-> run the script
# VER = 2
#	-> run the script, merge
# VER = 3
# 	-> merge, plot frames, and create a gif
# VER = 4
#	-> create mp4 from frames

while getopts n:c:l:v: option
do
	case "${option}"
		in
		n) NAME=${OPTARG};;
		c) CORES=${OPTARG};;
		l) LOC=${OPTARG};;
		v) VER=${OPTARG};;
	esac
done

# check to see if arguments were passed
if [ -z "$NAME" ]
then
	echo "-n, No name specified, aborting script"
	exit 1
fi
if [ -z "$CORES" ]
then
	CORES=2
	echo "-c, No number of cores specified, using CORES=$CORES"
fi
if [ -z "$LOC" ]
then
	LOC=1 # 1 if local, 0 if on Niagara
	echo "-l, No locality specified, using LOC=$LOC"
fi
if [ -z "$VER" ]
then
	VER=1
	echo "-v, No version specified, using VER=$VER"
fi

###############################################################################
echo ''
echo '--Checking experiment directory--'
echo ''
# Check if experiments folder exists
if [ -e _experiments ]
then
	echo 'Experiment folder exists'
else
	echo 'Experiment folder not found. Aborting script'
	exit 1
fi
# Check if this experiment has been created
if [ -e _experiments/$NAME ]
then
	echo "Experiment for $NAME exists"
else
	echo "Experiment for $NAME does not exist. Aborting script."
	exit 1
fi
# Check if this experiment has a run file
if [ -e _experiments/$NAME/run_${NAME}.sh ]
then
	echo "Executing experiment run file: run_${NAME}.sh"
	echo ''
	bash _experiments/$NAME/run_${NAME}.sh -n $NAME -c $CORES -l $LOC -v $VER
else
	echo 'Experiment run file does not exist. Aborting script'
	exit 1
fi
