from connection import SSGConnection


if __name__ == "__main__":
    group_key = "f6b18dce67385558b08f9315a9c0560eb580730148efa499994ab590"
    bucket_name = 'test_tree'
    key_name = 'testfold/test1'
    filename = 'home/sungjin/python_essential.pdf'
    # conn = SSGConnection(group_key)
    conn = SSGConnection()
    # test_bucket = conn.create_bucket(bucket_name)
    conn.make_request('DELETE', 'buckets', bucket='bucket_name', key='key_name')

    # key_list = test_bucket.get_key_list()
    # test_key = test_bucket.new_key(key_name)
    # test_key.set_contents_from_filename(filename, 0)
    # test_key.send_file()
    # test_key.finish_response()


    # print test_key.name
    # print test_key.filename
    # print test_key.real_name


    #test_bucket = conn.create_bucket(bucket_name=bucket_name)
    #print test_bucket.generate_url()
    #print type(test_bucket)
    # print conn.header['Authorization']
    #
    # #print test_bucket.name
    # #print test_bucket.real_name

    # bucket_list = conn.get_all_buckets()
    #
    # for b in bucket_list:
    #     print b.name
    #     print b.real_name
    #     print '\n'