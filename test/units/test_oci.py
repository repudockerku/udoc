#!/usr/bin/env python
"""
udocker unit tests: OciLocalFileAPI
"""
from udocker.oci import OciLocalFileAPI



# @patch('udocker.oci.FileUtil.isdir')
# @patch('udocker.oci.os.listdir')
# @patch('udocker.container.localrepo.LocalRepository.load_json')
# def test_02__load_structure(self, mock_ljson, mock_oslist, mock_isdir):
#     """Test02 OciLocalFileAPI()._load_structure."""
#     mock_ljson.side_effect = [[], []]
#     status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
#     self.assertEqual(status, {})

#     out_res = {'repolayers': {},
#                 'manifest': {},
#                 'oci-layout': 'oci_lay1',
#                 'index': 'idx1'}
#     mock_ljson.side_effect = ['oci_lay1', 'idx1']
#     mock_oslist.return_value = ['f1']
#     mock_isdir.return_value = False
#     status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
#     self.assertEqual(status, out_res)

#     out_res = {'repolayers': {'f1:f2': {'layer_a': 'f1',
#                                         'layer_f': 'tmpimg/blobs/f1/f2',
#                                         'layer_h': 'f2'}},
#                 'manifest': {},
#                 'oci-layout': 'oci_lay1',
#                 'index': 'idx1'}
#     mock_ljson.side_effect = ['oci_lay1', 'idx1']
#     mock_oslist.side_effect = [['f1'], ['f2']]
#     mock_isdir.return_value = True
#     status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
#     self.assertEqual(status, out_res)

# def test_03__get_from_manifest(self):
#     """Test03 OciLocalFileAPI()._get_from_manifest."""
#     imgtag = '123'
#     struct = {'manifest': {'123': {'json': {'layers': [{'digest': 'd1'},
#                                                         {'digest': 'd2'}],
#                                             'config': {'digest': 'dgt'}}}}}
#     lay_out = ['d2', 'd1']
#     conf_out = 'dgt'
#     status = OciLocalFileAPI(self.local)._get_from_manifest(struct, imgtag)
#     self.assertEqual(status, (conf_out, lay_out))

#     imgtag = ''
#     struct = dict()
#     ocilocal = OciLocalFileAPI(self.local)
#     self.assertEqual(ocilocal._get_from_manifest(struct, imgtag), ("", list()))

# # @patch('udocker.oci.Unique.imagename')
# # @patch('udocker.oci.Unique.imagetag')
# # @patch('udocker.container.localrepo.LocalRepository.load_json',autospec=True)
# # def test_04__load_manifest(self, mock_ljson, mock_uniqtag, mock_uniqname):
# #     """Test04 OciLocalFileAPI()._load_manifest."""
# #     manifest = {'annotations': {'org.opencontainers.image.ref.name': '123'},
# #                 'digest': {'layer_a': 'f1',
# #                            'layer_f': 'tmpimg/blobs/f1/f2',
# #                            'layer_h': 'f2'}}
# #     mock_uniqtag.return_value = '123'
# #     mock_uniqname.return_value = 'imgname'
# #     mock_ljson.return_value = {'layers': [{'digest': 'd1'},
# #                                           {'digest': 'd2'}],
# #                                'config': {'digest': 'dgt'}}
# #     struct = {'manifest': {'123': {'json': mock_ljson}},
# #               'repolayers': manifest}
# #     status = OciLocalFileAPI(self.local)._load_manifest(struct, manifest)
# #     self.assertEqual(status, (struct, "imgname", ['123']))

# # def test_05__load_repositories(self):
# #     """Test05 OciLocalFileAPI()._load_repositories."""

# # def test_06__load_image_step2(self):
# #     """Test07 OciLocalFileAPI()._load_image_step2."""

# @patch.object(OciLocalFileAPI, '_load_repositories')
# @patch.object(OciLocalFileAPI, '_load_structure')
# def test_07_load(self, mock_loadstruct, mock_loadrepo):
#     """Test07 OciLocalFileAPI().load."""
#     tmpdir = '/ROOT'
#     imgrepo = 'somerepo'
#     mock_loadstruct.return_value = {}
#     status = OciLocalFileAPI(self.local).load(tmpdir, imgrepo)
#     self.assertEqual(status, [])

#     tmpdir = '/ROOT'
#     imgrepo = 'somerepo'
#     mock_loadstruct.return_value = {'repolayers':
#                                         {'f1:f2': {'layer_a': 'f1',
#                                                     'layer_f': 'tmpimg/blobs/f1/f2',
#                                                     'layer_h': 'f2'}},
#                                     'manifest': {},
#                                     'oci-layout': 'oci_lay1',
#                                     'index': 'idx1'}
#     mock_loadrepo.return_value = ['r1', 'r2']
#     status = OciLocalFileAPI(self.local).load(tmpdir, imgrepo)
#     self.assertEqual(status, ['r1', 'r2'])