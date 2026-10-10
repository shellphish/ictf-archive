; firmware.asm

bits 32
section .text

armed equ 0x20000
target equ 0x20004
voltage equ 0x20008

;
; Initialize firmware.
;
; @return Zero if successful, otherwise non-zero.
;
global firmware_init
firmware_init:
	; load pointers
	mov eax, 0x00
	ret

;
; Enable detonation.
;
; @param sec Seconds.
; @return Zero if successful, otherwise non-zero.
;
global firmware_arm
firmware_arm:
	; check if bomb is already armed
	mov ecx, armed
	mov ecx, [ecx]
	test ecx, ecx
	jz short .disarmed
	mov eax, 0x01
	jmp short .out

.disarmed:
	mov ecx, armed
	mov dword [ecx], 0x01
	mov ecx, [esp+0x04]
	mov edx, target
	mov [edx], ecx
	mov eax, 0x00

.out:
	ret

;
; Disable detonation.
;
; @return Zero if successful, otherwise non-zero.
;
global firmware_disarm
firmware_disarm:
	mov ecx, armed
	mov [ecx], dword 0x00
	mov eax, 0x00
	ret

;
; Return bomb status
;
; @param ts Current time.
; @param[out] Status code.
; @param[out] Seconds remaining until detonation.
; @param[out] Voltage level.
; @return Zero if successful, otherwise non-zero.
;
global firmware_status
firmware_status:
	; check armed flag, set status
	mov eax, armed
	mov ecx, [esp+0x08]
	mov eax, [eax]
	mov [ecx], eax
	test eax, eax
	jz short .disarmed

.armed:
	mov edx, [esp+0x04]
	mov ecx, [esp+0x0c]
	mov ebx, target
	mov ebx, [ebx]
	sub ebx, edx
	mov [ecx], ebx

	mov ecx, [esp+0x10]
	mov edx, voltage
	mov edx, [edx]
	mov [ecx], edx
	jmp short .out

.disarmed:
	mov ecx, [esp+0x0c]
	mov dword [ecx], 0x00
	mov ecx, [esp+0x10]
	mov dword [ecx], 0x00

.out:
	; return success
	mov eax, 0x00
	ret

.w00t:
	jmp .w00t
	jmp .w00t

section .bombreg write

global debug
debug dd 0x1a6e1b23

