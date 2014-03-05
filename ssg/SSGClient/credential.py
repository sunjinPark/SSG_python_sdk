

class Credential:
    def __init__(self, key_file):
        key_list = self._read_keys_from_file(key_file)
        self.meta_pw = key_list.pop()
        self.group_key = key_list.pop()
        self.secret = key_list.pop()
        self.accessid = key_list.pop()

    def _read_keys_from_file(self, key_file):
        crf = open(key_file, 'r')
        buf = crf.read()
        key_list = buf.split(',')
        crf.close()
        return key_list