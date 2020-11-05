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
Caption db "Лабораторна работа №5", 0
Output db "Результат програми: %d", 0ah, 0ah,
          "Автор: Шендріков Євгеній, ІО-82", 0
StrBuf dw ?, 0

sum PROTO
counter PROTO
int_ret PROTO
call_function PROTO
return_const PROTO
main PROTO

.code
sum PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; LOADARG
	;; LOADARG
	;; ADD
	mov eax, edi
	add eax, esi
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
sum ENDP

counter PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; LOADARG
	;; ADD
	mov eax, edi
	add eax, 1
	;; SET
	mov edi, eax
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
counter ENDP

int_ret PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; SET
	mov ecx, 3
	;; DIV
	mov eax, 3
	cdq
	idiv ecx
	mov ecx, eax
	;; SET
	;; RETURN
	mov eax, ecx
	mov esp, ebp
	pop ebp
	ret
int_ret ENDP

call_function PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; LOADARG
	mov eax, edi
	;; LOADARG
	;; LOADARG
	;; CALL
	mov edi, esi
	mov esi, edx
	call eax
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
call_function ENDP

return_const PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; SET
	mov eax, 4
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
return_const ENDP

main PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; ADDROF
	lea eax, [sum]
	;; CALL
	mov edi, 3
	mov esi, 4
	call eax
	;; NOTEQUALCMP
	mov ecx, 1
	cmp eax, 7
	jne __JackShenC_label14
	mov ecx, 0
__JackShenC_label14:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label1
	;; RETURN
	mov eax, 1
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label1:
	;; ADDROF
	lea eax, [sum]
	;; CALL
	mov edi, 5
	mov esi, 2
	call eax
	;; NOTEQUALCMP
	mov ecx, 1
	cmp eax, 7
	jne __JackShenC_label15
	mov ecx, 0
__JackShenC_label15:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label2
	;; RETURN
	mov eax, 2
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label2:
	;; ADDROF
	lea eax, [counter]
	;; CALL
	mov edi, 5
	call eax
	;; NOTEQUALCMP
	mov ecx, 1
	cmp eax, 6
	jne __JackShenC_label16
	mov ecx, 0
__JackShenC_label16:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label3
	;; RETURN
	mov eax, 4
	mov esp, ebp
	pop ebp
	ret
	;; JUMP
	jmp __JackShenC_label4
	;; LABEL
__JackShenC_label3:
	;; ADDROF
	lea eax, [int_ret]
	;; CALL
	call eax
	;; NOTEQUALCMP
	mov ecx, 1
	cmp eax, 1
	jne __JackShenC_label17
	mov ecx, 0
__JackShenC_label17:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label5
	;; RETURN
	mov eax, 5
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label5:
	;; LABEL
__JackShenC_label4:
	;; ADDROF
	lea eax, [return_const]
	;; CALL
	call eax
	;; SET
	;; NOTEQUALCMP
	mov ecx, 1
	cmp eax, 4
	jne __JackShenC_label18
	mov ecx, 0
__JackShenC_label18:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label6
	;; RETURN
	mov eax, 10
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label6:
	;; ADDROF
	lea eax, [call_function]
	;; ADDROF
	lea edi, [sum]
	;; CALL
	mov esi, 7
	mov edx, 7
	call eax
	;; EQUALCMP
	mov ecx, 1
	cmp eax, 14
	je __JackShenC_label19
	mov ecx, 0
__JackShenC_label19:
	;; JUMPZERO
	cmp ecx, 0
	je __JackShenC_label7
	;; RETURN
	mov eax, 222
	mov esp, ebp
	pop ebp
	ret
	;; LABEL
__JackShenC_label7:
	;; RETURN
	mov eax, 0
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