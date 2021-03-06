"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import tempfile

from . import config
from . import shared


def visualise(ssu_or_lsu, fasta_input, output_folder, rnacentral_id, model_id):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if ssu_or_lsu.lower() == 'lsu':
        cm_library = config.RIBOVISION_LSU_CM_LIBRARY
        templates = config.RIBOVISION_LSU_TRAVELER
        bpseq = config.RIBOVISION_LSU_BPSEQ
    elif ssu_or_lsu.lower() == 'ssu':
        cm_library = config.RIBOVISION_SSU_CM_LIBRARY
        templates = config.RIBOVISION_SSU_TRAVELER
        bpseq = config.RIBOVISION_SSU_BPSEQ
    elif ssu_or_lsu.lower() == 'rnasep':
        cm_library = config.RNASEP_CM_LIBRARY
        templates = config.RNASEP_TRAVELER
        bpseq = config.RNASEP_BPSEQ
    else:
        print('Please specify LSU or SSU')
        return

    temp_fasta = tempfile.NamedTemporaryFile()
    temp_sto = tempfile.NamedTemporaryFile()
    temp_stk = tempfile.NamedTemporaryFile()
    temp_pfam_stk = tempfile.NamedTemporaryFile(delete=False)
    temp_afa = tempfile.NamedTemporaryFile()
    temp_map = tempfile.NamedTemporaryFile()

    cmd = 'esl-sfetch %s %s > %s' % (fasta_input, rnacentral_id, temp_fasta.name)
    result = os.system(cmd)
    if result:
        raise ValueError("Failed esl-sfetch for: %s" % rnacentral_id)

    model_path = os.path.join(cm_library, model_id + '.cm')
    if not os.path.exists(model_path):
        print('Model not found %s' % model_path)
        return
    cm_options = ['', '--mxsize 2048 --maxtau 0.49']
    for options in cm_options:
        cmd = "cmalign %s %s %s > %s" % (options, model_path, temp_fasta.name, temp_sto.name)
        result = os.system(cmd)
        if not result:
            break
    else:
        print("Failed cmalign of %s to %s" % (rnacentral_id, model_id))
        return

    cmd = 'esl-alimanip --rna --sindi --outformat pfam {} > {}'.format(temp_sto.name, temp_stk.name)
    result = os.system(cmd)
    if result:
        print("Failed esl-alimanip for %s %s" % (rnacentral_id, model_id))
        return

    cmd = 'ali-pfam-lowercase-rf-gap-columns.pl {} > {}'.format(temp_stk.name, temp_pfam_stk.name)
    result = os.system(cmd)
    if result:
        raise ValueError("Failed ali-pfam-lowercase-rf-gap-columns for %s %s" % (rnacentral_id, model_id))

    shared.remove_large_insertions_pfam_stk(temp_pfam_stk.name)

    cmd = 'ali-pfam-sindi2dot-bracket.pl -l -n -w -a -c {} > {}'.format(temp_pfam_stk.name, temp_afa.name)
    result = os.system(cmd)
    if result:
        raise ValueError("Failed ali-pfam-sindi2dot-bracket for %s %s" % (rnacentral_id, model_id))

    cmd = '/rna/python36/bin/python3.6 /rna/traveler/utils/infernal2mapping.py -i {} > {}'.format(temp_afa.name, temp_map.name)
    result = os.system(cmd)
    if result:
        raise ValueError("Failed infernal2mapping for %s" % (cmd))

    cmd = 'ali-pfam-sindi2dot-bracket.pl %s > %s/%s-%s.fasta' % (temp_pfam_stk.name, output_folder, rnacentral_id.replace('/', '_'), model_id)
    result = os.system(cmd)
    if result:
        print("Failed esl-pfam-sindi2dot-bracket for %s %s" % (rnacentral_id, model_id))
        return

    result_base = os.path.join(output_folder, '{rnacentral_id}-{model_id}'.format(
        rnacentral_id=rnacentral_id.replace('/', '_'),
        model_id=model_id,
    ))

    log = result_base + '.log'
    cmd = ('traveler '
           '--verbose '
           '--target-structure {result_base}.fasta '
           '--template-structure --file-format traveler {traveler_templates}/{model_id}.tr {ribovision_bpseq}/{model_id}.fasta '
           '--draw {map} {result_base} > {log}').format(
               result_base=result_base,
               model_id=model_id,
               traveler_templates=templates,
               ribovision_bpseq=bpseq,
               log=log,
               map=temp_map.name
           )
    print(cmd)
    result = os.system(cmd)

    if result:
        print('Repeating using Traveler mapping')
        cmd = ('traveler '
               '--verbose '
               '--target-structure {result_base}.fasta '
               '--template-structure --file-format traveler {traveler_templates}/{model_id}.tr {ribovision_bpseq}/{model_id}.fasta '
               '--all {result_base} > {log}').format(
                   result_base=result_base,
                   model_id=model_id,
                   traveler_templates=templates,
                   ribovision_bpseq=bpseq,
                   log=log
               )
        print(cmd)
        os.system(cmd)

    temp_fasta.close()
    temp_sto.close()
    temp_stk.close()
    temp_pfam_stk.close()
    temp_afa.close()
    temp_map.close()
    os.remove(temp_pfam_stk.name)

    overlaps = 0
    with open(log, 'r') as raw:
        for line in raw:
            match = re.search(r'Overlaps count: (\d+)', line)
            if match:
                if overlaps:
                    print('ERROR: Saw too many overlap counts')
                    break
                overlaps = int(match.group(1))

    with open(result_base + '.overlaps', 'w') as out:
        out.write(str(overlaps))
        out.write('\n')
    if ssu_or_lsu != 'rnasep':
        adjust_font_size(result_base)


def adjust_font_size(result_base):
    filenames = [result_base + '.colored.svg', result_base + '.svg']
    for filename in filenames:
        if not os.path.exists(filename):
            continue
        cmd = """sed -i 's/font-size: 7px;/font-size: 4px;/' {}""".format(filename)
        os.system(cmd)
