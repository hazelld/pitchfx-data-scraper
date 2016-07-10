#ifndef _HEAP_H_
#define _HEAP_H_

/*	Heap
 *	William Hazell
 *
 *	This module is a thread-safe read/write heap. It 
 *	is as generic as possible to ensure it can be re-used.
 *
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <semaphore.h>
#include "defines.h"

/* Define the max heap size */
#define MAX_HEAP 100

/* This is the lock to ensure the heap isn't being modified 
 * by another thread before modifying heap. 
 */
sem_t heap_mutex;

/*	struct heap:
 *
 *	Heap data structure.
 */
struct heap {
	void* heap[MAX_HEAP];
	int count;
	
	/* Call-back to compare items */
	int (*compare) (void*, void*);

	/* Call-back to swap 2 items safely */
	void* (*copy_value) (void*, void*);

	/* Call-back to free memory of item */
	void (*destroy_item) (void*);

};


/*	init_heap():
 *
 *	This function is used to set the values of a struct heap* that has
 *	already been allocated in memory. It sets the default variables, and 
 *	the provided callbacks. 
 *
 *	This function also inits the semaphore used to ensure thread-safety. 
 *
 */
int init_heap (	struct heap* h, int (*compare) (void*, void*), 
				void (*destroy) (void*), void* (*copy_value) (void*, void*));


/*	insert_heap():
 *
 *	This function is used to safely insert into the heap. It takes a pointer
 *	to a pointer to a struct heap, as realloc is used within the function. Since
 *	this has to be thread-safe, this has to be done to prevent other threads from 
 *	now having invalid pointers to the old heap.
 *
 */
int insert_heap (struct heap** h, void* item);


/*	remove_heap():
 *
 *	This function removes the top item of the heap, 
 *	then restores the heap property. The item off the 
 *	top of the heap will be returned to the caller, and 
 *	the caller is responsible to free all memory.
 *
 * 	This function doesn't need a double pointer as the pointer 
 * 	will never change, as we leave the memory alloc'd.
 */
void* remove_heap (struct heap* h);


/*	destroy():
 *
 *	This function frees all memory used by the heap by using 
 *	the callback function destroy_item() that is provided on 
 *	init. 
 *
 */
void destroy_heap (struct heap* h);


/*  empty():
 *
 *  This function returns whether or not the heap is empty.
 *
 *  Returns:
 *  
 *      SUCCESS => Heap is empty
 *      FAILURE => Heap isnt empty
 */
int empty (struct heap* h);
#endif
