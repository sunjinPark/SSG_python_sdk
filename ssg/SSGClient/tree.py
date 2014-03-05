#!/usr/bin/python
# -*- coding: utf-8 -*-

from boto.s3.bucket import Bucket
from ssg.SSGInterface.bucket import SSGBucket
from ssg.SSGClient.fruit import Fruit


class Tree(object):

    def __init__(self, connection=None, name=None, real_bucket_name=None, fruit_class=Fruit):
        self.ssg_bucket = SSGBucket(connection.ssg_conn, name, real_name=real_bucket_name)
        self.s3_bucket = Bucket(connection.s3_conn, real_bucket_name)
        self.name = name
        self.connection = connection
        self.fruit_class = fruit_class

    def copy_fruit(self, new_fruit_name, src_tree_name, src_fruit_name):
        """
        Create a new key in the tree by copying another existing key.

        :type new_fruit_name: string
        :param new_fruit_name: The name of the new key

        :type src_tree_name: string
        :param src_tree_name: The name of the source bucket

        :type src_fruit_name: string
        :param src_fruit_name: The name of the source key

        :rtype: :class:ssg.SSGClient.fruit.Fruit or subclass
        :returns: An instance of the newly created fruit object
        """
        pass

    def delete_cors(self, headers=None):
        """
        Removes all CORS configuration from the S3 bucket.
        """
        return self.s3_bucket.delete_cors(headers=headers)

    def delete_fruit(self, fruit_name):
        """
        Deletes a fruit from the tree.
        If a version_id is provided, only that version of the fruit will be deleted.

        :type fruit_name: string
        :param fruit_name: The fruit name to delete
        """
        self.fruit_class = self.get_fruit(fruit_name, validate=False)
        self.fruit_class.delete()
        return self.fruit_class

    def get_all_fruits(self):
        """
        A lower-level method for getting all fruits in this tree.
        """
        fruit_object_list = list()
        fruit_list = self.list()

        for f in fruit_list:
            fruit = self.get_fruit(f)
            fruit_object_list.append(fruit)
        return fruit_object_list

    def get_cors(self, headers=None):
        """
        Returns the current CORS configuration on the bucket.
        """
        return self.s3_bucket.get_cors(headers)

    def get_cors_xml(self, headers=None):
        """
        Returns the current CORS configuration on the bucket as an XML document.

        :rtype: boto.s3.cors.CORSConfiguration
        :return: A CORSConfiguration object
                that describes all current CORS rules in effect for the bucket.
        """
        return self.s3_bucket.get_cors_xml(headers)

    def get_fruit(self, fruit_name, validate=True):
        """
        Check to see if a particular key exists within the bucket.
        This method uses a HEAD request to check for the existance of the key.
        Returns: An instance of a Fruit object or None

        :type fruit_name:
        :param fruit_name:

        :type validate: boolean
        :param validate: If True, it doesn't raise request_error if there is no fruit. (Default: True)

        :rtype: :class:`ssg.SSGClient.fruit.Fruit`
        :returns: A Fruit object from this tree.
        """
        ssg_key = self.ssg_bucket.get_key(fruit_name, validate)
        fruit = self.fruit_class(self, name=fruit_name, ssg_key=ssg_key)
        return fruit

    def get_location(self):
        """
        Returns the LocationConstraint for the bucket.

        :rtype: string
        :returns: The LocationConstraint for th tree.
        """
        return self.ssg_bucket.get_location()

    def list(self):
        """
        List fruits' name in this tree.

        :rtype: list
        :return: fruits' name list
        """
        return self.ssg_bucket.list()

    def lookup(self, fruit_name):
        """
        Deprecated: Please user get_key method.

        :type fruit_name: string
        :param fruit_name: The name of the key to retrieve

        :rtype: :class:`ssg.SSGClient.fruit.Fruit`
        :returns: A Fruit object from this tree.
        """
        return self.get_fruit(fruit_name)

    def new_fruit(self, fruit_name=None):
        """
        Creates a new key

        :type fruit_name: string
        :param fruit_name: The name of the fruit to retrieve

        :rtype: ssg.SSGClient.fruit.Fruit
        :returns: An instance of the newly created Fruit object
        """
        if not fruit_name:
            raise ValueError('Empty fruit names are not allowed')
        return self.fruit_class(self, fruit_name)

    def set_cors(self, cors_config, headers=None):
        """
        Set the CORS for this bucket given a boto CORSConfiguration object

        :type cors_config: boto.s3.cors.CORSConfiguration
        :param cors_config: The CORS configuration you want to configure for this bucket
        """
        return self.s3_bucket.set_cors(cors_config, headers)

    def set_cors_xml(self, cors_xml, headers=None):
        """
        Set the CORS(Cross-Origin Resource Sharing) for a bucket.

        :type cors_xml: string
        :param cors_xml: The XML document describing your desired CORS configuration.
        """
        return self.s3_bucket.set_cors_xml(cors_xml, headers)

    def set_fruit_class(self, fruit_class):
        """
        Set the fruit class associated with this tree.
        By default, this would be the ssg.SSGClient.fruit.Fruit.
        """
        self.fruit_class = fruit_class
