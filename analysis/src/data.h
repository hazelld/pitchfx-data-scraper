#ifndef _DATA_H_
#define _DATA_H_

/*	data.h
 *
 *	William Hazell
 *
 *	This module is the layer between the database module (db.c) and the
 *	processing of this data. This layer is meant to deal with the following
 *	problems:
 *	
 *	Public:
 *		=> 	Provide the concrete data structures for the program to use
 *		=> 	Provide a public interface for getting these data structures.
 *		
 *	Hidden:
 *		=> 	Deal with any heavy lifting with making these data structures
 *			(ie. averaging, number crunching etc)
 *		=> 	Cache data structures on disk to cut down on the heavy lifting 
 *			of the number crunching aspects
 *
 */

/* Used for scaffolding for the get_ methods */
#include <time.h>

/* Need access to the thread stuff */
#include "thread_manager.h"

/*	Pitcher Data Structure */
struct pitcher {
	int id;
};


/* Batter Data Structure */
struct batter {
	int id;
};

/*	get_pitcher():
 *
 *	This function is the public interface for getting a pitcher data
 *	structure from the database, through db.c.
 *	
 *	Returns:
 *		Pitcher* :The pitcher object
 *		NULL	 :Pitcher object was not found (wrong ID)
 */
struct pitcher* get_pitcher (int id);


/*	get_batter():
 *
 *	This function is the public interface for getting a batter's data
 *	structure from the database, through db.c.
 *
 *	Returns:
 *		Batter* :The Batter Object
 *		NULL 	:Batter object was not found (wrong ID)
 *
 */
struct batter* get_batter (int id);


/* Used for testing */
extern void* data_stub (void*);

#endif
