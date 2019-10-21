#!/bin/bash
# A bash script to submit a job to Niagara
# Optionally takes in arguments:
#	$ sh submit_profile_job.sh -c <cores>
#                              -x <n_x>
#                              -z <n_z>

while getopts c:x:z: option
do
	case "${option}"
		in
		c) CORES=${OPTARG};;
		x) N_X=${OPTARG};;
		z) N_Z=${OPTARG};;
	esac
done

# check to see if arguments were passed
if [ -z "$CORES" ]
then
    CORES=40
	echo "No number of cores specified, using CORES=${CORES}"
fi
if [ -z "$N_X" ]
then
    N_X=280
	echo "No N_X value specified, using N_X=${N_X}"
fi
if [ -z "$N_Z" ]
then
    N_Z=80
	echo "No N_Z value specified, using N_Z=${N_Z}"
fi

# Prepare scratch

DATE=`date +"%m-%d_%Hh%M"`
NAME="${N_X}x${N_Z}"
# create a 2 digit version of CORES
#printf -v CO "%02d" $CORES
JOBNAME="${DATE}_${NAME}-2D_RB"
#JOBNAME="$DATE-2D_RB-n$CO"
DIRECTORY='Dedalus/Stack_test'
SUBDIRECT='template_dedalus_repository'
RUN_DIR='runs'

set -x # echos each command as it is executed

# Go into directory of job to run
cd ${HOME}/${DIRECTORY}/${SUBDIRECT}
# Pull from github the latest version of that project
git pull
# Copy that into the scratch directory
cp -r ${HOME}/${DIRECTORY}/${SUBDIRECT} ${SCRATCH}/${DIRECTORY}/${RUN_DIR}
mv ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${SUBDIRECT} ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${JOBNAME}
cd ${SCRATCH}/${DIRECTORY}/${RUN_DIR}/${JOBNAME}

# Submit the job
sbatch --job-name=$JOBNAME lanceur.slrm -c $CORES -n $NAME -x $N_X -z $N_Z

# Check the queue
squeue -u mschee

echo 'Done'
