#include "core.h"

/* Local functions that are call-backs for heap */
static int compare_jobs (void* job1, void* job2);
static void* copy_job (void* job1, void* job2);
static void free_job (void* job);

/* Local functions used for managing of jobs */
static int init_job(struct job* j, int priority,
					void* (*job_func) (void*), void* args,
					void (*free_args) (void*));
void* start_job (void* args); //entry point of thread 


/* These are the two functions the core will use, one is input and 
 * the other is the output. 
 * [data.c] => Core => [analysis.c] 
 */
void* (*input_func) (void* args);
void* (*output_func) (void* args);

/* These are the setter functions for the global variables above */
static void set_input_func (void* (*input) (void* args)) {
	input_func = input;
}

static void set_output_func (void* (*output) (void* args)) {
	output_func = output;
}


/**/
void init_core (void) {

	struct heap* job_heap = malloc(sizeof(struct heap));

	/* Attempt to connect to database */
	if (db_connect() != SUCCESS) {
		// Error checking
	}

	/* Start the thread manager */
	init_thread_manager();
	init_heap(job_heap, compare_jobs, free_job, copy_job);
    set_output_func(analysis_stub);	
	set_input_func(data_stub);
    /* TODO: Add a populate_heap() method */
    start_sched(job_heap);

	/* Clean up */
	destroy_heap(job_heap);
}


/* Testing Stubs */
void free_stub (void* v) {
    printf("Freeing...\n");
}

/**/
void start_sched (struct heap* job_heap) {

    int test[10]; for(int i = 0; i < 10; i++) {test[i] = i + 1;}
    struct job* current_job;
    struct job_package* job_pack;

    /* Currently for TESTING */
    for (int i = 0; i < 10; i++) {
        struct job* buff_job = malloc(sizeof(struct job));
        init_job (buff_job, test[i], input_func, NULL, free_stub);
        insert_heap(&job_heap, (void*) buff_job);
        printf("Successfully inserted job for input_func with priority of %d\n", i);
    }

	while (!empty(job_heap)) {
		struct job* buff = (struct job*)remove_heap(job_heap);
		int pri = buff->priority;
		printf("Remove priority: %d\n", pri);
	}

    while (1) {
            
        /* Get the next job */
        if (current_job == NULL) 
            current_job = (struct job*) remove_heap(job_heap);

        /* Build our job pack */
        if (job_pack == NULL) {
            printf("Building job pack..\n");
            job_pack = malloc(sizeof(struct job_package));
            job_pack->current_job = current_job;
            job_pack->job_heap = &job_heap;

            /* Currently for TESTING */
            if (current_job->priority % 2 == 0) {
                printf("Setting output function\n");
                job_pack->next_func      = output_func;
                job_pack->next_free_args = free_stub;
            }
        }
    
        /* If the requested thread started, set these to NULL to 
         * ensure we get next job. Memory can't be freed here, as 
         * the thread will be using job_pack. Thread will free this
         * memory.
         */
        if ( request_thread (start_job, (void*)job_pack) == SUCCESS) {
            job_pack    = NULL;
            current_job = NULL;
        }
    }
}



/**/
void* start_job (void* args) {
    
    struct job_package* job_pack = (struct job_package*)args;
    struct job* first_job = job_pack->current_job;
    void* first_job_return;
    
    printf("Starting Job!\n");

    /* Run the first job then free */
    first_job_return =  first_job->job_func(first_job->args);
    free_job(first_job);

    /*  If there is no second function, return */
    if (job_pack->next_func == NULL)
        return NULL;

    /* Build the next job then add to heap */
    struct job* new_job = malloc(sizeof(struct job));
    init_job (new_job, 1, job_pack->next_func, first_job_return,
              job_pack->next_free_args);
    insert_heap(job_pack->job_heap, new_job);
    
    printf("Ending Job!\n");
    /* Free the job pack up we no longer need */
    free(job_pack);
    return NULL;
}


/*	compare_jobs():
 *
 *	This function is the callback used by the heap module to 
 *	compare two items in the heap. 
 *
 *	Returns: (job1->priority - job2->priority)
 *
 *	< 0	 	=>	Job 2 has a higher priority than job 1
 *	= 0 	=>	The jobs have equal priority
 *	> 0		=> 	Job 1 has a higher priority than job 2
 *
 */
static int compare_jobs (void* job1, void* job2) {
	struct job* first  = (struct job*) job1;
	struct job* second = (struct job*) job2;

	return first->priority - second->priority;
}


/*	copy_job():
 *
 *	This function is the callback used by the heap module to 
 *	make a copy of the second argument, and place into the address
 *	pointed to by the first argument. If the first argument is NULL, 
 *	the memory is allocated then returned. 
 *
 */
static void* copy_job (void* job1, void* job2) {
	
	struct job* original;
	struct job* copy;
	
	original = (struct job*) job2;

	if (job1 == NULL)
		copy = malloc(sizeof(struct job));
	else
		copy = job1;

	init_job (copy, original->priority, original->job_func, original->args,
				original->free_args);
	
	return copy;	
}


/*	free_job():
 *
 *	This is the callback function used by the heap module to 
 *	free the memory of a single struct job data structure. 
 *
 */
static void free_job (void* job) {
	struct job* j = (struct job*) job;
	
	/* TODO: free arguments properly */
	free(j);
}


/*	init_job():
 *
 *	This function is used to initialize a struct job data
 *	type with the given arguments. No memory is allocated in 
 *	this function
 *
 */
static int init_job(struct job* j, int priority,
					void* (*job_func) (void*), void* args,
					void (*free_args) (void*)) {
	j->job_func  = (*job_func);
	j->free_args = (*free_args);
	j->args		 = args;
	j->priority  = priority;
	return SUCCESS;
}
