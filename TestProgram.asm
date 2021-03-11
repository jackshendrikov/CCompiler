.386
.model flat, stdcall
option casemap:none

include \masm32\include\windows.inc
include \masm32\include\masm32.inc
include \masm32\include\kernel32.inc
include \masm32\include\user32.inc
includelib \masm32\lib\masm32.lib
includelib \masm32\lib\kernel32.lib
includelib \masm32\lib\user32.lib

.data
Caption db "Test Program", 0
Output db   "——————————————————", 0ah,
			"|                          RESULT                          |", 0ah,
			"——————————————————", 0ah, 0ah,
			"Program Result: %d", 0ah, 0ah,
			"Author: Shendrikov Yevhenii", 0
StrBuf dw ?, 0

main PROTO

.code
main PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; SET
	mov edx, 0
	;; SET
	mov ecx, 10
	;; SET
	mov ecx, 0
	;; LABEL
__JackShenC_label1:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 10
	jne __JackShenC_label36
	mov eax, 0
__JackShenC_label36:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label3
	;; ADD
	mov eax, edx
	add eax, ecx
	;; SET
	mov edx, eax
	;; SET
	mov eax, 0
	;; LABEL
__JackShenC_label2:
	;; SET
	mov eax, ecx
	;; ADD
	add ecx, 1
	;; SET
	;; JUMP
	jmp __JackShenC_label1
	;; LABEL
__JackShenC_label3:
	;; NOTEQUALCMP
	mov eax, 1
	cmp edx, 45
	jne __JackShenC_label37
	mov eax, 0
__JackShenC_label37:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label4
	;; RETURN
	mov eax, 1
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label4:
	;; SET
	mov edx, 0
	;; SET
	mov ecx, 20
	;; LABEL
__JackShenC_label5:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 80
	jne __JackShenC_label38
	mov eax, 0
__JackShenC_label38:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label7
	;; ADD
	mov eax, edx
	add eax, ecx
	;; SET
	mov edx, eax
	;; LABEL
__JackShenC_label6:
	;; MULT
	mov eax, ecx
	imul eax, 2
	;; SET
	mov ecx, eax
	;; JUMP
	jmp __JackShenC_label5
	;; LABEL
__JackShenC_label7:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 80
	jne __JackShenC_label39
	mov eax, 0
__JackShenC_label39:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label8
	;; RETURN
	mov eax, 2
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label8:
	;; NOTEQUALCMP
	mov eax, 1
	cmp edx, 60
	jne __JackShenC_label40
	mov eax, 0
__JackShenC_label40:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label9
	;; RETURN
	mov eax, 3
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label9:
	;; SET
	mov edx, 0
	;; LABEL
__JackShenC_label10:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 100
	jne __JackShenC_label41
	mov eax, 0
__JackShenC_label41:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label12
	;; ADD
	mov eax, edx
	add eax, ecx
	;; SET
	mov edx, eax
	;; LABEL
__JackShenC_label11:
	;; ADD
	add ecx, 1
	;; SET
	;; JUMP
	jmp __JackShenC_label10
	;; LABEL
__JackShenC_label12:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 100
	jne __JackShenC_label42
	mov eax, 0
__JackShenC_label42:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label13
	;; RETURN
	mov eax, 4
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label13:
	;; NOTEQUALCMP
	mov eax, 1
	cmp edx, 1790
	jne __JackShenC_label43
	mov eax, 0
__JackShenC_label43:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label14
	;; RETURN
	mov eax, 5
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label14:
	;; SET
	mov edx, 0
	;; LABEL
__JackShenC_label15:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 110
	jne __JackShenC_label44
	mov eax, 0
__JackShenC_label44:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label17
	;; ADD
	add edx, ecx
	;; SET
	;; SET
	mov eax, ecx
	;; ADD
	add ecx, 1
	;; SET
	;; LABEL
__JackShenC_label16:
	;; JUMP
	jmp __JackShenC_label15
	;; LABEL
__JackShenC_label17:
	;; NOTEQUALCMP
	mov eax, 1
	cmp ecx, 110
	jne __JackShenC_label45
	mov eax, 0
__JackShenC_label45:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label18
	;; RETURN
	mov eax, 6
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label18:
	;; NOTEQUALCMP
	mov eax, 1
	cmp edx, 1045
	jne __JackShenC_label46
	mov eax, 0
__JackShenC_label46:
	;; JUMPZERO
	cmp eax, 0
	je __JackShenC_label19
	;; RETURN
	mov eax, 7
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label19:
	;; SET
	mov eax, 0
	;; LABEL
__JackShenC_label20:
	;; SET
	mov ecx, eax
	;; ADD
	add eax, 1
	;; SET
	;; EQUALCMP
	mov ecx, 1
	cmp eax, 10
	je __JackShenC_label47
	mov ecx, 0
__JackShenC_label47:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label23
	;; JUMP
	jmp __JackShenC_label22
	;; LABEL
__JackShenC_label23:
	;; LABEL
__JackShenC_label21:
	;; JUMP
	jmp __JackShenC_label20
	;; LABEL
__JackShenC_label22:
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
main ENDP

start:
	invoke main
	invoke wsprintf, ADDR StrBuf, ADDR Output, eax
	invoke MessageBox, 0, ADDR StrBuf, ADDR Caption, MB_ICONINFORMATION
	invoke ExitProcess, 0
end start