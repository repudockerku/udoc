#!/usr/bin/env python
"""
udocker unit tests: FileUtil
"""
import sys
import pytest
from udocker.utils.fileutil import FileUtil

STDOUT = sys.stdout
STDERR = sys.stderr
UDOCKER_TOPDIR = "test_topdir"
BUILTINS = "builtins"


def find_str(self, find_exp, where):
    """Find string in test output messages."""
    found = False
    for item in where:
        if find_exp in str(item):
            self.assertTrue(True)
            found = True
            break
    if not found:
        self.assertTrue(False)


def is_writable_file(obj):
    """Check if obj is a file."""
    try:
        obj.write("")
    except (AttributeError, OSError, IOError):
        return False
    else:
        return True


@pytest.fixture
def futil(mocker):
    mock_absp = mocker.patch('os.path.abspath', return_value='/dir/somefile')
    mock_base = mocker.patch('os.path.basename', return_value='somefile')
    mock_regpre = mocker.patch.object(FileUtil, '_register_prefix')
    return FileUtil('somefile')


def test_01_init(mocker):
    """Test01 FileUtil() constructor."""
    mock_absp = mocker.patch('os.path.abspath', return_value='/dir/somefile')
    mock_base = mocker.patch('os.path.basename', return_value='somefile')
    mock_regpre = mocker.patch.object(FileUtil, '_register_prefix')
    fileutil = FileUtil('somefile')
    assert fileutil.filename == '/dir/somefile'
    mock_absp.assert_called()
    mock_base.assert_called()
    mock_regpre.assert_called()


def test_02_init(mocker):
    """Test02 FileUtil() constructor."""
    mock_absp = mocker.patch('os.path.abspath')
    mock_base = mocker.patch('os.path.basename')
    mock_regpre = mocker.patch.object(FileUtil, '_register_prefix')
    fileutil = FileUtil('-')
    assert fileutil.filename == '-'
    mock_absp.assert_not_called()
    mock_base.assert_not_called()
    mock_regpre.assert_not_called()


data_regp = (('/dir1', '/dir1', ['/dir1', '/dir1', '/dir1', '/dir1'], True, False,
              ['/tmp/', '/tmp/', '/tmp/', '/tmp/', '/some_contdir', '/some_contdir',
               '/home/.udocker/containers/123', '/home/.udocker/containers/123', '/dir1/',
               '/dir1/', '/dir1/', '/dir1/']),
             ('file1', '/dir1/file1', ['/dir1/file1', '/dir1/file1', '/dir1/file1', '/dir1/file1'],
              False, False,
              ['/tmp/', '/tmp/', '/tmp/', '/tmp/', '/some_contdir', '/some_contdir',
               '/home/.udocker/containers/123', '/home/.udocker/containers/123', '/dir1/',
               '/dir1/', '/dir1/', '/dir1/', '/dir1/file1', '/dir1/file1']))


@pytest.mark.parametrize("ftype,abspath,rpathsd,risdir,rislink,expected", data_regp)
def test_03_register_prefix(mocker, ftype, abspath, rpathsd, risdir, rislink, expected):
    """Test03 FileUtil.register_prefix()."""
    mock_absp = mocker.patch('os.path.abspath', return_value=abspath)
    mock_base = mocker.patch('os.path.basename', return_value=ftype)
    mock_rpath = mocker.patch('os.path.realpath', side_effect=rpathsd)
    mock_isdir = mocker.patch('os.path.isdir', return_value=risdir)
    mock_islink = mocker.patch('os.path.islink', return_value=rislink)
    fileutil = FileUtil(ftype)
    fileutil.register_prefix()
    assert fileutil.safe_prefixes == expected
    mock_absp.assert_called()
    mock_base.assert_called()
    mock_rpath.assert_called()
    mock_isdir.assert_called()
    mock_islink.assert_called()


def test_04_umask(futil, mocker):
    """Test04 FileUtil.umask()."""
    mock_umask = mocker.patch('os.umask', return_value=0)
    resout = futil.umask()
    assert resout
    mock_umask.assert_called()


def test_05_umask(futil, mocker):
    """Test05 FileUtil.umask()."""
    mock_umask = mocker.patch('os.umask', return_value=1)
    resout = futil.umask(1)
    assert resout
    assert futil.orig_umask == 1
    mock_umask.assert_called()


def test_06_umask(futil, mocker):
    """Test06 FileUtil.umask()."""
    mock_umask = mocker.patch('os.umask', side_effect=TypeError('fail'))
    resout = futil.umask()
    assert not resout
    mock_umask.assert_called()


def test_07_umask(futil, mocker):
    """Test07 FileUtil.umask()."""
    mock_umask = mocker.patch('os.umask', side_effect=TypeError('fail'))
    resout = futil.umask(1)
    assert not resout
    mock_umask.assert_called()


def test_08_mktmp(futil, mocker):
    """Test08 FileUtil.mktmp()."""
    mock_uniqf = mocker.patch('udocker.utils.fileutil.Unique.filename', return_value='fname213')
    mock_exists = mocker.patch('os.path.exists', return_value=False)
    resout = futil.mktmp()
    assert resout == '/tmp/fname213'
    assert futil.tmptrash['/tmp/fname213']
    mock_uniqf.assert_called()
    mock_exists.assert_called()


def test_09_mkdir(futil, mocker):
    """Test09 FileUtil.mkdir()"""
    mock_mkdirs = mocker.patch('os.makedirs')
    resout = futil.mkdir()
    assert resout
    mock_mkdirs.assert_called()


def test_10_mkdir(futil, mocker):
    """Test10 FileUtil.mkdir()"""
    mock_mkdirs = mocker.patch('os.makedirs', side_effect=OSError('fail'))
    resout = futil.mkdir()
    assert not resout
    mock_mkdirs.assert_called()


def test_11_rmdir(futil, mocker):
    """Test11 FileUtil.rmdir()"""
    mock_rmdir = mocker.patch('os.rmdir')
    resout = futil.rmdir()
    assert resout
    mock_rmdir.assert_called()


def test_12_rmdir(futil, mocker):
    """Test12 FileUtil.rmdir()"""
    mock_rmdir = mocker.patch('os.rmdir', side_effect=OSError('fail'))
    resout = futil.rmdir()
    assert not resout
    mock_rmdir.assert_called()


data_mk = ((True, 'somedir'),
           (False, None))


@pytest.mark.parametrize("rmkdir,expected", data_mk)
def test_13_mktmpdir(futil, mocker, rmkdir, expected):
    """Test13 FileUtil.mktmpdir()."""
    mock_mkdir = mocker.patch.object(FileUtil, 'mkdir', return_value=rmkdir)
    mock_mktmp = mocker.patch.object(FileUtil, 'mktmp', return_value='somedir')
    resout = futil.mktmpdir()
    assert resout == expected
    mock_mkdir.assert_called()
    mock_mktmp.assert_called()


def test_14_uid(futil, mocker):
    """Test14 FileUtil.uid()."""
    mock_lstat = mocker.patch('os.lstat')
    mock_lstat.return_value.st_uid = 1234
    resout = futil.uid()
    assert resout == 1234
    mock_lstat.assert_called()


def test_15_uid(futil, mocker):
    """Test15 FileUtil.uid()."""
    mock_lstat = mocker.patch('os.lstat', side_effect=OSError('fail'))
    resout = futil.uid()
    assert resout == -1


data_spref = (('/bin', ['/bin'], ['/bin', '/bin'], True, False, True),
              ('ls', ['/bin/ls'], ['/bin/ls', '/bin/ls'], False, False, True),
              ('link', ['/bin/link'], ['/bin/link', '/bin/link'], False, True, True))


@pytest.mark.parametrize("fname,safep,rpathsd,risdir,rislink,expected", data_spref)
def test_16__is_safe_prefix(futil, mocker, fname, safep, rpathsd, risdir, rislink, expected):
    """Test16 FileUtil._is_safe_prefix()."""
    mock_base = mocker.patch('os.path.basename', return_value=fname)
    mock_rpath = mocker.patch('os.path.realpath', side_effect=rpathsd)
    mock_isdir = mocker.patch('os.path.isdir', return_value=risdir)
    mock_islink = mocker.patch('os.path.islink', return_value=rislink)
    futil.safe_prefixes = safep
    resout = futil._is_safe_prefix(fname)
    assert resout == expected
    mock_rpath.assert_called()
    mock_isdir.assert_called()
    mock_islink.assert_called()


def test_17_chown(futil, mocker):
    """Test17 FileUtil.chown()."""
    mock_lchown = mocker.patch('os.lchown')
    resout = futil.chown(0, 0, False)
    assert resout
    mock_lchown.assert_called()


def test_18_chown(futil, mocker):
    """Test18 FileUtil.chown()."""
    mock_lchown = mocker.patch('os.lchown', side_effect=[None, None, None, None])
    mock_walk = mocker.patch('os.walk', return_value=[("/tmp", ["dir"], ["file"]), ])
    resout = futil.chown(0, 0, True)
    assert resout
    mock_lchown.assert_called()
    mock_walk.assert_called()


def test_19_chown(futil, mocker):
    """Test19 FileUtil.chown()."""
    mock_lchown = mocker.patch('os.lchown', side_effect=OSError("fail"))
    resout = futil.chown(0, 0, False)
    assert not resout
    mock_lchown.assert_called()


def test_20_rchown(futil, mocker):
    """Test20 FileUtil.rchown()."""
    mock_fuchown = mocker.patch.object(FileUtil, 'chown', return_value=True)
    assert futil.rchown()
    mock_fuchown.assert_called()


# def test_21__chmod(futil, mocker):
#     """Test21 FileUtil._chmod()."""
#     mock_lstat = mocker.patch('os.lstat')
#     mock_stat = mocker.patch('stat')
#     mock_chmod = mocker.patch('os.chmod')
#     mock_lstat.return_value.st_mode = 33277
#     mock_stat.return_value.S_ISREG = True
#     mock_stat.return_value.S_ISDIR = False
#     mock_stat.return_value.S_ISLNK = False
#     mock_stat.return_value.S_IMODE = 509
#     futil._chmod("somefile")
#     mock_lstat.assert_called()
#     mock_stat.S_ISREG.assert_called()
#     mock_stat.S_IMODE.assert_called()


def test_22__chmod(futil, mocker):
    """Test22 FileUtil._chmod()."""
    mock_lstat = mocker.patch('os.lstat', side_effect=OSError('fail'))
    futil._chmod("somefile")
    mock_lstat.assert_called()


def test23_chmod(futil, mocker):
    """Test23 FileUtil.chmod()."""
    mock_walk = mocker.patch('os.walk', return_value=[("/tmp", ["dir"], ["file"]), ])
    mock_fuchmod = mocker.patch.object(FileUtil, '_chmod', side_effect=[None, None, None, None])
    futil.safe_prefixes = ["/tmp"]
    resout = futil.chmod(0o600, 0o700, 0o755, True)
    assert resout
    mock_fuchmod.assert_called()
    mock_walk.assert_called()


def test24_chmod(futil, mocker):
    """Test24 FileUtil.chmod()."""
    mock_walk = mocker.patch('os.walk', return_value=[("/tmp", ["dir"], ["file"]), ])
    mock_fuchmod = mocker.patch.object(FileUtil, '_chmod', return_value=None)
    futil.safe_prefixes = ["/tmp"]
    resout = futil.chmod(0o600, 0o700, 0o755, False)
    assert resout
    mock_fuchmod.assert_called()
    mock_walk.assert_not_called()


def test25_chmod(futil, mocker):
    """Test25 FileUtil.chmod()."""
    mock_fuchmod = mocker.patch.object(FileUtil, '_chmod', side_effect=OSError('fail'))
    resout = futil.chmod()
    assert not resout


def test26_rchmod(futil, mocker):
    """Test26 FileUtil.rchmod()."""
    mock_fuchmod = mocker.patch.object(FileUtil, 'chmod', return_value=True)
    futil.rchmod()
    mock_fuchmod.assert_called()


def test_27__removedir(futil, mocker):
    """Test27 FileUtil._removedir()."""
    mock_walk = mocker.patch('os.walk', return_value=[("/tmp", ["dir"], ["file"]), ])
    mock_islink = mocker.patch('os.path.islink', side_effect=[False, True, True, True])
    mock_chmod = mocker.patch('os.chmod', side_effect=[None, None, None, None])
    mock_unlink = mocker.patch('os.unlink', side_effect=[None, None, None, None])
    mock_rmdir = mocker.patch('os.rmdir', side_effect=[None, None, None, None])
    resout = futil._removedir()
    assert resout
    mock_walk.assert_called()
    mock_islink.assert_called()
    mock_chmod.assert_called()
    mock_rmdir.assert_called()


def test_28__removedir(futil, mocker):
    """Test28 FileUtil._removedir()."""
    mock_walk = mocker.patch('os.walk', side_effect=OSError('fail'))
    resout = futil._removedir()
    assert not resout


# @patch('udocker.utils.fileutil.os.rmdir')
# @patch('udocker.utils.fileutil.os.unlink')
# @patch('udocker.utils.fileutil.os.chmod')
# @patch('udocker.utils.fileutil.os.walk')
# @patch('udocker.utils.fileutil.os.path.islink')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_16__removedir(self, mock_regpre, mock_base, mock_absp, mock_islink, mock_walk,
#                         mock_chmod, mock_unlink, mock_rmdir):
#     """Test16 FileUtil._removedir()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
#     mock_islink.side_effect = [False, True, True, True]
#     mock_chmod.side_effect = [None, None, None, None]
#     mock_unlink.side_effect = [None, None, None, None]
#     mock_rmdir.side_effect = [None, None, None, None]
#     # remove directory under /tmp OK
#     futil = FileUtil("/tmp/directory")
#     status = futil._removedir()
#     self.assertTrue(mock_walk.called)
#     self.assertTrue(mock_islink.call_count, 2)
#     self.assertTrue(mock_chmod.call_count, 3)
#     self.assertTrue(status)

#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_walk.return_value = list()
#     mock_chmod.side_effect = OSError("fail")
#     futil = FileUtil("/directory")
#     status = futil._removedir()
#     self.assertFalse(status)

# @patch.object(FileUtil, '_removedir')
# @patch('udocker.utils.fileutil.HostInfo')
# @patch('udocker.utils.fileutil.os.path.realpath')
# @patch('udocker.utils.fileutil.os.path.lexists')
# @patch('udocker.utils.fileutil.os.remove')
# @patch('udocker.utils.fileutil.os.path.islink')
# @patch('udocker.utils.fileutil.os.path.isfile')
# @patch('udocker.utils.fileutil.os.path.isdir')
# @patch.object(FileUtil, 'uid')
# @patch.object(FileUtil, '_is_safe_prefix')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_17_remove(self, mock_regpre, mock_base, mock_absp, mock_safe, mock_uid, mock_isdir,
#                     mock_isfile, mock_islink, mock_remove, mock_exists, mock_realpath,
#                     mock_hinfo, mock_furmdir):
#     """Test17 FileUtil.remove()."""

#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/filename4.txt'

#     mock_exists.return_value = True
#     futil = FileUtil("filename4.txt")
#     status = futil.remove()
#     self.assertFalse(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.return_value.uid = 1001
#     mock_uid.return_value = 1000
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove()
#     self.assertFalse(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.uid = 1001
#     mock_uid.return_value = 1001
#     mock_safe.return_value = False
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove(False)
#     self.assertFalse(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.uid = 1001
#     mock_uid.return_value = 1001
#     mock_safe.return_value = True
#     mock_isfile.return_value = True
#     mock_remove.return_value = None
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove(True)
#     self.assertTrue(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.uid = 1001
#     mock_uid.return_value = 1001
#     mock_safe.return_value = True
#     mock_isfile.return_value = True
#     mock_remove.side_effect = OSError("fail")
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove(True)
#     self.assertFalse(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.uid = 1001
#     mock_uid.return_value = 1001
#     mock_safe.return_value = True
#     mock_isfile.return_value = False
#     mock_islink.return_value = False
#     mock_isdir.return_value = True
#     mock_remove.return_value = None
#     mock_furmdir.return_value = True
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove(True, True)
#     self.assertTrue(status)

#     mock_base.return_value = 'filename4.txt'
#     mock_absp.return_value = '/tmp/somedir/filename4.txt'
#     mock_exists.return_value = True
#     mock_hinfo.uid = 1001
#     mock_uid.return_value = 1001
#     mock_safe.return_value = True
#     mock_isfile.return_value = False
#     mock_islink.return_value = False
#     mock_isdir.return_value = True
#     mock_remove.return_value = None
#     mock_furmdir.return_value = False
#     futil = FileUtil("/tmp/somedir/filename4.txt")
#     status = futil.remove(True, True)
#     self.assertFalse(status)

# @patch('udocker.utils.fileutil.Uprocess.call')
# @patch('udocker.utils.fileutil.os.path.isfile')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_18_verify_tar(self, mock_regpre, mock_base, mock_absp, mock_isfile, mock_call):
#     """Test18 FileUtil.verify_tar()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_isfile.return_value = False
#     mock_call.return_value = 0
#     status = FileUtil("tarball.tar").verify_tar()
#     self.assertFalse(status)

#     mock_isfile.return_value = True
#     mock_call.return_value = 0
#     status = FileUtil("tarball.tar").verify_tar()
#     self.assertTrue(status)

#     mock_isfile.return_value = True
#     mock_call.return_value = 1
#     status = FileUtil("tarball.tar").verify_tar()
#     self.assertFalse(status)

# @patch('udocker.utils.fileutil.Uprocess.call')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_19_tar(self, mock_regpre, mock_base, mock_absp, mock_call):
#     """Test19 FileUtil.tar()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_call.return_value = 1
#     status = FileUtil("tarball.tar").tar("tarball.tar")
#     self.assertFalse(status)

#     mock_call.return_value = 0
#     status = FileUtil("tarball.tar").tar("tarball.tar")
#     self.assertTrue(status)

# @patch('udocker.utils.fileutil.Uprocess.pipe')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_20_copydir(self, mock_regpre, mock_base, mock_absp, mock_call):
#     """Test20 FileUtil.copydir()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_call.return_value = 1
#     status = FileUtil("filename.txt").copydir("/dir1")
#     self.assertEqual(status, 1)

#     mock_call.return_value = 0
#     status = FileUtil("filename.txt").copydir("/dir1")
#     self.assertEqual(status, 0)

# @patch.object(FileUtil, 'remove')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_21_cleanup(self, mock_regpre, mock_base, mock_absp, mock_remove):
#     """Test21 FileUtil.cleanup()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     Config().conf['tmpdir'] = "/tmp"
#     FileUtil.tmptrash = {'file1.txt': None, 'file2.txt': None}
#     FileUtil("").cleanup()
#     self.assertEqual(mock_remove.call_count, 2)

# @patch('udocker.utils.fileutil.os.path.isdir')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_22_isdir(self, mock_regpre, mock_base, mock_absp, mock_isdir):
#     """Test22 FileUtil.isdir()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_isdir.return_value = True
#     status = FileUtil("filename.txt").isdir()
#     self.assertTrue(status)

#     mock_isdir.return_value = False
#     status = FileUtil("filename.txt").isdir()
#     self.assertFalse(status)

# @patch('udocker.utils.fileutil.os.stat')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_23_size(self, mock_regpre, mock_base, mock_absp, mock_stat):
#     """Test23 FileUtil.size()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_stat.return_value.st_size = 4321
#     size = FileUtil("somefile").size()
#     self.assertEqual(size, 4321)

#     mock_stat.side_effect = OSError("fail")
#     size = FileUtil("somefile").size()
#     self.assertEqual(size, -1)

# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_24_getdata(self, mock_regpre, mock_base, mock_absp):
#     """Test24 FileUtil.getdata()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     with patch(BUILTINS + '.open', mock_open(read_data='qwerty')):
#         data = FileUtil("somefile").getdata()
#         self.assertEqual(data, 'qwerty')

#     # mock_open.side_effect = OSError("fail")
#     # status = FileUtil("somefile").getdata()
#     # self.assertEqual(status, b'')

# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_25_get1stline(self, mock_regpre, mock_base, mock_absp):
#     """Test25 FileUtil.get1stline()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     with patch(BUILTINS + '.open', mock_open(read_data='qwerty')):
#         data = FileUtil("somefile").get1stline()
#         self.assertEqual(data, 'qwerty')

#     # mock_open.side_effect = OSError("fail")
#     # status = FileUtil("somefile").get1stline()
#     # self.assertEqual(status, b'')

# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_26_putdata(self, mock_regpre, mock_base, mock_absp):
#     """Test26 FileUtil.putdata()"""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     with patch(BUILTINS + '.open', mock_open()):
#         data = FileUtil("somefile").putdata("qwerty")
#         self.assertEqual(data, 'qwerty')

#     mock_open.side_effect = OSError("fail")
#     status = FileUtil("somefile").putdata("qwerty")
#     self.assertEqual(status, "")

# @patch('udocker.utils.fileutil.os.path.split')
# @patch('udocker.utils.fileutil.os.path.exists')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_27_getvalid_path(self, mock_regpre, mock_base, mock_absp, mock_exists, mock_split):
#     """Test27 FileUtil.getvalid_path()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "somefile"
#     mock_exists.return_value = True
#     futil = FileUtil("somefile")
#     status = futil.getvalid_path()
#     self.assertEqual(status, "somefile")

#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "somefile"
#     mock_exists.side_effect = [False, True]
#     mock_split.return_value = ("somefile", "/dir")
#     futil = FileUtil("somefile")
#     status = futil.getvalid_path()
#     self.assertEqual(status, "somefile")

# @patch('udocker.utils.fileutil.os.path.islink')
# @patch('udocker.utils.fileutil.os.path.normpath')
# @patch('udocker.utils.fileutil.os.path.realpath')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_28__cont2host(self, mock_regpre, mock_base, mock_absp, mock_rpath, mock_normp,
#                         mock_islink):
#     """Test28 FileUtil._cont2host()."""
#     hpath = ""
#     croot = "/ROOT"
#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "/home/somefile"
#     futil = FileUtil("somefile")
#     status = futil._cont2host(hpath, croot)
#     self.assertEqual(status, "")

#     hpath = "/usr/bin"
#     croot = "/ROOT/usr/bin"
#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "/home/somefile"
#     mock_rpath.return_value = "/ROOT/usr/bin"
#     mock_normp.return_value = "/ROOT/usr/bin"
#     mock_islink.return_value = False
#     futil = FileUtil("somefile")
#     status = futil._cont2host(hpath, croot)
#     self.assertEqual(status, "/ROOT/usr/bin")

#     hpath = "/usr/bin"
#     croot = "/ROOT/usr/bin"
#     vol = ["/home/user:/ROOT/home/user"]
#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "/home/somefile"
#     mock_rpath.return_value = "/ROOT/usr/bin"
#     mock_normp.return_value = "/ROOT/usr/bin"
#     mock_islink.return_value = False
#     futil = FileUtil("somefile")
#     status = futil._cont2host(hpath, croot, vol)
#     self.assertEqual(status, "/ROOT/usr/bin")

# @patch.object(FileUtil, '_cont2host')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_29_cont2host(self, mock_regpre, mock_base, mock_absp, mock_c2h):
#     """Test29 FileUtil.cont2host()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = "somefile"
#     mock_absp.return_value = "somefile"
#     mock_c2h.return_value = "/ROOT/dir"
#     futil = FileUtil("somefile")
#     status = futil.cont2host("/ROOT/dir")
#     self.assertEqual(status, "/ROOT/dir")
#     self.assertTrue(mock_c2h.called)

# @patch('udocker.utils.fileutil.os.access')
# @patch('udocker.utils.fileutil.os.path.isfile')
# @patch.object(FileUtil, '_cont2host')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_30__find_exec(self, mock_regpre, mock_base, mock_absp,
#                         mock_c2h, mock_isfile, mock_access):
#     """Test30 FileUtil._find_exec()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     futil = FileUtil("somefile")
#     status = futil._find_exec("")
#     self.assertEqual(status, "")

#     mock_isfile.return_value = True
#     mock_access.return_value = True
#     futil = FileUtil("/bin/ls")
#     status = futil._find_exec("/bin")
#     self.assertEqual(status, "/bin/ls")

#     mock_isfile.return_value = True
#     mock_access.return_value = True
#     mock_c2h.return_value = "/ROOT/bin/ls"
#     futil = FileUtil("/bin/ls")
#     status = futil._find_exec("/bin", "", "", ".", False)
#     self.assertEqual(status, "/bin/ls")

# @patch.object(FileUtil, '_find_exec')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_31_find_exec(self, mock_regpre, mock_base, mock_absp, mock_findexe):
#     """Test31 FileUtil.find_exec()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'ls'
#     mock_absp.return_value = '/bin/ls'
#     mock_findexe.return_value = '/bin/ls'
#     futil = FileUtil("/bin/ls")
#     status = futil.find_exec("/bin", "", "", ".", False)
#     self.assertEqual(status, "/bin/ls")

# @patch('udocker.utils.fileutil.os.rename')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_32_rename(self, mock_regpre, mock_base, mock_absp, mock_rename):
#     """Test32 FileUtil.rename()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'ls'
#     mock_absp.return_value = '/bin/ls'
#     mock_rename.return_value = None
#     futil = FileUtil("/bin/ls")
#     status = futil.rename("somefile")
#     self.assertTrue(status)

#     mock_regpre.return_value = None
#     mock_base.return_value = 'ls'
#     mock_absp.return_value = '/bin/ls'
#     mock_rename.side_effect = OSError("fail")
#     futil = FileUtil("/bin/ls")
#     status = futil.rename("somefile")
#     self.assertFalse(status)

# # def test_33__stream2file(self):
# #     """Test33 FileUtil._stream2file()."""

# # def test_34__file2stream(self):
# #     """Test34 FileUtil._file2stream()."""

# # def test_35__file2file(self):
# #     """Test35 FileUtil._file2file()."""

# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_36_copyto(self, mock_regpre, mock_base, mock_absp):
#     """Test36 FileUtil.copyto()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     with patch(BUILTINS + '.open', mock_open()):
#         status = FileUtil("source").copyto("dest")
#         self.assertTrue(status)

#         status = FileUtil("source").copyto("dest", "w")
#         self.assertTrue(status)

#         status = FileUtil("source").copyto("dest", "a")
#         self.assertTrue(status)

# @patch('udocker.utils.fileutil.os.path.exists')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_37_find_file_in_dir(self, mock_regpre, mock_base, mock_absp, mock_exists):
#     """Test37 FileUtil.find_file_in_dir()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/dir'
#     file_list = []
#     status = FileUtil("/dir").find_file_in_dir(file_list)
#     self.assertEqual(status, "")

#     file_list = ["F1", "F2"]
#     mock_exists.side_effect = [False, False]
#     status = FileUtil("/dir").find_file_in_dir(file_list)
#     self.assertEqual(status, "")

#     file_list = ["F1", "F2"]
#     mock_exists.side_effect = [False, True]
#     status = FileUtil("/dir").find_file_in_dir(file_list)
#     self.assertEqual(status, "/dir/F2")

# @patch('udocker.utils.fileutil.stat')
# @patch('udocker.utils.fileutil.os.stat')
# @patch('udocker.utils.fileutil.os.symlink')
# @patch('udocker.utils.fileutil.os.remove')
# @patch('udocker.utils.fileutil.os.chmod')
# @patch('udocker.utils.fileutil.os.access')
# @patch('udocker.utils.fileutil.os.path.realpath')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_38__link_change_apply(self, mock_regpre, mock_base, mock_absp, mock_realpath,
#                                 mock_access, mock_chmod, mock_remove, mock_symlink,
#                                 mock_osstat, mock_stat):
#     """Test38 FileUtil._link_change_apply()."""
#     mock_regpre.return_value = None
#     mock_chmod.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_realpath.return_value = "/HOST/DIR"
#     mock_access.return_value = True
#     futil = FileUtil("/con")
#     futil._link_change_apply("/con/lnk_new", "/con/lnk", False)
#     self.assertTrue(mock_remove.called)
#     self.assertTrue(mock_symlink.called)

#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_realpath.return_value = "/HOST/DIR"
#     mock_access.return_value = False
#     mock_chmod.side_effect = [None, None]
#     mock_remove.return_value = None
#     mock_symlink.return_value = None
#     mock_osstat.return_value.st_mode = None
#     mock_stat.return_value = None
#     mock_realpath.return_value = "/HOST/DIR"
#     futil = FileUtil("/con")
#     futil._link_change_apply("/con/lnk_new", "/con/lnk", True)
#     self.assertTrue(mock_chmod.call_count, 2)
#     self.assertTrue(mock_remove.called)
#     self.assertTrue(mock_symlink.called)

# @patch('udocker.utils.fileutil.os.readlink')
# @patch.object(FileUtil, '_link_change_apply', return_value=None)
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_39__link_set(self, mock_regpre, mock_base, mock_absp, mock_lnchange, mock_readlink):
#     """Test39 FileUtil._link_set()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_readlink.return_value = "X"
#     futil = FileUtil("/con")
#     status = futil._link_set("/con/lnk", "", "/con", False)
#     self.assertFalse(status)

#     mock_readlink.return_value = "/con"
#     futil = FileUtil("/con")
#     status = futil._link_set("/con/lnk", "", "/con", False)
#     self.assertFalse(status)

#     mock_readlink.return_value = "/HOST/DIR"
#     futil = FileUtil("/con")
#     status = futil._link_set("/con/lnk", "", "/con", False)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

#     mock_readlink.return_value = "/HOST/DIR"
#     futil = FileUtil("/con")
#     status = futil._link_set("/con/lnk", "", "/con", True)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

#     mock_readlink.return_value = "/HOST/DIR"
#     futil = FileUtil("/con")
#     status = futil._link_set("/con/lnk", "", "/con", True)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

# @patch('udocker.utils.fileutil.os.readlink')
# @patch.object(FileUtil, '_link_change_apply', return_value=None)
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_40__link_restore(self, mock_regpre, mock_base, mock_absp, mock_lnchange, mock_rlink):
#     """Test40 FileUtil._link_restore()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_rlink.return_value = "/con/AAA"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "/con", "/root", False)
#     self.assertTrue(status)

#     mock_rlink.return_value = "/con/AAA"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "/con", "/root", False)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

#     mock_rlink.return_value = "/root/BBB"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "/con", "/root", False)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

#     mock_rlink.return_value = "/XXX"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "/con", "/root", False)
#     self.assertTrue(mock_lnchange.called)
#     self.assertFalse(status)

#     mock_rlink.return_value = "/root/BBB"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "/con", "/root", True)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

#     mock_rlink.return_value = "/root/BBB"
#     futil = FileUtil("/con")
#     status = futil._link_restore("/con/lnk", "", "/root", True)
#     self.assertTrue(mock_lnchange.called)
#     self.assertTrue(status)

# @patch.object(FileUtil, '_link_restore')
# @patch.object(FileUtil, '_link_set')
# @patch.object(FileUtil, '_is_safe_prefix')
# @patch('udocker.utils.fileutil.os.lstat')
# @patch('udocker.utils.fileutil.os.path.islink')
# @patch('udocker.utils.fileutil.os.walk')
# @patch('udocker.utils.fileutil.os.path.realpath')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_41_links_conv(self, mock_regpre, mock_base, mock_absp, mock_realpath, mock_walk,
#                         mock_islink, mock_lstat, mock_is_safe_prefix, mock_link_set,
#                         mock_link_restore):
#     """Test41 FileUtil.links_conv()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = 'filename.txt'
#     mock_absp.return_value = '/tmp/filename.txt'
#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = False
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertEqual(status, None)

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_walk.return_value = []
#     mock_islink.return_value = True
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertEqual(status, [])

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_walk.return_value = [("/", [], []), ]
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertEqual(status, [])

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_islink = False
#     mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertEqual(status, [])

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_islink = True
#     mock_lstat.return_value.st_uid = 1
#     Config().conf['uid'] = 0
#     mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertEqual(status, [])

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_islink = True
#     mock_lstat.return_value.st_uid = 1
#     mock_link_set.reset_mock()
#     mock_link_restore.reset_mock()
#     Config().conf['uid'] = 1
#     mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, True, "")
#     self.assertFalse(mock_link_restore.called)

#     mock_realpath.return_value = "/ROOT"
#     mock_is_safe_prefix.return_value = True
#     mock_islink = True
#     mock_lstat.return_value.st_uid = 1
#     mock_link_set.reset_mock()
#     mock_link_restore.reset_mock()
#     Config().conf['uid'] = 1
#     mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
#     futil = FileUtil("/ROOT")
#     status = futil.links_conv(False, False, "")
#     self.assertFalse(mock_link_set.called)

# @patch('udocker.utils.fileutil.os.path.isdir')
# @patch('udocker.utils.fileutil.os.listdir')
# @patch('udocker.utils.fileutil.os.path.dirname')
# @patch('udocker.utils.fileutil.os.path.abspath')
# @patch('udocker.utils.fileutil.os.path.basename')
# @patch.object(FileUtil, '_register_prefix')
# def test_42_match(self, mock_regpre, mock_base, mock_absp, mock_dname, mock_lsdir, mock_isdir):
#     """Test42 FileUtil.match()."""
#     mock_regpre.return_value = None
#     mock_base.return_value = "/con/filename.txt"
#     mock_absp.return_value = "/con/filename.txt"
#     mock_dname.return_value = "/con/fil*"
#     mock_isdir.return_value = False
#     mock_lsdir.return_value = list()
#     futil = FileUtil("/con/filename.txt")
#     status = futil.match()
#     self.assertEqual(status, [])

#     mock_regpre.return_value = None
#     mock_base.return_value = "fil*"
#     mock_absp.return_value = "/con/filename*"
#     mock_dname.return_value = "/con"
#     mock_isdir.return_value = True
#     mock_lsdir.return_value = ["filename1", "filename2"]
#     futil = FileUtil("/con/filename*")
#     status = futil.match()
#     self.assertEqual(status, ["/con/filename1", "/con/filename2"])
