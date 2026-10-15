#include "CTFFlag.hpp"

#include <netinet/in.h>
#include <openssl/evp.h>

#define MAGIC 0x31337313
#define FLAG_PAYLOAD_LEN 8
#define HASH_LEN 20
#define FLAG_LEN FLAG_PAYLOAD_LEN + HASH_LEN


static char lookupTable[] = {
  'A','B','C','D','E','F','G','H','I','J','K','L','M',
  'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
  'a','b','c','d','e','f','g','h','i','j','k','l','m',
  'n','o','p','q','r','s','t','u','v','w','x','y','z',
  '0','1','2','3','4','5','6','7','8','9','+','/'
};

static uint8_t lookup(char c) {
  if(c >= 'A' && c <= 'Z'){
    return c - 'A';
  }
  else if(c >= 'a' && c <= 'z'){
    return c - 'a' + 26;
  }
  else if(c >= '0' && c <= '9'){
    return c - '0' + 26 + 26;
  }
  else if(c == '+') {
    return 26 + 26 + 10;
  }
   else if(c == '/') {
    return 26 + 26 + 10 + 1;
  }
  else if(c == '=') {
    return 10 + 26 + 26 + 1 + 1;
  }
  else
    return 255;
}

static string base64enc(const uint8_t* input, uint32_t len) {
  const uint32_t full_blocks = len/3;
  const uint32_t padding =  (len%3) ? 3 - len%3 : 0;
  string ret;
  
  for(uint32_t i=0; i< full_blocks; i++) {
    uint8_t b1 = input[i*3];
    uint8_t b2 = input[i*3+1];
    uint8_t b3 = input[i*3+2];
    
    uint8_t g1 = (b1 >> 2) & 0x3f;
    uint8_t g2 = (b1 << 4 | b2 >>4) & 0x3f;
    uint8_t g3 = (b2 << 2 | b3 >> 6) &0x3f;
    uint8_t g4 = b3 & 0x3f;
    
    ret += lookupTable[g1];
    ret += lookupTable[g2];
    ret += lookupTable[g3];
    ret += lookupTable[g4];
  }
  
  if (padding == 1) {
    uint8_t b1 = input[full_blocks*3];
    uint8_t b2 = input[full_blocks*3+1];

    uint8_t g1 = (b1 >> 2) & 0x3f;
    uint8_t g2 = (b1 << 4 | b2 >>4) & 0x3f;
    uint8_t g3 = (b2 << 2 ) &0x3f;
    
    ret += lookupTable[g1];
    ret += lookupTable[g2];
    ret += lookupTable[g3];
    ret += "=";
  }
  else if(padding == 2) {
    uint8_t b1 = input[full_blocks*3];
    
    uint8_t g1 = (b1 >> 2) & 0x3f;
    uint8_t g2 = (b1 << 4) & 0x3f;

    ret += lookupTable[g1];
    ret += lookupTable[g2];
    ret += "==";
  }
  return ret;
}

bool base64dec(const string& input, uint8_t* output, uint32_t* len) {
  uint8_t modulus = 0; 
  uint8_t padding = 0;
  uint32_t currptr = 0;
  char block[4];
  
  for(string::size_type i=0; i<input.size(); i++) {
    char c = input[i];
    uint8_t g = lookup(c);
    if(g == 255) continue;
    else if (g == 64) {
      // Padding
      block[modulus] = 0;
      padding++;
    }
    else {
      block[modulus] = g;
      padding = 0;
    }

    if(modulus == 3) {
      char cbuf[3];
      cbuf[0] = (block[0]<< 2 | block[1] >> 4) & 0xff;
      cbuf[1] = (block[1] << 4 | block[2] >> 2) & 0xff;
      cbuf[2] = (block[2] << 6 | block[3]) & 0xff;
      
      uint8_t copylen = 3 - padding;
      if(currptr + copylen > *len) {
	// Overflow
	copylen = *len - currptr;
	memcpy(output + currptr, cbuf, copylen);
	return false;
      }
      else {
	memcpy(output + currptr, cbuf, copylen);
	currptr += copylen;
      }
      modulus = 0;
      padding = 0;
    }
    else {
      modulus++;
    }
  }
  
  *len = currptr;
  return true;
}


CTFFlag::CTFFlag(uint8_t teamnum, uint8_t servicenum, uint16_t generation, const string& key) {
  this->teamNum = teamnum;
  this->serviceNum = servicenum;
  this->generation = generation;
  this->key = key;
}

CTFFlag::CTFFlag(const string& flag, const string& key) {
  uint8_t binflag[FLAG_LEN];
  uint32_t len = FLAG_LEN;

  if(!base64dec(flag, binflag, &len)) {
    throw FlagException("Flag too long");
  }
  else if(len != FLAG_LEN) {
    throw FlagException("Flag too short");
  }

  this->key = key;
  teamNum = binflag[4];
  serviceNum = binflag[5];
  this->generation = ntohs(*(uint16_t*)(&binflag[6]));
  
#ifdef DEBUG
  for(int i=0; i<FLAG_LEN; i++) {
    printf("%02hhX ", binflag[i]);
  }
  printf("\n");
#endif

  if( ntohl(*(uint32_t*)(&binflag[0])) != MAGIC ) {
    throw FlagException("Invalid magic");
  }
  
  if(toString() != flag) {
    throw FlagException("Invalid signature");
  }
}

uint8_t CTFFlag::getTeamNum() {
  return teamNum;
}

uint8_t CTFFlag::getServiceNum() {
  return serviceNum;
}

uint16_t CTFFlag::getGeneration() {
  return generation;
}

string CTFFlag::toString() {
  uint8_t flag[FLAG_LEN];
  EVP_MD_CTX hash_ctx;

  *(uint32_t*)(&flag[0]) = htonl(MAGIC);
  flag[4] = teamNum;
  flag[5] = serviceNum;
  *(uint16_t*)(&flag[6]) = htons(generation);
  
  if(!EVP_DigestInit(&hash_ctx, EVP_sha1())) {
    throw FlagException("Error creating digest conrtext");
  }
  if(!EVP_DigestUpdate(&hash_ctx, flag, FLAG_PAYLOAD_LEN)) {
    throw FlagException("Error updating digest");
  }
  if(!EVP_DigestUpdate(&hash_ctx, key.c_str(), key.size())) {
    throw FlagException("Error updating digest");
  }

  uint32_t len = HASH_LEN;
  if(!EVP_DigestFinal(&hash_ctx, &flag[FLAG_PAYLOAD_LEN], &len) || len != HASH_LEN) {
    throw FlagException("Error calculating digest");
  }

  
#ifdef DEBUG
  for(int i=0; i<FLAG_LEN; i++) {
    printf("%02hhX ", flag[i]);
  }
  printf("\n");
#endif

  return base64enc(flag, FLAG_LEN);
   
}
