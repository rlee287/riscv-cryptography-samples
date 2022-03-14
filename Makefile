all: rsa_expmod_bin aes_bin

.PHONY: clean

CC_OPTS = -Wall -Wno-pointer-sign -O3 -g -std=c11

crypto-algorithms/base64.o: crypto-algorithms/base64.c crypto-algorithms/base64.h
	$(CC) $(CC_OPTS) -c -o crypto-algorithms/base64.o crypto-algorithms/base64.c
crypto-algorithms/aes.o: crypto-algorithms/aes.c crypto-algorithms/aes.h
	$(CC) $(CC_OPTS) -c -o crypto-algorithms/aes.o crypto-algorithms/aes.c
crypto-algorithms/sha256.o: crypto-algorithms/sha256.c crypto-algorithms/sha256.h
	$(CC) $(CC_OPTS) -c -o crypto-algorithms/sha256.o crypto-algorithms/sha256.c

aes_bin: aes_bin.c crypto-algorithms/aes.o crypto-algorithms/base64.o
	$(CC) $(CC_OPTS) -o aes_bin aes_bin.c crypto-algorithms/aes.o crypto-algorithms/base64.o

clean:
	rm -f *.o crypto-algorithms/*.o aes_bin rsa_expmod_bin