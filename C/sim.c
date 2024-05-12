#include <sim.h>
#include <stdlib.h>
#include <math.h>

complex_t* state;

double deltax;
double deltay;

void init_state(int w, int h, int tw, int th) {
	state = malloc(sizeof(complex_t) * w * h);

	deltax = (double)tw / w;
	deltay = (double)th / h;

	// Make gaussian
	// Outer coeff
	double outer_coeff = 1.0 / (0.01 * sqrt(M_PI));
}

void init_hamiltonian(int w, int h, int tw, int th) {
}

complex_t* get_state(void) {
	return state;
}

void update_state(void) {
}
