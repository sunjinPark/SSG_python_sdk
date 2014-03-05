#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import path

from ssg.SSGClient.connection import Connection


if __name__ == "__main__":
    current_dir = path.dirname(path.abspath(__file__))
    conn = Connection(current_dir + '/../../SSGarden.key')
    print conn.ssg_conn.header
    tree_name = 'delete_test'
    #tree_name = 'test_tree'
    fruit_name = 'logo'
    target_file = current_dir + '/됐니.png'
    des_file = current_dir + '/되어랏.png'

    test_tree = conn.get_tree(tree_name, False)
    # print "fruits : " + str(test_tree.list())
    # test_tree.delete_fruit(fruit_name)
    # print test_tree.list()
    fruit = test_tree.new_fruit(fruit_name)#, False)

    #fruit.delete()
    # fruit = test_tree.get_fruit(fruit_name, False)
    # print fruit.exists()
    fruit.set_contents_from_filename(target_file)
    # fruit.get_contents_to_filename(target_file)
    # print fruit.s3_key.name
    #print test_tree.list()


    # fruit.set_contents_from_filename(target_file)
    # print test_tree.get_location()
    # for f in fruit_list:
    #     print f.__dict__
    # conn.create_basket('7')
    # #conn = Connection('/home/sungjin/SSGarden.key')
    #
    # tree = conn.get_tree(tree_name)
    # print 'tree : ' + tree.name
    # fruit = tree.get_fruit(fruit_name)
    #
    # print 'fruit : ' + fruit.name

    # test_tree = conn.create_Tree(tree_name)

    # fruit.get_contents_to_filename(des_file)
    # fruit.set_contents_from_filename('dd')
    # error print tree.get_location()

    #
    # fruit = basket.get_fruit("test2")
    #
    # #fruit.set_contents_from_filename(current_dir + '/testpic.png')
    # #fruit.set_contents_from_filename(current_dir + '/testfile.txt')
    # #fruit.set_contents_from_filename(current_dir + '/testfile.txt')
    # #fruit.set_contents_from_filename(current_dir + '/testdoc.doc')
    #
    # fruit.get_contents_to_filename('test')
