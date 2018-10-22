/*-- EEE3096S 2018 --*/
/*-- Prac 6 / Mini Project A --*/

/*-- CTTKIE001 --*/
/*-- DMNSTE001 --*/

/*-- Sort implemented using assembly --*/
/*-- This sorting algorithm is only used in 'Unsecure Mode', and thus only needs to sort the array of durations (direction does not matter) --*/

.data

unsorted_array: .skip 64	/* 16x4 */
sorted_array: .skip 64

input_message: .asciz "The array to be sorted is: [%u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u]\n"
.balign 4
output_message: .asciz "The sorted array is: [%u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u]\n"

.balign 4
end_of_main: .word 0

.text

.global main
main:
	ldr r1, =end_of_main
	str lr, [r1]				/* save the link register */

	/*-- Code here --*/

	ldr r0, =input_message
	ldr r1, =unsorted_array
	bl printf					/* print the input message

outer_loop:
	/* r4 - outer counter */
	cmp r4, #15
	beq end_outer_loop
	

inner_loop:
	/* r3 - inner counter */

end_inner_loop:

	b outer_loop

end_outer_loop:





end_main:
	ldr lr, =end_of_main
	ldr lr, [lr]				/* replace the original link register */
	bx ldr						/* exit main usign link register */

/*-- External --*/
.global printf