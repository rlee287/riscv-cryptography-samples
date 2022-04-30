#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "crypto-algorithms/aes.h"
#include "crypto-algorithms/base64.h"

#define BLOCK_LEN (128/8)

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
    puts("Usage: aes_bin_block base64_enc_key base64_ptxt_block");
}
int main(int argc, char **argv) {
    if (argc != 3) {
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

    if (base64_decode(argv[2], NULL, strlen(argv[2])) != BLOCK_LEN) {
        puts("Message must be a single block (128 bits)");
        return 1;
    }

    uint8_t msg_buf[BLOCK_LEN];
    base64_decode(argv[2], msg_buf, strlen(argv[2]));
    uint8_t enc_msg_buf[BLOCK_LEN];

    aes_encrypt(msg_buf, enc_msg_buf, expanded_key_arr, key_len*8);
    zero_memory(msg_buf, BLOCK_LEN);

    size_t enc_base64_len = base64_encode(enc_msg_buf, NULL, BLOCK_LEN, 0);
    char * enc_base64_buf = malloc((enc_base64_len+1) * sizeof(char));
    base64_encode(enc_msg_buf, enc_base64_buf, BLOCK_LEN, 0);
    enc_base64_buf[enc_base64_len] = '\x00';
    puts(enc_base64_buf);

    zero_memory(key_buf, key_len);
    free(enc_base64_buf);

    return 0;
}