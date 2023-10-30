import socket
from file_utils import break_file
import os
import json
import hashlib

'''
Provide addresses in tuple format
Handshaked peers should only be allowed
'''


class Sender:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_addr = socket.gethostbyname(self.hostname)
        self.port = 65432
        self.alt_port = 54321
        self.CHUNK_SIZE = 1024

    def setup_listener(self):
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sckt.bind((self.ip_addr, self.port))
        except OSError:
            sckt.bind((self.ip_addr, self.alt_port))
        else:
            return None
        return sckt

    def send_message(self, sckt, client_addr, content):
        if sckt:
            print(client_addr)
            sckt.connect(client_addr)
            res = sckt.send(content)
            sckt.close()
            print(res)
        else:
            raise RuntimeError("Unable to bind socket")

    def break_file(self, file_path):
        return break_file(file_path, self.CHUNK_SIZE)

    def populate_peers(self, peers, parts):
        ctr = [i for i in range(0, len(parts))]
        if len(peers) == len(parts):
            return zip(ctr, peers, parts)
        elif len(peers) > len(parts):
            return zip(ctr, peers[0:len(parts)], parts)
        else:
            new_peers = peers
            extra_req = len(parts) - len(peers)
            i = 0
            iter = 0
            while i < extra_req:
                if iter >= len(peers):
                    iter = 0
                new_peers.append(peers[iter])
                iter += 1
                i += 1
            return zip(ctr, new_peers, parts)

    def upload_file(self, file_path, peers):
        sckt = self.setup_listener()
        parts = self.break_file(file_path)
        file_info = os.path.splitext(file_path)
        filename = file_info[0]
        if filename.__contains__('/'):
            filename = filename[filename.rindex('/')+1:]
        orig_file = filename
        filename = hashlib.md5(filename.encode('utf-8')).hexdigest()
        print("HASH", filename)
        for ctr, peer, part in self.populate_peers(peers, parts):
            meta = {"part_file_name": f'{ctr}.part',
                    "original_name": orig_file,
                    "uid": filename,
                    "extension": file_info[1], "content": part,
                    "offset": ctr, "length": len(parts),
                    "original_size": len(parts)*self.CHUNK_SIZE}

            json_meta = json.dumps(meta)
            print(json_meta)
            # self.send_message(sckt, peer, json_meta)
        print("Sent")


if __name__ == "__main__":
    sender = Sender()
    peers = ['0.0.0.0:8000']
    sender.upload_file('/home/akshat/clg/se_project/File-Sharing-P2P/p2pbackend/o.jpg', peers)
