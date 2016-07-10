#include "thread_manager.h"

/**/
void init_thread_manager (void) {
	
	/* Init global semaphore & thread count */
	sem_init(&thread_mutex, 0, 1);
	used_threads = 1;

}


/* Request a thread to start */
int request_thread ( void* (*func) (void*), void* args ) {

    if (free_thread() == FAILURE)
        return FAILURE;

    pthread_t id;

    if (pthread_create(&id, NULL, func, args) ) {
        fprintf(stderr, "Could not create thread.\n");
        return FAILURE;
    }
    
    return SUCCESS;
}


/* Decrement the used_threads variable safely */
static int free_thread (void) {
	int result;

	sem_wait(&thread_mutex);
	if (used_threads < 2) {
		result = FAILURE;
	} else {
		result = SUCCESS;
		used_threads--;
	}
	sem_post(&thread_mutex);
	return result;
}


/* Increment the used_threads variable safely */
static int start_thread (void) {
	int result;

	sem_wait(&thread_mutex);
	if (used_threads >= MAX_CORE_THREADS) {
		result = FAILURE;
	} else {
		result = SUCCESS;
		used_threads++;
	}
	sem_post(&thread_mutex);
	return result;
}
