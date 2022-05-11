all: native riscv

native: rsa_sign_bin_native aes_bin_native aes_bin_block_native numeric_passcode_native

riscv: rsa_sign_bin_riscv aes_bin_riscv aes_bin_block_riscv numeric_passcode_riscv

.PHONY: clean native riscv

CC_OPTS = -Wall -Wno-pointer-sign -O3 -g -std=c11
CXX_OPTS = -Wall -O3 -g -std=c++11

crypto-algorithms/native:
	mkdir crypto-algorithms/native
crypto-algorithms/riscv:
	mkdir crypto-algorithms/riscv

crypto-algorithms/native/base64.o: crypto-algorithms/base64.c crypto-algorithms/base64.h | crypto-algorithms/native
	gcc $(CC_OPTS) -c -o $@ $<
crypto-algorithms/native/aes.o: crypto-algorithms/aes.c crypto-algorithms/aes.h | crypto-algorithms/native
	gcc $(CC_OPTS) -c -o $@ $<
crypto-algorithms/native/sha256.o: crypto-algorithms/sha256.c crypto-algorithms/sha256.h | crypto-algorithms/native
	gcc $(CC_OPTS) -c -o $@ $<

crypto-algorithms/riscv/base64.o: crypto-algorithms/base64.c crypto-algorithms/base64.h | crypto-algorithms/riscv
	riscv64-linux-gnu-gcc $(CC_OPTS) -c -o $@ $<
crypto-algorithms/riscv/aes.o: crypto-algorithms/aes.c crypto-algorithms/aes.h | crypto-algorithms/riscv
	riscv64-linux-gnu-gcc $(CC_OPTS) -c -o $@ $<
crypto-algorithms/riscv/sha256.o: crypto-algorithms/sha256.c crypto-algorithms/sha256.h | crypto-algorithms/riscv
	riscv64-linux-gnu-gcc $(CC_OPTS) -c -o $@ $<

rsa_sign_bin_native: rsa_sign_bin.cc crypto-algorithms/native/sha256.o crypto-algorithms/native/base64.o | crypto-algorithms/native
	g++ $(CXX_OPTS) -o $@ $^
rsa_sign_bin_riscv: rsa_sign_bin.cc crypto-algorithms/riscv/sha256.o crypto-algorithms/riscv/base64.o | crypto-algorithms/riscv
	riscv64-linux-gnu-g++ -static $(CXX_OPTS) -o $@ $^

aes_bin_native: aes_bin.c crypto-algorithms/native/aes.o crypto-algorithms/native/base64.o | crypto-algorithms/native
	gcc $(CC_OPTS) -o $@ $^
aes_bin_riscv: aes_bin.c crypto-algorithms/riscv/aes.o crypto-algorithms/riscv/base64.o | crypto-algorithms/riscv
	riscv64-linux-gnu-gcc -static $(CC_OPTS) -o $@ $^

aes_bin_block_native: aes_bin_block.c crypto-algorithms/native/aes.o crypto-algorithms/native/base64.o | crypto-algorithms/native
	gcc $(CC_OPTS) -o $@ $^
aes_bin_block_riscv: aes_bin_block.c crypto-algorithms/riscv/aes.o crypto-algorithms/riscv/base64.o | crypto-algorithms/riscv
	riscv64-linux-gnu-gcc -static $(CC_OPTS) -o $@ $^

numeric_passcode_native: numeric_passcode.c
	gcc $(CC_OPTS) -o $@ $^
numeric_passcode_riscv: numeric_passcode.c
	riscv64-linux-gnu-gcc -static $(CC_OPTS) -o $@ $^

clean:
	rm -f *.o crypto-algorithms/native/*.o crypto-algorithms/riscv/*.o aes_bin_native aes_bin_block_native numeric_passcode_native rsa_sign_bin_native aes_bin_riscv aes_bin_block_native numeric_passcode_riscv rsa_sign_bin_riscv
