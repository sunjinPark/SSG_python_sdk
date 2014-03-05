#!/usr/bin/python
# -*- coding: utf-8 -*-
from boto.s3.connection import S3Connection
from boto.s3.cors import CORSConfiguration
from boto.s3.connection import check_lowercase_bucketname

from ssg.SSGClient.credential import Credential
from ssg.SSGClient.tree import Tree
from ssg.SSGInterface.connection import SSGConnection


class Connection(object):
    user_bucket_name = None

    def __init__(self, key_file=None, tree_class=Tree):
        if not (key_file is None):
            self.connection(key_file)

        else:
            self.s3_conn = None
            self.ssg_conn = None

        self.tree_class = tree_class

    def connection(self, key_file, tree_class=Tree):
        #추후 수정 필요
        self._cre = Credential(key_file)
        self.s3_conn = S3Connection(self._cre.accessid, self._cre.secret)
        self.ssg_conn = SSGConnection(self._cre.group_key)
        self.tree_class = tree_class

    def create_tree(self, tree_name, headers=None, location='', policy=None):
        """
        Creates a new located tree. By default it’s in the Tokyo

        :type tree_name: string
        :param tree_name: The name of the new tree

        :type location: str
        :param location: The location of the new bucket. You can use one of the
                        constants in :class: ssg.SSGInterface.connection.Location


        """
        ssg_bucket = self.ssg_conn.create_bucket(tree_name, location)
        real_bucket_name = ssg_bucket.real_name
        if self.s3_conn.lookup(real_bucket_name) is None:
            self._create_user_s3_bucket_internal(real_bucket_name, location)
        else:
            #바로 이전거 delete 요청...
            print "you have already owned bucket : %s" % self.user_bucket_name
            return None

        tree = self.tree_class(self, tree_name, real_bucket_name)

        return tree

    def get_all_trees(self):
        """
        get all available trees in same garden.

        :rtype tree_list: list
        :return tree_list: available tree list
        """
        tree_list = []
        ssg_bucket_list = self.ssg_conn.get_all_buckets()
        print ssg_bucket_list
        for ssg_bucket in ssg_bucket_list:
            tree_list.append(self.tree_class(self, ssg_bucket.name, ssg_bucket.real_name))
        return tree_list

    def get_tree(self, tree_name, validate=True):
        """
        Retrieves a tree by name.

        If validate=False is passed, no request is made to the service (no charge/communication delay).
        This is only safe to do if you are sure the tree exists.

        If the default validate=True is passed, a request is made to the service to ensure the tree exists.

        :type tree_name: string
        :param tree_name: The name of the new tree

        :type validate: boolean
        :param validate: If True, it will try to verify the bucket exists on the service-side. (Default: True)

        :rtype tree: <Tree> object
        :return tree: if a tree exists, this function returns <Tree> object
        """
        ssg_bucket = self.ssg_conn.get_bucket(tree_name, validate)
        tree = self.tree_class(self, tree_name, ssg_bucket.real_name)
        return tree

    def head_tree(self, tree_name):
        """
        Determines if a tree exists by name.
        If the tree does not exist, an S3ResponseError will be raised.

        :type tree_name: str
        :param tree_name: The name of the tree

        :rtype tree: <Tree> object
        :returns tree: if a tree exists, this function returns <Tree> object
        """
        tree = self.get_tree(tree_name, validate=False)
        return tree

    def lookup(self, tree_name, validate=True):
        """
        Attempts to get a tree from S3.

        Works identically to Connection.get_tree, save for that it will return None
        if the tree does not exist instead of throwing an exception.

        :type tree_name: string
        :param tree_name: The name of th bucket

        :type validate: boolean
        :param validate: If True, it doesn't raise request_error if there is no tree. (Default: True)
        """
        tree = self.get_tree(tree_name, validate=validate)
        return tree

    def set_tree_class(self, tree_class):
        """
        Set the tree class associated with this tree. If you want to subclass that
        for some reason this allows you to associate your new tree class.

        :type tree_class: class
        :param tree_class: A subclass of Tree that can be more specific
        """
        self.tree_class = tree_class

    def list(self):
        """
        Get all trees' name in same garden.
        """
        tree_list = list()
        ssg_bucket_list = self.ssg_conn.get_all_buckets()
        for b in ssg_bucket_list:
            tree_list.append(b.name)
        return tree_list

    def _create_user_s3_bucket_internal(self, real_bucket_name, location=None):
        method_list = ['PUT', 'POST', 'DELETE', 'GET', 'HEAD']
        new_bucket = self.s3_conn.create_bucket(real_bucket_name, location=location)
        cors_cfg = CORSConfiguration()
        cors_cfg.add_rule(method_list, allowed_origin=['*'], allowed_header=['*'])
        new_bucket.set_cors(cors_cfg)
