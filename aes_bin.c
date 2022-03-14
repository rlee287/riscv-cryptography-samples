#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "crypto-algorithms/aes.h"
#include "crypto-algorithms/base64.h"

// Copied from libsodium
void zero_memory(void * ptr, size_t len) {
    volatile unsigned char *volatile pnt_ =
        (volatile unsigned char *volatile) ptr;
    size_t i = (size_t) 0U;

    while (i < len) {
        pnt_[i++] = 0U;
    }
}

void print_usage() {
    puts("Usage: aes_bin base64_enc_key base64_enc_nonce base64_ptxt_msg");
}
int main(int argc, char **argv) {
    if (argc != 4) {
        print_usage();
        return 1;
    }

    size_t key_len = base64_decode(argv[1], NULL, strlen(argv[1]));
    if (key_len != 128/8 && key_len != 192/8 && key_len != 256/8) {
        puts("Key must be 128, 192, or 256 bits long");
        return 1;
    }
    // Make buffers the max size needed (i.e. for 256-bit keys)
    uint8_t key_buf[256/8];
    uint32_t expanded_key_arr[4*(14+1)];

    base64_decode(argv[1], key_buf, strlen(argv[1]));
    aes_key_setup(key_buf, expanded_key_arr, key_len*8);

    if (base64_decode(argv[2], NULL, strlen(argv[2])) != 64/8) {
        puts("Nonce must be 64 bits (half the block size)");
        return 1;
    }
    // We need the counter to be 0-initialized
    uint8_t nonce_buf[128/8] = {0};
    base64_decode(argv[2], nonce_buf, strlen(argv[2]));

    size_t msg_len = base64_decode(argv[3], NULL, strlen(argv[3]));
    uint8_t * msg_buf = malloc(msg_len * sizeof(uint8_t));
    uint8_t * enc_msg_buf = malloc(msg_len * sizeof(uint8_t));
    base64_decode(argv[3], msg_buf, strlen(argv[3]));

    aes_encrypt_ctr(msg_buf, msg_len, enc_msg_buf, expanded_key_arr, key_len*8, nonce_buf);
    zero_memory(msg_buf, msg_len);
    free(msg_buf);

    size_t enc_base64_len = base64_encode(enc_msg_buf, NULL, msg_len, 0);
    char * enc_base64_buf = malloc((enc_base64_len+1) * sizeof(char));
    base64_encode(enc_msg_buf, enc_base64_buf, msg_len, 0);
    enc_base64_buf[enc_base64_len] = '\x00';
    puts(enc_base64_buf);

    zero_memory(key_buf, key_len);
    free(enc_msg_buf);
    free(enc_base64_buf);

    return 0;
}