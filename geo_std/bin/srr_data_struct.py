import pandas as pd
import sys
import argparse
import json
import os
import os.path
from pprint import pprint


def data_parse(file_n):
    '''Receives a table and returns two dicts. 
    The first one has the SRR related with each 
    IP samples as keys and a list of GSM of corresponding
    controls. The second ones has the GSM of each Input sample 
    as keys and a list of their SRR as values.'''
    
    file_hist = open(file_n, 'r')
    dict_srr_IP = {}
    dict_gsm_srr_ctrl = {}
    
    for i,line in enumerate(file_hist):
        if i == 0: #removing the header line
            continue
        
        line = line.strip()
        splited_table = line.split('\t')[1:] #removing index column; file separated by TAB
        splited_table[-2] = splited_table[-2].replace('"', '') #replacing "" by nothing; Corresponding Control column
        splited_table[19] = splited_table[19].replace('"', '') #SRR column

        if splited_table[-2] != 'NA': #removing inputs
            srr_ip = splited_table[19].split(',')[0] #getting just the first SRR (in this case, the first technical replicate to filter json)
            gsm_ctrl = splited_table[-2].split(',')
            dict_srr_IP[srr_ip] = gsm_ctrl

        else:
            srr_ctl = splited_table[19].split(',')[0]
            dict_gsm_srr_ctrl[splited_table[7]] = srr_ctl #getting each GSM cctrl from GSM column (individualy)

            
    file_hist.close()
    
    return dict_srr_IP, dict_gsm_srr_ctrl



def build_dict(dict_srr_IP, dict_gsm_srr_ctrl):
    '''Receives two dicts and returns a final dict 
    where the keys are the SRR of each IP samples, and the value
    is a list of SRR of their corresponding controls
    '''

    final_dict = {}

    for k,v in dict_srr_IP.items():
        for val in v:
            if k not in final_dict.keys():
                final_dict[k] = [dict_gsm_srr_ctrl[val]] #SRR from IP as key and SRR from GSEM cctrl as value
            
            else: 
                final_dict[k].append(dict_gsm_srr_ctrl[val])


    return final_dict


def open_json(file_n):
    '''load the json file'''

    with open(file_n) as f:
        json_full = json.load(f)
        
        return json_full
       

def create_json_struc(final_dict, list_json_stand, dict_ip_srr, list_ctrl_srr):
    '''receives a dict and three lists. Returns a list of list of tuples with 
    the IP sample from the json file and the correspondent inputs
    '''

    general_list = []
    ctrl_str_r1 = 'chip.ctl_fastqs_rep1_R1' #stand the key name for the json file (all rep 1)
    ctrl_str_r2 = 'chip.ctl_fastqs_rep1_R2' #stand the key name for the json file (all rep 1)

    for k,v in dict_ip_srr.items():
        # ctrl_dict_rep = {'R1': [], 'R2': [] }
        ctrl_dict_rep = {'R1': '', 'R2': '' }

        partial_list = list_json_stand.copy()
        for tup in v:
            tup = list(tup) #  convert to list to modify rep2, rep3 into rep1
            rep1 = 'rep1'
            rep = tup[0].split('_') #splitinng key name chip.fasta_rep5_R1
            rep[1] = rep1 #replacing other rep2, rep3, ... by rep1 string
            tup[0] = "_".join(rep)
            tup = tuple(tup) #stand the IP key for the json file (all rep 1)
            partial_list.append(tup) #IP 
    
        ip_path = v[0][1][0] #first path of each IP sample in case of more than one technical replicate
        srr_ip = os.path.basename(ip_path).split('_')[0] #gettin SRR IP
        srr_ctl = final_dict[srr_ip] #find cctrl for each IP 
             
        for ctrl in list_ctrl_srr:
            for ctrl_path in ctrl[1]:
                if  os.path.basename(ctrl_path).split('_')[0] in srr_ctl:
                    if 'R1' in ctrl[0]:
                        # ctrl_dict_rep['R1'].append(ctrl_path)
                        ctrl_dict_rep['R1'] = ctrl[1]

                    else: 
                        # ctrl_dict_rep['R2'].append(ctrl_path)
                        ctrl_dict_rep['R2'] = ctrl[1]

   
        r1_tup  = (ctrl_str_r1, ctrl_dict_rep['R1'])
        partial_list.append(r1_tup)
        
        if len(ctrl_dict_rep['R2']) > 0:
            r2_tup  = (ctrl_str_r2, ctrl_dict_rep['R2'])
            partial_list.append(r2_tup)

        general_list.append(partial_list)
    
    return general_list
 


def play_json(json_full, final_dict):

    '''Receives a json and a dict. It generates three lists of tuples. One list with stand keys and values from the json file. 
    The second one with the IP samples information (key and values), and the third one with the control information'''

    list_json_stand = []
    list_ctrl_srr = []
    dict_ip_srr = {}

    list_keys_stand = ['chip.always_use_pooled_ctl','chip.genome_tsv',
    'chip.paired_end','chip.ctl_paired_end','chip.pipeline_type',
    'chip.aligner','chip.title','chip.description']

    for k,v in json_full.items():         
        if k in list_keys_stand:
            list_json_stand.append((k,v)) #fixed information

        if 'chip.fastqs' in k:
            rep = k.split('_')[1] #get just SRR 
            if rep in dict_ip_srr.keys():
                dict_ip_srr[rep].append((k,v))
            else:
                dict_ip_srr[rep] = [(k,v)]

        if 'chip.ctl_fastqs' in k:
            list_ctrl_srr.append((k,v))


    return create_json_struc(final_dict, list_json_stand, dict_ip_srr, list_ctrl_srr)   


def write_json(general_list, root_dir, json_full):

    ctn = 0
    gse =  os.path.basename(json_full).split('_')[0]
    
    ctrl_paired  = 0 #paired end true or false
    ip_paired    = 0 #paired end true or false 
    
    for sublist in general_list:
        ctn+=1
        json_name = gse + '_' + str(ctn) + '.json'
        output = open(json_name, 'w')
        #output = open(os.path.join(root_dir, json_name), 'w')
        to_write = '{\n'

        for tup in sublist:
            if isinstance(tup[1], bool):
                to_write += '"' + tup[0] + '"' + ':' + str(tup[1]).lower() + ',\n'

            elif isinstance(tup[1], list):
                lista = ['"'+ x +'"' for x in tup[1]]
                to_write += '"' + tup[0] + '"' + ': [' + ",".join(lista) + '],\n'
            
            else:
                to_write += '"' + tup[0] + '"' + ':' + '"' + tup[1] + '"' + ',\n'

        
            if tup[0] in 'chip.fastqs_rep1_R2': #change to true - paired end key
                ip_paired = 1
            if tup[0] == 'chip.ctl_fastqs_rep1_R2': #change to true - paired end key
                ctrl_paired = 1
        
        
        to_write += '}'
        to_write = to_write.replace(',\n}','\n}')
        if ip_paired == 1:
            to_write = to_write.replace('"chip.paired_end":false,', '"chip.paired_end":true,') #replacing false by true
            ip_paired = 0
        if ctrl_paired == 1:
            to_write = to_write.replace('"chip.ctl_paired_end":false,', '"chip.ctl_paired_end":true,') #replacing false by true
            ctrl_paired = 0
        
        
        output.write(to_write)
        output.close()


def std_json_line(tup):

    to_write = ''

    if isinstance(tup[1], bool):
        to_write += '"' + tup[0] + '"' + ':' + str(tup[1]).lower() + ',\n'

    elif isinstance(tup[1], list):
        lista = ['"'+ x +'"' for x in tup[1]]
        to_write += '"' + tup[0] + '"' + ': [' + ",".join(lista) + '],\n'
            
    else:
        to_write += '"' + tup[0] + '"' + ':' + '"' + tup[1] + '"' + ',\n'

      
    return to_write
    

def generate_input_json(json_file):

    json_full = open_json(json_file)
    list_keys_stand = ['chip.always_use_pooled_ctl','chip.genome_tsv',
    'chip.paired_end','chip.ctl_paired_end','chip.pipeline_type',
    'chip.aligner','chip.title','chip.description']

    dict_of_inputs = {}
    to_write = ''
    ctrl_paired = 0


    gse =  os.path.basename(json_file).split('_')[0] 

    for k,v in json_full.items():
       if "chip.ctl_fastqs_rep" in k:

           rep = k.split("_")[2]
           if rep in dict_of_inputs.keys():
               dict_of_inputs[rep].append((k,v))
           else:
               dict_of_inputs[rep] = [(k,v)]

           
            # list_of_inputs.append((k,v))
            
            # if 'R2' in k:
            #     ctrl_paired = 1

    ctn = 1
    for rep, sample in dict_of_inputs.items():
        to_write += '{\n'
        if len(sample) > 1: #tuple with the chip_fastq_ctrl and the sample path
            ctrl_paired = 1
        
        for tup_input in sample:
            
            json_name = gse + '_' + str(ctn) + '.json'
            output = open(json_name, 'w')
            
            tup_input = list(tup_input)
            rep = tup_input[0].split('_') #splitinng key name chip.fasta_rep5_R1
            rep[2] = 'rep1' #replacing other rep2, rep3, ... by rep1 string
            tup_input[0] = "_".join(rep)
            tup_input = tuple(tup_input) #stand the IP key for the json file (all rep 1)

            
            to_write += std_json_line(tup_input)

            
        for k,v in json_full.items():
            if k in list_keys_stand:
                to_write += std_json_line((k,v))   
            
        if ctrl_paired == 1:
            to_write = to_write.replace('"chip.ctl_paired_end":false,', '"chip.ctl_paired_end":true,') #replacing false by true
            ctrl_paired = 0

        to_write += std_json_line(("chip.fastqs_rep1_R1", ["/home/frosig/scratch/chip-seq-ihec-test/SRR-samples/samples/2021_GSE_diff/GSE131583/data_srr/SRR11235536_1.fastq.gz"]))
        #to_write += std_json_line(("chip.fastqs_rep1_R2", ["/home/frosig/scratch/chip-seq-ihec-test/SRR-samples/samples/2021_GSE_diff/GSE131583/data_srr/SRR11235536_2.fastq.gz"]))
        to_write = to_write.replace('"chip.paired_end":false,', '"chip.paired_end":false,')

        to_write += '}'
        to_write = to_write.replace(',\n}','\n}')

        output.write(to_write)
        output.close()
        to_write= ''
        ctn += 1
            
    
def main():

    if not args.input_only:
        file_n = args.table
        dict_srr_IP, dict_gsm_srr_ctrl = data_parse(file_n)
        final_dict = build_dict(dict_srr_IP,dict_gsm_srr_ctrl)
        json_full = open_json(args.json)
        root_dir  = os.path.dirname(args.json)
        general_list = play_json(json_full, final_dict)
        write_json(general_list, root_dir,args.json)
    else:
        generate_input_json(args.json)
        



if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description="A tool to filter the json input for IHEC pipeline and return jsons for each IP sample with their respective corresponding controls"
    )

    parser.add_argument('-t', '--table', action="store",
    
                        help='The table generated by word_dist script (including corresponding control column). You should save a version separated by TAB',
                        required=True
                        
                        )

    parser.add_argument('-j', '--json', action="store",
    
                        help='The complete json file (all samples of each series) generated by chip-seq-json-generator script.',
                        required=True
                        
                        )

    parser.add_argument('-i', '--input_only', default=False, type=bool,
                         help='Generate the jsons with only inputs and a fake IP',
                         required=False
                        
                        )

    args = parser.parse_args()

    main()
