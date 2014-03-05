from ssg.SSGClient.connection import Connection
from boto.s3.cors import CORSConfiguration


"""
Connect to SSG.

The first step in accessing S3 is to create a connection to the service.
There are two ways to do this in this SDK.
"""
key_file = "./SSGarden.key"

#first way
conn1 = Connection(key_file)

#second way
conn2 = Connection()
conn2.connection(key_file)


"""
Plant your own tree.

The second step is that planting tree to store your data.
Tree name is globally unique, same as AWS S3 Bucket.

There are many locations and you can plant tree that we supply.
If you want more information, you can see 'ssg.SSGInterface.connection.Location'
"""
#Planting tree
tree = conn1.create_tree(tree_name='my_tree17', location='')
print "you planted your tree that name of %s" % tree.name


"""
Accessing A Tree

Once a Tree exists, you can access it by getting the Tree.
It also have two ways to get tree.
lookup() method occurs error message when tree doesn't exist.
"""
#first
mytree1 = conn1.get_tree('my_tree')
print "you got a tree that name of %s using get_tree method" % mytree1.name

#if you want to generate error message when tree doesn't exist, you just add validate=False.
#mytree = conn1.get_tree('unknow_tree', validate=False)
#now you can see error message.

#second
mytree2 = conn1.lookup('my_tree')
print "you got a tree that name of %s using lookup method" % mytree1.name


"""
Listing All Available Buckets

In addition to accessing specific Tree via the create_tree method you can also get a list of
all available trees' name that you have created.
"""
rs = conn1.list()
print "you have %s trees in your garden" % str(len(rs))
print "Tree names list : " + str(rs)


"""
Setting/Getting/Deleting CORS Configuration on a Bucket

Cross-origin resource sharing (CORS) defines a way for client web applications
 that are loaded in one domain to interact with resources in a different domain.
With CORS support in Amazon S3, you can build rich client-side web applications
with Amazon S3 and selectively allow cross-origin access to your Amazon S3 resources.
"""
cors_cfg = CORSConfiguration()
cors_cfg.add_rule(['PUT', 'POST', 'DELETE'], 'https://www.example.com', allowed_header='*', max_age_seconds=3000, expose_header='x-amz-server-side-encryption')
cors_cfg.add_rule('GET', '*')


"""
The above code creates a CORS configuration object with two rules.

The first rule allows cross-origin PUT, POST, and DELETE requests from the https://www.example.com/ origin. The rule also allows all headers in preflight OPTIONS request through the Access-Control-Request-Headers header. In response to any preflight OPTIONS request, Amazon S3 will return any requested headers.
The second rule allows cross-origin GET requests from all origins.
To associate this configuration with a bucket:
"""
mytree1 = conn1.lookup('my_tree1')
mytree1.set_cors(cors_cfg)

"""
To retrieve the CORS configuration associated with a bucket:
"""
cors_cfg = mytree1.get_cors()
print "cors_cfg : " + str(cors_cfg)

"""
And, finally, to delete all CORS configurations from a bucket:
"""
mytree1.delete_cors()


"""
Accessing a Fruit

Accessing and upload file
"""
file_path = "./test_file.txt"
myfruit = mytree1.new_fruit("my_fruit")
myfruit.set_contents_from_filename(file_path)

"""
Accessing and download file
"""
file_path = "./download_file.txt"
myfruit2 = mytree1.get_fruit("my_fruit")
myfruit2.get_contents_to_filename(file_path)