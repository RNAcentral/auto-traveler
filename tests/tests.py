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

import filecmp
import os
import unittest

from utils import config, rfam


EXECUTABLE = os.path.join(config.PROJECT_HOME, 'r2dt.py')

# @unittest.skip("")
class TestCovarianceModelDatabase(unittest.TestCase):

    @staticmethod
    def count_lines(filename):
        with open(filename) as f_modelinfo:
            num_lines = sum(1 for line in f_modelinfo)
        return num_lines

    @staticmethod
    def counts_cms(folder):
        return len([name for name in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder,name))
                       and name.endswith('.cm')])

    def verify_cm_database(self, location, count):
        print('Verifying models in {}'.format(location))
        modelinfo = os.path.join(location, 'modelinfo.txt')
        all_cm = os.path.join(location, 'all.cm')
        num_lines = self.count_lines(modelinfo)
        num_cms = self.counts_cms(location)
        self.assertTrue(os.path.exists(modelinfo), 'A required file modelinfo.txt does not exist')
        self.assertTrue(os.path.exists(all_cm), 'A required file all.cm does not exist')
        self.assertEqual(num_lines, num_cms, 'The number of lines in modelinfo.txt file does not match the number of covariance model files')
        self.assertEqual(num_cms, count, 'The number of CMs does not match')

    def test_crw_database(self):
        self.verify_cm_database(config.CRW_CM_LIBRARY, 884)

    def test_ribovision_lsu_database(self):
        self.verify_cm_database(config.RIBOVISION_LSU_CM_LIBRARY, 21)

    def test_ribovision_ssu_database(self):
        self.verify_cm_database(config.RIBOVISION_SSU_CM_LIBRARY, 10)

    def test_rnasep_cm_database(self):
        self.verify_cm_database(config.RNASEP_CM_LIBRARY, 20)

    def test_rfam_database(self):
        for rfam_acc in rfam.get_all_rfam_acc():
            if rfam_acc in rfam.blacklisted():
                continue
            template = rfam.get_traveler_template_xml(rfam_acc)
            self.assertTrue(os.path.exists(template), '{} not found'.format(template))
            fasta = rfam.get_traveler_fasta(rfam_acc)
            self.assertTrue(os.path.exists(fasta), '{} not found'.format(fasta))
            cm = rfam.get_rfam_cm(rfam_acc)
            self.assertTrue(os.path.exists(cm), '{} not found'.format(cm))


# @unittest.skip("")
class TestRibovisionLSU(unittest.TestCase):
    fasta_input = os.path.join('examples', 'lsu-small-example.fasta')
    test_results = os.path.join('tests', 'results', 'ribovision')
    precomputed_results = os.path.join('tests', 'examples', 'ribovision')
    cmd = 'python3 {} ribovision draw_lsu {} {}'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'hits.txt',
        'URS000080E357_9606-mHS_LSU_3D.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestRibovisionSSU(unittest.TestCase):
    fasta_input = os.path.join('examples', 'ribovision-ssu-examples.fasta')
    test_results = os.path.join('tests', 'results', 'ribovision-ssu')
    precomputed_results = os.path.join('tests', 'examples', 'ribovision-ssu')
    cmd = 'python3 {} ribovision draw_ssu {} {}'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'hits.txt',
        'URS00002A2E83_10090-HS_SSU_3D.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestRfam(unittest.TestCase):
    rfam_acc = 'RF00162'
    fasta_input = os.path.join('examples', rfam_acc + '.example.fasta')
    test_results = os.path.join('tests', 'results', 'rfam')
    precomputed_results = os.path.join('tests', 'examples', 'rfam', rfam_acc)
    cmd = 'python3 {} rfam draw {} {} {}'.format(EXECUTABLE, rfam_acc, fasta_input, test_results)
    files = [
        'URS00001D0AD3_224308-RF00162.colored.svg',
        'URS00002D29F6_224308-RF00162.colored.svg',
        'URS00002F3927_224308-RF00162.colored.svg',
        'URS000053CEAC_224308-RF00162.colored.svg',
        'URS000008638F_224308-RF00162.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, self.rfam_acc, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestCrw(unittest.TestCase):
    label = 'crw'

    fasta_input = os.path.join('examples', label + '-examples.fasta')
    test_results = os.path.join('tests', 'results', label)
    precomputed_results = os.path.join('tests', 'examples', label)
    cmd = 'python3 {} crw draw {} {}'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'hits.txt',
        'URS00000F9D45_9606-d.5.e.H.sapiens.2.colored.svg',
        'URS000044DFF6_9606-d.16.m.H.sapiens.5.colored.svg',
        'URS000001AE2D_4932-d.16.e.S.cerevisiae.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file), 'File {} does not exist'.format(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestSingleEntry(unittest.TestCase):
    fasta_input = os.path.join('examples', 'examples.fasta')
    test_results = os.path.join('tests', 'results', 'single-entry')
    precomputed_results = os.path.join('tests', 'examples', 'single-entry')
    cmd = 'python3 {} draw {} {}'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'URS00000F9D45_9606-d.5.e.H.sapiens.2.colored.svg',
        'URS000044DFF6_9606-d.16.m.H.sapiens.5.colored.svg',
        'URS000053CEAC_224308-RF00162.colored.svg',
        'URS0000162127_9606-RF00003.colored.svg',
        'URS000080E357_9606-mHS_LSU_3D.colored.svg',
        'URS0000023412_9606-E_Thr.colored.svg',
        'URS00000012EC-RF00005.colored.svg',
        'URS0000664B0C_4896-RNAseP_e_S_pombe_JB.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, 'results', 'svg', filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file), 'File {} does not exist'.format(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestGtrnadbDomainIsotype(unittest.TestCase):
    trnascan_model = 'E_Thr'
    fasta_input = os.path.join('examples', 'gtrnadb.{}.fasta'.format(trnascan_model))
    test_results = os.path.join('tests', 'results', 'gtrnadb')
    precomputed_results = os.path.join('tests', 'examples', 'gtrnadb', trnascan_model)
    cmd = 'python3 {} gtrnadb draw {} {} --domain E --isotype Thr'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'URS0000023412_9606-E_Thr.colored.svg',
        'URS000021550A_9606-E_Thr.colored.svg',
        'URS00000A1A88_9606-E_Thr.colored.svg',
        'URS00000F30A4_9606-E_Thr.colored.svg',
        'URS00001D9AFB_9606-E_Thr.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, self.trnascan_model, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file), 'File {} does not exist'.format(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)

# @unittest.skip("")
class TestRnasep(unittest.TestCase):
    fasta_input = os.path.join('examples', 'rnasep.fasta')
    test_results = os.path.join('tests', 'results', 'rnasep')
    precomputed_results = os.path.join('tests', 'examples', 'rnasep')
    cmd = 'python3 {} rnasep draw {} {}'.format(EXECUTABLE, fasta_input, test_results)
    files = [
        'hits.txt',
        'URS00000A7310_29284-RNAseP_a_H_trapanicum_JB.colored.svg',
        'URS0000CBCB35_210-RNAseP_b_H_pylory_26695_JB.colored.svg',
        'URS0000EEAD19_2190-RNAseP_a_M_jannaschii_JB.colored.svg',
        'URS0001BC2932_272844-RNAseP_a_P_abyssi_JB.colored.svg',
        'URS0001BC3468_782-RNAseP_b_R_prowazekii_JB.colored.svg',
        'URS00003C82BC_186497-RNAseP_a_P_furiosus_JB.colored.svg',
        'URS00004BB8BB_511145-RNAseP_b_E_coli_JB.colored.svg',
        'URS00006A4F8D_64091-RNAseP_a_Halobacterium-NRC1_JB.colored.svg',
        'URS00006D6BE6_273075-RNAseP_a_T_acidophilum_JB.colored.svg',
        'URS00006E8172_2285-RNAseP_a_S_acidocaldarius_JB.colored.svg',
        'URS00019F4D0F_358-RNAseP_b_A_tumefaciens_JB.colored.svg',
        'URS00019F2369_1773-RNAseP_b_M_tuberculosis_JB.colored.svg',
        'URS000066E9AE_2287-RNAseP_a_S_solfataricus_JB.colored.svg',
        'URS000072E054_1095685-RNAseP_N_gonnorhoeae_JB.colored.svg',
        'URS0000637B30_1247414-RNAseP_N_gonnorhoeae_JB.colored.svg',
        'URS0000664B0C_4896-RNAseP_e_S_pombe_JB.colored.svg',
        'URS000013F331_9606-RNAseP_e_H_sapiens_3D.colored.svg',
    ]

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        os.system(self.cmd)

    def test_examples(self):
        for filename in self.files:
            new_file = os.path.join(self.test_results, filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)


class TestForceTemplate(unittest.TestCase):
    fasta_input = os.path.join('examples', 'force')
    test_results = os.path.join('tests', 'results', 'force')
    precomputed_results = os.path.join('tests', 'examples', 'force')
    cmd = 'r2dt.py draw --force_template {} {} {}'
    cases = {
        'URS00000F9D45_9606': 'd.5.b.E.coli', # CRW: human 5S with E. coli 5S
        'URS0000704D22_9606': 'EC_SSU_3D', # RiboVision SSU: Human SSU with E.coli
        'URS000020CCFC_274': 'EC_LSU_3D', # RiboVision LSU: T. thermophilus with E.coli
        'URS00000A1A88_9606': 'B_Thr', # GtRNAdb: human E_Thr with B_Thr
        'URS00000A1A88_9606': 'RF00005', # GtRNAdb E_Thr using Rfam tRNA
        'URS0001BC2932_272844': 'RNAseP_a_P_furiosus_JB', # RNAse P: Pyrococcus abyssi with P.furiosus
    }

    @staticmethod
    def delete_folder(folder):
        os.system('rm -Rf {}'.format(folder))

    def setUp(self):
        self.delete_folder(self.test_results)
        for seq_id, model_id in self.cases.items():
            input_fasta = os.path.join(self.fasta_input, seq_id + '.fasta')
            os.system(self.cmd.format(model_id, input_fasta, self.test_results))

    def test_examples(self):
        for seq_id, model_id in self.cases.items():
            filename = '{}-{}.colored.svg'.format(seq_id, model_id)
            new_file = os.path.join(self.test_results, 'results', 'svg', filename)
            reference_file = os.path.join(self.precomputed_results, filename)
            self.assertTrue(os.path.exists(new_file), 'File {} does not exist'.format(new_file))
            self.assertTrue(filecmp.cmp(new_file, reference_file), 'File {} does not match'.format(new_file))

    def tearDown(self):
        self.delete_folder(self.test_results)


if __name__ == '__main__':
    unittest.main()
