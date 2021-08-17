import os
import sys


'''script to create the SE and PE lists. Necessary to adjust the config file'''



def main():

    list_gse = open(sys.argv[1]) #GSE list so far (49)
    root_path = sys.argv[2] #path to GSEs dir

    list_SE = []
    list_PE = []

    for gse in list_gse:
        
        gse = gse.strip()
        path_check = os.path.join(root_path,gse,'data_srr')
        # path_to_move = os.path.join(root_path,gse) #to generate a list of path for each series in case to mv some files
        # print(path_to_move)
        
        list_dir = os.listdir(path_check)

        for srr in list_dir:

            if "_2.fastq.gz" in srr:
                list_PE.append(gse)
            
            if "_2.fastq.gz" not in srr:
                list_SE.append(gse)
                
    print(len(list(set(list_PE))))
    print(len(list(set(list_SE)))) #to adjust

    just_single = list(set(list_SE) - set(list_PE))

    print(just_single)
    # sys.exit()


    output_se = open('SE_gses.txt', 'w')
    output_se.write('\n'.join(just_single))
    output_se.close()



if __name__ == "__main__":


    main()