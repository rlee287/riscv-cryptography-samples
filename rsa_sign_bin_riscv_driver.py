from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
import hashlib

from random import SystemRandom

from base64 import b64encode, b16decode

import subprocess
import os.path

import tqdm

secure_rand_inst = SystemRandom()

def test_once() -> bool:
    key_len = secure_rand_inst.randint(1024, 1152)
    key = RSA.generate(key_len)

    msg = get_random_bytes(secure_rand_inst.randrange(1, 512))
    computed_msg_hash = hashlib.sha256(msg)

    rsa_bin_result = subprocess.run(["../riscv_tools_built/bin/spike",
        "--log=rsa_test.txt", "--log-commits",
        "../riscv_tools_built/riscv64-linux-gnu/bin/pk", "./rsa_sign_bin_riscv",
        str(key.n),
        str(key.d),
        b64encode(msg).decode("ascii")], capture_output=True)

    if rsa_bin_result.returncode != 0:
        print("rsa_bin failed")
        print(rsa_bin_result.stdout.decode("utf8"))
        print(rsa_bin_result.stderr.decode("utf8"))
        return False

    tuple_out = tuple(rsa_bin_result.stdout.split(b"\n"))
    # Skip over the "bbl loader" printout
    _, hash_bin, sig_bin_str, _ = tuple_out
    if hash_bin.decode("ascii") != computed_msg_hash.hexdigest():
        print("Hash mismatch")
        print("Python: ", repr(computed_msg_hash.hexdigest()))
        print("Bin:    ", repr(hash_bin.decode("ascii")))
        return False

    sig_bin_str = sig_bin_str[2:]
    if len(sig_bin_str) % 2 == 1:
        sig_bin_str = b"0" + sig_bin_str

    hash_bin_val = int.from_bytes(b16decode(hash_bin, casefold=True), 'big')
    sig_bin = int(sig_bin_str, 16)

    computed_sig = pow(hash_bin_val, key.d, key.n)

    if computed_sig != sig_bin:
        print("Result mismatch")
        print("Python: ", hex(computed_sig))
        print("Bin:    ", hex(sig_bin))
        return False
    
    return True

def main():
    if not os.path.isfile("./rsa_sign_bin_native"):
        print("rsa_bin binary not found")
        return

    test_runs = 1000
    #pb = tqdm.trange(test_runs)
    for i in [0]: #pb:
        if not test_once():
            break
    else:
        # No break -> success
        print("Success")

if __name__ == "__main__":
    main()