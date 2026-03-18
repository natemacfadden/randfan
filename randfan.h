#ifndef RANDFAN_H
#define RANDFAN_H

#include <stdint.h>

int randfan(
	int * vecs,
	int dim,
	int num_vecs,
	int max_num_simps,
	uint32_t seed,
	uint32_t * simps,
	uint32_t * num_simps
);

#ifdef RANDFAN_IMPLEMENTATION

int randfan(
	int * vecs,
	int dim,
	int num_vecs,
	int max_num_simps,
	uint32_t seed,
	uint32_t * simps,
	uint32_t * num_simps) {

	return 0;
}

#endif

#endif
