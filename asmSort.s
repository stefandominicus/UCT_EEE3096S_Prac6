/*-- EEE3096S 2018 --*/
/*-- Prac 6 / Mini Project A --*/

/*-- CTTKIE001 --*/
/*-- DMNSTE001 --*/

/*-- Sort implemented using assembly --*/
/*-- This sorting algorithm is only used in 'Unsecure Mode', and thus only needs to sort the array of durations (direction does not matter) --*/

.data

unsorted_array: .skip 64	/* 16x4 */
sorted_array: .skip 64

input_message: .asciz "The array to be sorted is:"
.balign 4
output_message: .asciz "The sorted array is:"

.balign 4
return_link: .word 0

.text

.global main
main:
	ldr r1, return_link
	str lr, [r1]				/* save the link register */

	/*-- Code here --*/

	ldr r0, =input_message
	bl printf

	/*-- End of algorithm --*/

	ldr lr, =return_link
	ldr lr, [lr]				/* replace the original link register */
	bx ldr						/* exit main usign link register */

/*-- External --*/
.global printf