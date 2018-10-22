/* asmSort.s */
/*  CTTKIE001, DMNSTE001  */

/*--------------------------
@ declare variables
r0 - text for printf
r1 - data for printf
r4 - current minimum value
r5 - address of array to sort
r6 - current number to be compared
r7 - outer loop counter
r8 - inner loop counter
r9 - base address of srt_array
r10 - element that has been moved
r11 - temp copy of current element
--------------------------*/

.data
array: .word 17, 20, 1, 4
item_print: .asciz "%d, "	@print item
new_line: .asciz "\n"

.text
.global main
.func main

main:
	PUSH {LR} 			@save current link register
	mov r7, #0			@initialize loop counters
	mov r8, #0

outer_loop:
	mov r8, r7 			@start from where the previous loop left off
	ldr r5, =array 			@get base address
	ldr r4, [r5,r7]			@base address with outer offset

inner_loop:
	ldr r5, =array 			@get base address
	ldr r6, [r5,r8]			@base address with inner offset
	cmp r6, r4			@check r6<r4
	blt swap_elements		@if r6<r4, branch

continue:
	add r8, r8, #4			@increase inner counter by 4
	cmp r8, #16			@has inner loop reached the end?
	blt inner_loop			@not yet finished. loop inner again
	add R7, R7, #4			@increment outer loop counter
	cmp R7, #16 			@has outer loop reached the end?
	blt outer_loop 			@not yet finished. loop outer again
	mov r7, #0			@get ready to start from the beginning

print_sorted:
	ldr r5, =array 			@get base address
	ldr r0, =item_print		@set print style
	ldr r1, [r5,r7]			@set data to print
	@mov r1, r4
	bl printf			@print element
	add r7, r7, #4			@increment counter
	cmp r7, #16			@check if reached the end
	blt print_sorted		@not at end - print next element

end:
	ldr r0, =new_line		@set text for new line
	bl printf			@print new line
	POP {PC}			@return to where the program was
	mov PC, LR

swap_elements:
	mov r11, r4			@save r4 to temp
	mov r4, r6			@set r4 <- r6
	str r4, [r5, r7]		@put r6 into outer location
	str r11, [r5, r8]		@put r4 into inner location
	b continue			@return to function
