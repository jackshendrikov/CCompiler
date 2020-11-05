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

main PROTO

.data
Caption db "Лабораторна работа №4", 0
Output db "Результат програми: %d", 0ah, 0ah,
          "Автор: Шендріков Євгеній, ІО-82", 0
StrBuf dw ?, 0

.code
main PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; SET
	mov eax, 3
	;; SET
	mov ecx, 7
	;; ADD
	add eax, ecx
	;; RETURN
	mov esp, ebp
	pop ebp
	ret
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