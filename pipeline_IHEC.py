import sys
import os
import argparse


def main():

    path_ihec = args.ihec
    path_gse = args.gse
    # list_dir_gse = next(os.walk(path_gse))[1] #os.listdir(path_gse)
    gse_list = open(args.list, 'r')
    path_out = args.out

    for line in gse_list:

        gse = line.strip()

        path_to_listdir = os.path.join(path_gse,gse) #list json
        list_dir = next(os.walk(path_to_listdir))[2]

        for json_ihec in list_dir:
            if 'json_' in json_ihec:
                
                to_name = json_ihec.split('.')[0]
                out_name = gse + '_' + to_name +'_ihec.sh'
                output = open(os.path.join(path_out,out_name), 'w')
                
                command_line = """#!/bin/bash
#SBATCH --time=4-00:00:00
#SBATCH --account=def-jacquesp
#SBATCH --cpus-per-task=4
#SBATCH --mem=5G
#SBATCH --mail-user=frog2901@usherbrooke.ca
#SBATCH --mail-type=FAIL
#SBATCH --output=%j-%x.slurm
#SBATCH --job-name=""" + gse + "\n\nmodule load singularity/3.7" + "\nmodule load python/3.7.4" + "\nmodule load java/1.8\n\n"

                command_ihec = "bash " + os.path.join(path_ihec,"piperunner_ihec_slurm_singularity.sh ")\
                    +  os.path.join(path_gse,gse,json_ihec)\
                    + " slurm_singularity " + os.path.join(path_out,"2021-GSE",gse) #creating a sub dir per GSE 
                
                to_write = command_line + '\n'
                # print(out_name)
                to_write += command_ihec
                output.write(to_write)
                
                output.close()




if __name__ == "__main__":

    parser = argparse.ArgumentParser(

            description="A tool to create the .sh file for each json for each series to the IHEC pipeline"
        )

    parser.add_argument('-i', '--ihec', action="store",
        
                            help='Absolute path to the piperunner_ihec_slurm_singularity.sh',
                            required=True
                            
                            )

    parser.add_argument('-g', '--gse', action="store",
        
                            help='Absolute path to the directory containing the gse directories',
                            required=True
                            
                            )

    parser.add_argument('-l', '--list', action="store",
        
                            help='List of GSEs in a txt file',
                            required=True
                            
                            )

                        
    parser.add_argument('-o', '--out', action="store",
        
                            help='Absolut path to the ihec.sh output',
                            required=True
                            
                            )




    args = parser.parse_args()

    main()


