#!/usr/bin/env nextflow

gseList = params.gseList
runDir = params.runDir
metaData = params.metaData
chipSeqJsonSrc = params.chipSeqJsonSrc
jsonSplitterSrc = params.jsonSplitterSrc
singularityWrapper = params.singularityWrapper
slurm_out = params.slurm_out
projectDir = params.projectDir


Channel
    .fromPath(gseList)
    .splitText()
    .set{ gseCh }


/*
    Parse list of GSE IDs
*/
process echoGse{
    input:
    val x from gseCh

    output:
    path '*.txt' into samplesCh                

    """ 
        a=\$(awk 'l=length(\$0) {print substr(\$0, 0, l )}' <<< ${x})
        echo \$a > \$a.txt
    """
}


/*
    Generate the bash file to split Json
*/
process createSplitScript{
    
    tag "${gseId.baseName}"
    publishDir "$runDir" + "${gseId.baseName}", mode: 'symlink'
    
    input:
    file gseId from samplesCh
                         
    output:    
    tuple path("${gseId.baseName}.sh"), val("${gseId.baseName}")  into splitJson


    """
      python ${projectDir}bin/pipeline_json.py -l ${gseId.baseName} -c ${chipSeqJsonSrc} -m  ${metaData} -p ${runDir} -g ${jsonSplitterSrc} > ${gseId.baseName}.sh

    """
}


/*
    Split the large Json into one json per sample
*/
process SplitJson{ 

    tag "$gseId"
    publishDir "$runDir" + "$gseId", mode: 'symlink'
    module 'python/3.7'

    input:
    tuple path(bashFile), val(gseId) from splitJson

    output:
    path "*.json" into jsonCh
     
    """
      bash $bashFile
    """

}


/*
    Generate the bash file to Ihec pipeline
*/
process createIhecScript{
   
   tag "$gseId"
   module 'python/3.7'

   input:
   path(jsonFile) from jsonCh
                            .flatten()
                            
   output:
   tuple path("*_ihec.sh"), path(jsonFile), val(gseId) into ihecLaucher  

   script:
   gseId = jsonFile.toString().split('_')[0] 
 
   """
    python ${projectDir}bin/pipeline_IHEC.py -i ${singularityWrapper} -g ${gseId} -j ${jsonFile} -r ${runDir} > ${gseId}_${jsonFile.baseName}_ihec.sh
   
   """

}


/*
    Launch the IhecPipeline
*/
process runIhecPipeline{

    tag "$gseId"
    label "IhecPipe"
    
    input:
    tuple path(ihecBash), path(jsonFile), val(gseId)  from ihecLaucher
    
    """
        bash $ihecBash

        echo Done > ${gseId}.done
    """
} 


