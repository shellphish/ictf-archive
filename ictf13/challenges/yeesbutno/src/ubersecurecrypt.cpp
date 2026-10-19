#include <openssl/sha.h>
#include <openssl/aes.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
//#include <gmp.h>

#include "ubersecurecrypt.h"
#include "util.h"

int create_forward_secure_tokens(const unsigned char ibuf[], unsigned int len,  unsigned char ohash[], int steps);

int min(int a, int b)
{
    if (a > b) {
        return b;
    } else {
        return a;
    }
}

int create_forward_secure_tokens(const unsigned char ibuf[], unsigned int len,  unsigned char ohash[], int steps);

//int
int dohash(unsigned char tohash[], unsigned int len, unsigned char ohash[])
{
    unsigned char IVPASS[] = "PRENEELAPPROVESMAYBE";
    unsigned char IV[20];
    unsigned char *encrypted;
    unsigned char *toencrypt;
    unsigned int aes_block_size = 16;
    AES_KEY aes_encryptKey;
    unsigned int outsize;

    outsize = (len / aes_block_size) * aes_block_size;
    if (len % aes_block_size > 0) {
        outsize += 16;
    }

    encrypted = (unsigned char *) malloc(outsize);
    assert(encrypted != NULL);
    toencrypt = (unsigned char *) malloc(outsize);
    assert(toencrypt != NULL);

    memset(toencrypt, 0, outsize);
    memcpy(toencrypt, tohash, len);


    SHA1(IVPASS, strlen((char *)IVPASS), IV);

    AES_set_encrypt_key(IV, 128, &aes_encryptKey);

    AES_cbc_encrypt(toencrypt, encrypted, outsize, &aes_encryptKey, IV, AES_ENCRYPT);
    memcpy(ohash, encrypted+outsize-16, 16);

    return 0;
}

int create_challenge_1()
{
    int r;
    //mpq_t x;
    r = rand() % 2;
    return r;
}

int create_forward_secure_tokens(const unsigned char ibuf[], unsigned int len,  unsigned char ohash[], int steps)
{
    unsigned char tohash[1024];
    int lentohash = len;
    unsigned char hash[1024];
    memcpy(tohash, ibuf, len);
    memcpy(hash, ibuf, min(len, 16));


    int i;

    for (i = 0; i < steps; i++) {
        //SHA1(tohash, lentohash, hash);
        dohash(tohash, lentohash, hash);
        memcpy(tohash, hash, 16);
        lentohash = 16;
    }
    memcpy(ohash, hash, 16);


    return 0;

}


int is_it_valid(unsigned char token[], unsigned int toklen, unsigned char password[], unsigned int passlen, int steps)
{
    unsigned char hash[20];
    create_forward_secure_tokens(password, passlen, hash, steps);
    if (memcmp((void *)hash, (const void *)token, 16) ==  0) {
        return 1;
    } else {
        return 0;
    }
}

int convert_moves_to_buffer(char moves[], unsigned int len, unsigned char buffer[], unsigned int *buflen)
{
    unsigned int i;
    int j = 0;
    *buflen = 0;

    int s;
    int idx;
    for (i = 0; i < len; i++,j = (j+1) %4) {
        idx = i / 4;
        if (i % 4 == 0) {
            buffer[idx] = 0;
        }

        switch (moves[i]) {
        case 'w':
            s = 0;
            break;

        case 'n':
            s = 1;
            break;

        case 's':
            s = 2;
            break;

        case 'e':
            s = 3;
            break;

        default:
            break;
        }

        buffer[idx] = (char) (((int)(buffer[idx])) + (s << (2*j)));
        *buflen = idx + 1;
    }
    return 0;
}

//int is_prime
int vulnerable_function1(char in[], int len)
{

    char *cur;
    cur = in + len;
    *cur -= *cur;
    return 0;
}
