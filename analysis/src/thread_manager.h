#ifndef _THREAD_MANAGER_H_
#define _THREAD_MANAGER_H_

#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include "defines.h"

/*	thread_mutex => Semaphore to safely change used_threads value
 *	used_threads => Number of currently used threads
 */
sem_t thread_mutex;
int used_threads;


/*	init_thread_manager():
 *	
 *	This function is used to initialize this module. This should always
 *	be called prior to using the other functions, as this will initialize all
 *	the semaphore and other default values.
 *
 */
void init_thread_manager();


/*	free_thread():
 *
 *	This function is used to safely decrement the value 
 *	of the used_threads variable. This ensures this variable
 *	is thread-safe.
 *	
 *	Returns:
 *		Success => Successfully decremented variable
 *		Failure => Somehow the used_threads is negative. This
 *				   is mainly for debugging purposes.
 */
static int free_thread (void);


/*	init_thread():
 *
 *	This function is used to safely increment the value of 
 *	the used_threads variable. This ensures this variable is thread
 *	safe.
 *
 *	Returns:
 *		Success => Incremented the variable successfully.
 *		Failure	=> Thread Cap has already been reached.
 */
static int init_thread (void);


/*  request_thread():
 *
 *  This function is used to request the start of a thread. It
 *  ensures the max amount of threads has not been reached, then
 *  will start the thread it is given.
 *
 *  Returns:
 *      SUCCESS => Thread was ran properly 
 *      FAILURE => Thread could not be started 
 */
int request_thread ( void* (*func) (void*), void* args );

#endif
