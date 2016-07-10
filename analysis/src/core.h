#ifndef _CORE_H_
#define _CORE_H_

/*	Core
 *	William Hazell
 *
 *	This module is intended as a generic job-scheduler for data 
 *	analysis. It acts as the middle man between the data retrieval [data.c]
 *	and the analysis [analysis.c]. It ensures a smooth flow between the 
 *	two modules, and ensures the output end [analysis.c] is never waiting
 *	on the input. This entire module is thread-safe & re-entrant to mimize
 *	the errors from using threads.
 *
 *	Notes:
 *
 *	=> This will use up to MAX_CORE_THREADS (defines.h) threads to speed up 
 *     the program.
 *
 *  => Relies on heap.c implementation of a thread-safe heap
 */

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include "heap.h"
#include "thread_manager.h"
#include "defines.h"
#include "db.h"
#include "data.h"
#include "analysis.h"


/*	struct job:
 *
 *	This defines a job that needs to be ran as soon as a 
 *	free thread is available. It holds the function to call, 
 *	and the arguments to be sent to the function. It also holds 
 *	a function to free the memory for the arguments.
 *
 *
 *	These will be kept in a priority queue [heap.c] to allow for 
 *	load-balancing to be easily done. 
 *
 */
struct job {
	void* (*job_func) (void* args);
	void* args;
	void (*free_args) (void* args);
	int priority;
};


/*  struct job_package:
 *
 *  Since we can only send 1 argument to function that a new thread starts,
 *  there needs to be a way to bundle all the information to send. This structure
 *  holds:
 *
 *  => Current struct job that needs to be ran
 *  => Optional function to run after the job->job_func() is ran
 *  => Callback to free the new arguments 
 *  => The job heap to queue this function up into
 *  
 *  Note: The purpose to include the next_func() is to allow the next function to 
 *  easily be put into the heap.This works well with the way everything is laid out, 
 *  as the return from data.c can easily be put into a new job, then added to the heap
 *  before the thread ends, removing the need to return the result from data.c.
 */
struct job_package {
    struct job* current_job;
    void* (*next_func) (void* args);
    void  (*next_free_args) (void* args);
    struct heap** job_heap;
};

/*	init():
 *
 *	This function performs the necessary set-up for the application to
 *	run. This includes:
 *
 *	-> Connecting to database through db.c directly
 *	-> Setting up the logging through log.c
 *	-> Get the exported functions from analysis.c for use
 *	-> Initialize the thread count semaphore
 *
 *	Once the startup has occurred, the control will be passed to the 
 *	proc_data() function for the "main" running loop. 
 */
void init_core (void);


/*	load_balance():
 *	
 *	This function is used to balance the jobs that are going to 
 *	be run. It is intended to ensure a smooth flow of data, so the 
 *	heap does not fill up with a large amount of the same functions. 
 *	The program should be doing a relatively even amount of both 
 *	making the data (data.c) and analyzing it (analysis.c). What 
 *	this function attempts to avoid situations where analysis is 
 *	waiting on data.c. 
 *
 *	This function is only intended to be used by the main thread, 
 *	while the all other jobs are busy. Instead of just waiting for 
 *	another thread to finish, the main thread might as well also be 
 *	doing something.
 *
 *	Note: Since no other module includes core.h, we can make this
 *		  static in the header without a larger-than-necessary memory
 *		  burden.
 */
static void load_balance ( struct heap* );


/*	start_sched():
 *
 *	This function is the running loop for the main thread. The flow of 
 *	the data is handled here, and in downtime, load_balance() is used. 
 *
 * 	NOTE: Currently with test data, not sending any arguments, but this 
 * 	will need to eventually change.
 *
 */
void start_sched (struct heap*);

#endif

