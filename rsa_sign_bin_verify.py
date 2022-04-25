from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.number import getPrime
import hashlib

from random import SystemRandom

from base64 import b64encode, b16decode

import subprocess
import os.path

import tqdm

secure_rand_inst = SystemRandom()

def test_once() -> bool:
    key_len = 256 #secure_rand_inst.randint(1024, 1152)
    prime_1 = getPrime(key_len//2)
    prime_2 = getPrime(key_len//2)
    n = prime_1*prime_2
    enc = 65537
    dec = pow(enc, -1, (prime_1-1)*(prime_2-1))

    #key = RSA.generate(key_len)

    msg = get_random_bytes(secure_rand_inst.randrange(1, 1024*16))
    computed_msg_hash = hashlib.sha256(msg)

    rsa_bin_result = subprocess.run(["./rsa_sign_bin_native",
        str(n),
        str(dec),
        b64encode(msg).decode("ascii")], capture_output=True)

    if rsa_bin_result.returncode != 0:
        print("rsa_bin failed")
        print(rsa_bin_result.stdout.decode("utf8"))
        print(rsa_bin_result.stderr.decode("utf8"))
        return False

    tuple_out = tuple(rsa_bin_result.stdout.split(b"\n"))
    hash_bin, sig_bin_str, _ = tuple_out
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

    computed_sig = pow(hash_bin_val, dec, n)

    if computed_sig != sig_bin:
        print("Result mismatch")
        print("Python: ", hex(computed_sig))
        print("Bin:    ", hex(sig_bin))
        return False
    
    return True

def main():
    if not os.path.isfile("./rsa_sign_bin_native"):
        print("rsa_sign_bin binary not found")
        return

    test_runs = 1000
    pb = tqdm.trange(test_runs)
    for i in pb:
        if not test_once():
            break
    else:
        # No break -> success
        print("Success")

if __name__ == "__main__":
    main()