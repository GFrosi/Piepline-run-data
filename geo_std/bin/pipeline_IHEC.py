import sys
import os
import argparse


def main():

                
    to_name = args.json_name.split('.')[0]
    out_name = args.gse + '_' + to_name +'_ihec.sh'
    output = open(out_name, 'w')
                
    command_line = "#!/bin/bash\n\n\
module load singularity/3.7\n\
module load python/3.7.4\n\
module load java/1.8\n\n"

    command_ihec = "bash " + os.path.join(args.ihec,"piperunner_ihec_slurm_singularity.sh ")\
     +  args.json_name\
     + " slurm_singularity " + os.path.join(args.root_dir,"2021-GSE_batch4_relaunch",args.gse) #creating a sub dir per GSE 
                
    to_write = command_line + '\n' + command_ihec
    output.write(to_write)           
    output.close()

    print( to_write )



if __name__ == "__main__":
    parser = argparse.ArgumentParser(

            description="A tool to create the .sh file for each json for each series to the IHEC pipeline"
        )

    parser.add_argument('-i', '--ihec', action="store",
        
                            help='Absolute path to the piperunner_ihec_slurm_singularity.sh',
                            required=True
                            
                            )

    parser.add_argument('-g', '--gse', action="store",
        
                            help='the gse directory name',
                            required=True
                            
                            )

    parser.add_argument('-j', '--json_name', action="store",
        
                            help='The file name of the splitted json',
                            required=True
                            
                            )

   
    parser.add_argument('-r', '--root_dir', action="store",
        
                            help='Directory where the GSE Dir are',
                            required=True
                            
                            )

    args = parser.parse_args()

    main()


