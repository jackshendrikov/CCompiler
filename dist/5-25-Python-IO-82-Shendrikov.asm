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

main PROTO

.code
main PROC
	push ebp
	mov ebp, esp
	sub esp, 0
	;; SET
	mov eax, 4
	;; MULT
	mov ecx, 2
	imul ecx, 3
	;; ADD
	add ecx, 1
	;; MULT
	mov edx, 4
	imul edx, 5
	;; ADD
	add ecx, edx
	;; MULT
	mov edx, 6
	imul edx, 7
	;; ADD
	add ecx, edx
	;; MULT
	imul ecx, eax
	;; SET
	mov eax, ecx
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