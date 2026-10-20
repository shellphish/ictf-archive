/*********************************************************************
 * @file          ubersecurecrypt.h
 * @version
 * @brief
 * @author        badnack <n.redini@gmail.com>
 * @date          Wed Dec  4 21:20:25 2013
 * Modified at:   Thu Dec  5 13:46:47 2013
 * Modified by:   badnack <n.redini@gmail.com>
 ********************************************************************/

extern unsigned char uberhash[];

int create_forward_secure_tokens(const unsigned char [], unsigned int ,  unsigned char [], int);
int init_uberhash();
int is_it_valid(unsigned char [], unsigned int, unsigned char [], unsigned int, int);
int convert_moves_to_buffer(char [], unsigned int, unsigned char [], unsigned int *);
