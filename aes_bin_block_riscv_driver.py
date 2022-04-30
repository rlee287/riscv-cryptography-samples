from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

from random import SystemRandom

from base64 import b64encode, b64decode, b16encode

import subprocess
import os.path

import tqdm

secure_rand_inst = SystemRandom()

def test_once() -> bool:
    key_len = secure_rand_inst.choice([128, 192, 256]) // 8
    key = get_random_bytes(key_len)

    msg = get_random_bytes(128//8)
    aes_inst = AES.new(key, AES.MODE_ECB)
    ct_bytes_py = aes_inst.encrypt(msg)

    aes_bin_result = subprocess.run(["../riscv_tools_built/bin/spike",
        "--log=aes_block_test.txt", "--log-commits",
        "../riscv_tools_built/riscv64-linux-gnu/bin/pk", "./aes_bin_block_riscv",
        b64encode(key).decode("ascii"),
        b64encode(msg).decode("ascii")], capture_output=True)

    if aes_bin_result.returncode != 0:
        print("aes_bin failed")
        print(aes_bin_result.stdout.decode("utf8"))
        print(aes_bin_result.stderr.decode("utf8"))
        return False

    tuple_out = tuple(aes_bin_result.stdout.split(b"\n"))
    # Skip over the "bbl loader" printout
    ct_bytes_bin = b64decode(tuple_out[1])

    if ct_bytes_py != ct_bytes_bin:
        print("Result mismatch")
        print("Python: ", b16encode(ct_bytes_py))
        print("Bin:    ", b16encode(ct_bytes_bin))
        return False
    
    return True

def main():
    if not os.path.isfile("./aes_bin_riscv"):
        print("aes_bin binary not found")
        return

    test_runs = 10000
    pb = [0] #tqdm.trange(test_runs)
    for i in pb:
        if not test_once():
            break
    else:
        # No break -> success
        print("Success")

if __name__ == "__main__":
    main()