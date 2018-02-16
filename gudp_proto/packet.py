from struct import pack,unpack

_u_32_mask = 0xffffffff

class Packet(object):
    
  

    def __init__(self, 
        prot_id = 0, 
        seq     = 0,
        ack     = 0,
        ack_bit = 0,
        data    = "",
        send_to = None):

        self.prot_id = prot_id
        self.seq     = seq
        self.ack     = ack
        self.ack_bit = ack_bit
        self.data    = data

    def pack(self):
        data_len    = len(self.data)
        pack_format = 'IIII' + str(data_len) + 's'
        return pack(pack_format,
            self.prot_id,
            self.seq,
            self.ack,
            self.ack_bit,
            self.data.encode()
        )

    def unpack(self, data):
        header, data = data[:16], data[16:]
        try:
            (self.prot_id,
            self.seq,
            self.ack,
            self.ack_bit) = unpack('IIII', header) 
        except:
            raise
        self.data    = data


def seq_gt(s1, s2):
    return  ( ( s1 > s2 ) and ( (s1 - s2) & _u_32_mask <= 32768 ) ) \
            or ( (s2 > s1) and ( (s2 - s1) & _u_32_mask <= 32768 ) )

def add_to_seq(s, to_add = 1):
    return (s + to_add) & _u_32_mask

def sub_from_seq(s, to_sub = 1):
    return (s - to_sub) & _u_32_mask