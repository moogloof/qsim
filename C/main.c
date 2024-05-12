#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <SDL.h>

#define SIM_WIDTH 640
#define SIM_HEIGHT 480

int main(int argc, char** argv) {
	SDL_Window* window = NULL;
	SDL_Renderer* renderer = NULL;

	// Initialize SDL video
	if (SDL_Init(SDL_INIT_VIDEO) < 0) {
		printf("Video init error :: %s\r\n", SDL_GetError());
	} else {
		// Create the window and renderer
		if (SDL_CreateWindowAndRenderer(0, 0, SDL_WINDOW_FULLSCREEN | SDL_WINDOW_INPUT_GRABBED, &window, &renderer) < 0) {
			printf("Window and renderer creation error :: %s\r\n", SDL_GetError());
		} else {
			// Set sim size
			if (SDL_RenderSetLogicalSize(renderer, SIM_WIDTH, SIM_HEIGHT) < 0) {
				printf("Error setting logical size :: %s\r\n", SDL_GetError());
			} else {
				int quit = 0;
				SDL_Event event;
				unsigned long frame_duration = 0;

				// Streaming texture
				SDL_Texture* buffer = SDL_CreateTexture(renderer, SDL_PIXEL_FORMATBGRA8888, SDL_TEXTUREACCESS_STREAMING, SIM_WIDTH, SIM_HEIGHT);

				// Random seed
				srand(time(NULL));

				// Sim loop
				while (!quit) {
					frame_duration = SDL_GetTicks64();

					SDL_SetRenderDrawColor(renderer, 0xff, 0xff, 0xff, 0xff);
					SDL_RenderClear(renderer);

					SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0xff);
					for (int i = 0; i < 100; i++)
						SDL_RenderDrawPoint(renderer, rand() % SIM_WIDTH, rand() % SIM_HEIGHT);

					SDL_RenderPresent(renderer);

					// Check if quit yet
					while (SDL_PollEvent(&event)) {
						// End loop on quit
						if (event.type == SDL_QUIT) {
							quit = 1;
						}
					}

					// Cap at 100 FPS so it doesn't go too fast
					frame_duration = SDL_GetTicks64() - frame_duration;
					if (frame_duration < 10)
						SDL_Delay(10 - frame_duration);
				}
			}
		}
	}

	// Cleanup
	SDL_DestroyWindow(window);
	SDL_DestroyRenderer(renderer);
	SDL_Quit();

	return 0;
}
