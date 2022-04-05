#include <iostream>

#include <boost/multiprecision/cpp_int.hpp>
#include "crypto-algorithms/sha256.h"
#include "crypto-algorithms/base64.h"

using boost::multiprecision::number;
using boost::multiprecision::cpp_int_backend;
using boost::multiprecision::signed_magnitude;
using boost::multiprecision::checked;
using boost::multiprecision::powm;

typedef number<cpp_int_backend<2048, 2048, signed_magnitude, checked> > int4096_t;

// See https://www.boost.org/doc/libs/1_78_0/libs/multiprecision/doc/html/index.html

void print_usage() {
    std::cout << "Usage: rsa_expmod_bin n d msg" << std::endl;
}
int main(int argc, char **argv) {
    if (argc != 4) {
        print_usage();
        return 1;
    }
    int4096_t n(argv[1]);
    int4096_t d(argv[2]);

    size_t msg_len = base64_decode((uint8_t*) argv[3], NULL, strlen(argv[3]));
    uint8_t *msg_buf = (uint8_t*) malloc(msg_len * sizeof(uint8_t));
    base64_decode((uint8_t*) argv[3], msg_buf, strlen(argv[3]));

    SHA256_CTX hash_ctx;
    uint8_t hash_val[256/8];
    sha256_init(&hash_ctx);
    sha256_update(&hash_ctx, msg_buf, msg_len);
    sha256_final(&hash_ctx, hash_val);

    free(msg_buf);

    for (int i=0; i<256/8; i++) {
        std::cout << std::setfill('0') << std::setw(2) << std::hex << (int)hash_val[i];
    }
    std::cout << std::endl;

    int4096_t c;
    boost::multiprecision::import_bits(c, &hash_val[0], &hash_val[256/8], 8);
    int4096_t m = powm(c, d, n);

    std::cout << "0x" << std::hex << m << std::endl;

    return 0;
}