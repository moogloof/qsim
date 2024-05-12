#ifndef SIM_H
#define SIM_H

typedef struct {
	double a; // Real part
	double b; // Imaginary part
} complex_t;

#define SQUARENORM(z) (z.a * z.a + z.b * z.b)
#define COMPLEXADD(z, w) ((complex_t){.a = z.a + w.a, .b = z.b + w.b})
#define COMPLEXMULT(z, w) ((complex_t){.a = z.a*w.a - z.b*w.b, .b = z.a*w.b + z.b*w.a})

void init_state(int, int, int, int);
void init_hamiltonian(int, int, int, int);

complex_t* get_state(void);
void update_state(void);

#endif
