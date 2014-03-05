#!/usr/bin/python
# -*- coding: utf-8 -*-


class Encryption(object):
    _split_count = None
    _mapping_password = None
    max_len = 15

    def __init__(self, meta_password):
        self.meta_password = meta_password
        self.file_size = None
        self.padding_byte = None

    def encrypt(self, file_buf):
        """
        encrypts file_buf using hash function.
        mapping password is always different and encrypt_buf is always different.

        :rtype: buffer
        :returns: encrypted buf
        """

        renewal_buf, self.file_size = self._padding_data(file_buf)

        chunks = self._split_by_split_count(renewal_buf)

        shuffled_buf = self._shuffle_buf(chunks)
        str_padding_byte = str(self.padding_byte)

        if len(str_padding_byte) == 1:
            str_padding_byte = '0' + str_padding_byte
        encrypt_buf = shuffled_buf + str(str_padding_byte)

        return encrypt_buf

    def decrypt(self, file_buf):
        """
        decrypts file_buf.

        :rtype: buffer
        :returns: decrypted buf
        """
        str_padding_byte = file_buf[-2:]
        self.padding_byte = int(str_padding_byte)
        shuffled_buf = file_buf[0:-2]
        header_byte = 2
        total_header_size = self.split_count * header_byte
        self.file_size = len(shuffled_buf) - total_header_size

        chunks = self._split_by_split_count(shuffled_buf)
        restored_buf = self._restore_buf(chunks)
        decrypt_buf = self._remove_padding(restored_buf)

        return decrypt_buf

    @property
    def split_count(self):
        if self._split_count is None:
            self._split_count = self._count_meta_password()
            if self._split_count > 30:
                raise ValueError("meta_pass word must be shorter than 30")
        return self._split_count

    @property
    def mapping_password(self):
        if self._mapping_password is None:
            self._mapping_password = self._generate_mapping_password()
        return self._mapping_password

    def _shuffle_buf(self, chunks):
        shuffled_buf = ''
        chunk_index = 0
        modified_chunk = list()
        shuffled_chunks = dict()

        for c in chunks:
            header = str(self.mapping_password[chunk_index])
            if len(header) == 1:
                header = '0' + header

            modified_chunk.append(header + c)
            shuffled_chunks[header] = modified_chunk[chunk_index]
            chunk_index += 1

        for seq in range(len(shuffled_chunks)):
            str_seq = str(seq)
            if len(str_seq) == 1:
                str_seq = '0' + str_seq
            shuffled_buf += shuffled_chunks[str_seq]

        return shuffled_buf

    def _count_meta_password(self):
        return len(self.meta_password)

    def _generate_mapping_password(self):
            hash_size = self.split_count
            trial_count = 0
            key_list = list()
            for index in range(hash_size):
                double_probing = 1
                new_value = 1
                value = (self.file_size / ord(self.meta_password[index])) % hash_size

                while key_list.count(value) != 0:
                    value = (value + double_probing) % hash_size
                    double_probing *= 2

                    if double_probing > hash_size:
                        value += 1
                        double_probing = 1

                    trial_count += 1
                    if trial_count > 20:
                        value += new_value
                        new_value *= 3
                        trial_count = 0
                    value %= hash_size

                key_list.append(value)

            return key_list

    def _split_by_split_count(self, file_buf):

        chunk_size = len(file_buf) / self.split_count
        chunk_index = 0

        chunks = list()
        pos = 0

        while chunk_index < self.split_count:
            chunk = ''
            chunk += file_buf[pos:pos+chunk_size]
            pos += chunk_size
            chunks.append(chunk)
            chunk_index += 1

        return chunks

    def _padding_data(self, file_buf):
        file_size = len(file_buf)
        self.padding_byte = self.split_count - (file_size % self.split_count)
        for b in range(self.padding_byte):
            file_buf += '0'
        return file_buf, len(file_buf)

    def _restore_buf(self, chunks):
        chunks_dict = dict()
        restored_buf = ''

        for c in chunks:
            k = c[0:2]
            v = c[2:]
            chunks_dict[k] = v

        for m in self.mapping_password:
            str_m = str(m)
            if len(str_m) == 1:
                str_m = '0' + str_m

            tmp_buf = chunks_dict[str_m]
            restored_buf += tmp_buf

        return restored_buf

    def _remove_padding(self, file_buf):
        size = len(file_buf) - self.padding_byte
        return file_buf[0:size]

    def _combine_buf(self, chunks):
        combine_buf = ''
        for c in chunks:
            combine_buf += c
        return combine_buf