#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path, mkdir
from shutil import rmtree
from boto.s3.key import Key
from ssg.SSGClient.encryption import Encryption
from ssg.SSGInterface.key import SSGKey


class Fruit(object):
    _tmp_dir = None

    def __init__(self, tree=None, name=None, ssg_key=None):
        self.tree = tree
        self.name = name

        if not ssg_key is None:
            self.ssg_key = ssg_key
            self.s3_key = Key(self.tree.s3_bucket, ssg_key.real_name)
        else:
            self.ssg_key = SSGKey(self.tree.ssg_bucket, name=name)
            self.s3_key = None

    def __unicode__(self):
        return self._tmp_dir

    def delete(self):
        """
        Delete this fruit from SSG
        """
        self.s3_key.delete()
        self.ssg_key.delete()
        # return a key object with information on what was deleted.
        return self

    def exists(self):
        """
        Returns True if the fruit exists.
        """
        return self.ssg_key.exists()

    def generate_url(self, expires_in):
        """
        Generate a URL to access this fruit.

        :type expires_in: int
        :param expires_in: How long the url is valid for, in seconds

        :rtype: dict
        :return: two urls that can access this fruit.
        """
        #url을 통해 따로 받아 다른 방법으로 encryption이나 decryption을 할 수 있음
        url_dict = dict()
        url_dict['s3_url'] = self.s3_key.generate_url(expires_in)
        url_dict['ssg_url'] = self.ssg_key.generate_url()
        return url_dict

    def get_contents_to_file(self, fp, headers=None, num_cb=10, torrent=False, version_id=None,
                             res_download_handler=None, response_headers=None):
        """
        Retrieve an object from SSG using the name of the Key object as the key in S3.
        Write the contents of the object to the file pointed to by ‘fp’
        """
        #download file by using file pointer
        pass

    def get_contents_to_buf(self, dec_class=None):
        """
        Retrieve an object from S3 using the name of the Key object as the key in S3.
        Write the contents of the object to the file pointed to by ‘buf’
        flow : download each cloud storage -> combine
            -> decryption -> save complete file -> flush tmp dir

        :rtype: buffer
        :return: buffer that receive from s3 and ssg
        """
        combiner = file_mng(self.tmp_dir)
        tmp_dir = combiner.tmp_dir
        #download from s3
        self.s3_key.get_contents_to_filename(tmp_dir+"tmp1")
        self.ssg_key.get_contents_to_filename(tmp_dir+"tmp2")

        #combine files
        enc_buf = combiner.combine_tmp_files()
        #decryption(save complete file)
        if dec_class is None:
            dec = Encryption(self.tree.connection._cre.meta_pw)
        else:
            dec = dec_class

        #decrpytion(filename)
        dec_buf = dec.decrypt(enc_buf)

        #flush tmp dir
        combiner.flush_tmp_dir()

        #error시엔 에러 메시지 출력 후 finally로 무조건 tmp dir 날리기
        return dec_buf

    def get_contents_to_filename(self, filename):
        """
        Retrieve an object from S3 using the name of the Key object as the key in S3.
        Store contents of the object to a file named by ‘filename’.

        :type file_name: string
        :param filename: The filename of where to put the file contents
        """

        dec_buf = self.get_contents_to_buf(dec_class=None)

        with open(filename, 'wb') as f:
            f.write(dec_buf)
        print str(self.name) + "download complete"

    def get_metadata(self):
        return self.ssg_key.get_metadata()

    def set_contents_from_file(self, fp, enc_class=None):
        """
        Store an object in SSG using the name of the fruit object as the fruit in SSG
         and the contents of the file pointed to by ‘fp’ as the contents.
        The data is read from ‘fp’ from its current position until ‘size’ bytes
         have been read or EOF.

        flow : encrypt file -> split file -> upload each cloud -> flush tmp dir
        """
        enc_file_path = self.tmp_dir + 'enc_file'
        #encrypt file
        if enc_class is None:
            enc = Encryption(self.tree.connection._cre.meta_pw)
        else:
            enc = enc_class

        enc_buf = enc.encrypt(fp.read())
        with open(enc_file_path, 'wb') as f:
            f.write(enc_buf)

        #split file
        splitter = file_mng(self.tmp_dir)
        s3_tmp, ssg_tmp = splitter.split(enc_file_path)

        #upload request
        self.ssg_key.set_contents_from_filename(ssg_tmp, path.getsize(s3_tmp))
        real_name = self.ssg_key.real_name
        self.s3_key = Key(self.tree.s3_bucket, real_name)

        if self.s3_key.exists(real_name):
            raise ValueError("Key already exists. Input another Key.")

        #upload to s3
        self.s3_key.set_contents_from_filename(s3_tmp)
        #upload to ssg
        #exception 필요
        self.ssg_key.send_file()
        #flush tmp dir
        splitter.flush_tmp_dir()

        #error시엔 둘다 지우는거로......
        print str(self.name) + "upload success!"

    def set_contents_from_filename(self, filename, enc_class=None):
        """
        Store an object in SSG using the name of the fruit object as the fruit in SSG
         and the contents of the file named by ‘filename’.

        :type filename: string
        :param filename: The name of the file that you want to put onto SSG
        """
        with open(filename, 'rb') as f:
            self.set_contents_from_file(f, enc_class)

    def build_post_form_args(self, size_s3, size_ssg, expires_in=6000):
        """
        This only returns the arguments required for the post form, not the
        actual form.  This does not return the file input field which also
        needs to be added.

        using example : It generates upload url.

        :type size_s3: int
        :param size_s3: The size in bytes, of s3 file size

        :type size_ssg: int
        :param size_ssg: The size in bytes, of ssg file size

        :type expires_in: int
        :param expires_in: Time (in seconds) before this expires, defaults to 6000
        """
        upload_dict = dict()
        upload_dict['ss3'] = self.ssg_key.build_post_form_args(size_s3=size_s3, size_ssg=size_ssg)

        real_name = self.ssg_key.real_name
        self.s3_key = Key(real_name)

        upload_dict['s3'] = self.tree.connection.s3_conn.build_post_form_args(bucket_name=self.tree.s3_bucket.name,
                                                                              key=real_name, expires_in=expires_in)
        return upload_dict

    def close(self):
        #close s3_key
        self.s3_key.close()
        #close ssg_key

    @property
    def tmp_dir(self):
        #make tmp dir location : ./tmp/
        self._tmp_dir = str(path.dirname(path.abspath(__file__)) + '/tmp/')
        if not path.isdir(self._tmp_dir):
            mkdir(self._tmp_dir)
        return self._tmp_dir


class file_mng(object):

    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir

    def split(self, src_path):
        """
        Splits into two parts the source file

        :type src_path: string
        :param src_path: indicates source file path
        """
        print 'start spilt'

        try:
            src_f = open(src_path, 'rb')
            src_size = path.getsize(src_path)

            #calculate each file size
            s3_size = src_size/2
            ssg_size = src_size - s3_size

            s3_buf = src_f.read(s3_size)
            print "s3_buf split complete"
            ssg_buf = src_f.read(ssg_size)
            print "ssg_buf split complete"

            #get tmp files path
            s3_path = self.tmp_dir + "tmp1"
            ssg_path = self.tmp_dir + "tmp2"

            #tmp file open
            tmp_s3 = open(s3_path, "wb")
            tmp_ssg = open(ssg_path, "wb")

            #written file from each buffer
            tmp_s3.write(s3_buf)
            tmp_ssg.write(ssg_buf)

            #close all files
            src_f.close()
            tmp_s3.close()
            tmp_ssg.close()

            print "split complete\n\n"

            return s3_path, ssg_path

        except IOError, e:
            print e
            print 'There is no "%s" file' % src_path
            return -1

    def combine_tmp_files(self):
        """
        Combines two files into one complete file.
        It works only in tmp dir
        """
        print 'start combine'
        try:
            #open tmp files
            tmp_s3 = open(self.tmp_dir + "tmp1", "rb")
            tmp_ssg = open(self.tmp_dir + "tmp2", "rb")
            # complete = open(file_path, 'wb')

            #write to buffer from files
            s3_buf = tmp_s3.read()
            ssg_buf = tmp_ssg.read()
            com_buf = s3_buf + ssg_buf

            # #make complete file to tmp_dir
            # complete.write(com_buf)

            #close all files
            tmp_s3.close()
            tmp_ssg.close()
            # complete.close()

        except IOError, e:
            print e
            print 'There is no "%s" file % tmp_file'
            return False

        print "combining complete"
        return com_buf

    def flush_tmp_dir(self):
        """
        Deletes tmp dir that is performed split and combine
        """
        if not path.isdir(self.tmp_dir):
                pass

        else:
            rmtree(self.tmp_dir)



