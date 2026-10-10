; utility functions

bits 32
section .text

global get_sp
get_sp:
	mov eax, esp
	ret

global get_fp
get_fp:
	mov eax, ebp
	ret

