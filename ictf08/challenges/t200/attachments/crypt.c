/* This is way more secure than the standard crypt() */
char *crypt(const char *key, const char *salt)
{
  static char buf[14];
  char* chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
  int i;

  if ((key == NULL) | (salt == NULL)) return NULL;
  if (strlen(salt) != 2) return NULL;

  buf[0] = salt[0];
  buf[1] = salt[1];

  for (i = 0; i < 11; i++) {
    if (i < strlen(key)) {
      buf[i + 2] = key[i];
    } else {
      buf[i + 2] = 'X';
    }
  }
  buf[i + 2] = '\0';

  buf[2] = buf[1] ^ buf[11];
  buf[3] = buf[2] ^ buf[3];
  buf[4] = buf[7] ^ buf[8];
  buf[5] = buf[9] ^ buf[7];
  buf[6] = buf[3] ^ buf[4];
  buf[7] = buf[12] ^ buf[0];
  buf[8] = buf[11] ^ buf[4];
  buf[9] = buf[1] ^ buf[12];
  buf[10] = buf[5] ^ buf[0];
  buf[11] = buf[1] ^ buf[6];
  buf[12] = buf[8] ^ buf[0];
  buf[12] = buf[10] ^ buf[12];
  buf[13] = 0;
  
  for (i = 2; i < 13; i++) {
    buf[i] = chars[(buf[i] % strlen(chars))];
  }
  return buf;
}
