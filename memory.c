/*******************************************************************************
* Memory management functions.
*
*	Project: Monte Carlo Simulation of Tripple Axis Spectrometers
*	File name: memory.c
*
*	Author: K.N.			Jul  1, 1997
*
*	$Id: memory.c,v 1.2 1997-07-02 07:28:56 kn Exp $
*
*	$Log: not supported by cvs2svn $
*	Revision 1.1  1997/07/01 08:24:20  kn
*	Initial revision
*
*
* Copyright (C) Risoe National Laboratory, 1991-1997, All rights reserved
*******************************************************************************/

#include <string.h>
#include <stdlib.h>

#include "mcstas.h"


/*******************************************************************************
* Allocate memory. This function never returns NULL; instead, the
* program is aborted if insufficient memory is available.
*******************************************************************************/
void *
mem(size_t size)
{
  void *p = malloc(size);
  if(p == NULL)
    fatal_error("memory exhausted during allocation of size %d.", size);
  return p;
}

/*******************************************************************************
* Free memory allocated with mem().
*******************************************************************************/
void memfree(void *p)
{
  if(p == NULL)
    debug(("memfree(): freeing NULL memory.\n"));
  else
    free(p);
}

/*******************************************************************************
* Allocate a new copy of a string.
*******************************************************************************/
char *
str_dup(char *string)
{
  char *s;

  s = mem(strlen(string) + 1);
  strcpy(s, string);
  return s;
}

/*******************************************************************************
* Free memory for a string.
*******************************************************************************/
void
str_free(char *string)
{
  memfree(string);
}
