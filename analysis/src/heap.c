#include "heap.h"


/* Local functions */
static void upheapify (struct heap* h, int index);
static void downheapify (struct heap* h, int index);
static int validate_heap (struct heap* h);
static void flip_values (struct heap* h, int index1, int index2);

/**/
int init_heap (	struct heap* h, int (*compare) (void*, void*), 
				void (*destroy) (void*), void* (*copy_value) (void*, void*)) {

	sem_init (&heap_mutex, 0, 1);

	h->count = 0;

	h->compare      = (*compare);
	h->copy_value   = (*copy_value);
	h->destroy_item = (*destroy);
	
	return validate_heap(h);
}


/*TODO: remove double pointer */
int insert_heap (struct heap** h, void* item) {
	
	sem_wait (&heap_mutex);
	
	if (validate_heap(*h) == FAILURE) {
		sem_post(&heap_mutex);
		return FAILURE;
	}
	
	(*h)->heap[++(*h)->count] = (*h)->copy_value(NULL, item);
	upheapify((*h), (*h)->count);
	sem_post(&heap_mutex);
	return SUCCESS;
}


/**/
void* remove_heap (struct heap* h) {
	sem_wait(&heap_mutex);
	void* retval = h->copy_value(NULL, h->heap[1]);
	h->heap[1] = h->copy_value(h->heap[1], h->heap[h->count]);
	h->destroy_item(h->heap[h->count]);
	h->count--;
	downheapify(h, 1);
	sem_post(&heap_mutex);
	return retval;
}


/* validate_heap():
 *
 * This function is used to ensure the heap is still valid after
 * a malloc or realloc call.
 *
 */
static int validate_heap (struct heap* h) {
	if (h->heap) 
		return SUCCESS;
	else
		return FAILURE;
}


/*	upheapify():
 *
 *	Recursive function to restore the heap-property after
 *	an insert. 
 *
 * 	Note: This is only called within the critical section 
 * 	of the insert function. Because of this, no locking of 
 * 	the semaphore is needed.
 *
 */
static void upheapify (struct heap* h, int index) {
	int parent;

	if ((index % 2) == 0)
		parent = index / 2;
	else
		parent = (index - 1) / 2;

	if (parent < 1 || index == 0 || index == parent) 
		return;
	

	if (h->compare(h->heap[index], h->heap[parent]) > 0) {
		flip_values(h, parent, index);
		upheapify(h, parent);
	}
}

/*	downheapify():
 *
 *	Recursive function to restore the heap-property after
 *	a removal
 *
 * 	Note: This is only called within the critical section
 * 	of the remove function. Because of this, no locking of the 
 * 	semaphoer is needed.
 */
static void downheapify (struct heap* h, int index) {
	int lc, rc, cmp;

	lc = index * 2;
	rc = (index * 2) + 1;

	if (lc > h->count && rc > h->count)
		return;

	/* Only left child & no right */
	if ( (lc == h->count) && (rc > h->count)) {
		
		if (h->compare(h->heap[index], h->heap[lc]) > 0) { return; }
		else {
			flip_values(h, index, lc);
			return;
		}
	}

	/* Decide whih child to flip */
	if (h->compare(h->heap[lc], h->heap[rc]) >= 0)
		cmp = lc;
	else if (h->compare(h->heap[lc], h->heap[rc]) < 0)
		cmp = rc;

	/* If child is larger than parent, flip */
	if (h->compare(h->heap[cmp], h->heap[index]) >= 0) {
		flip_values (h, index, cmp);
		downheapify (h, cmp);
	}
}


/**/
static void flip_values (struct heap* h, int index1, int index2) {
	void* temp;
	temp = h->copy_value(NULL, h->heap[index1]);
	h->copy_value(h->heap[index1], h->heap[index2]);
	h->copy_value(h->heap[index2], temp);
	h->destroy_item(temp);
}


/**/
void destroy_heap (struct heap* h) {
	
}


/**/
int empty (struct heap* h) {
	int result;
	sem_wait(&heap_mutex);
	if (h->count > 0)
        result = 0;
    else 
        result = 1;
	sem_post(&heap_mutex);
	return result;
}
