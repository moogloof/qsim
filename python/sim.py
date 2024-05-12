import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import numpy as np
import imageio


xybins = 51
true_wh = 6.0
delta_xy = true_wh / (xybins - 1)
delta_t = 0.01

# Utility function
# Return distance from axis
def generate_axis_dist(x0, y0):
	axis_distx = np.linspace(-true_wh / 2, true_wh / 2, xybins) + x0
	axis_disty = np.linspace(-true_wh / 2, true_wh / 2, xybins) + y0

	return axis_distx, axis_disty

# Utility function
# Distance from some point
def generate_point_dist(x0, y0):
	axis_distx, axis_disty = generate_axis_dist(x0, y0)

	axis_distx = np.repeat(axis_distx[np.newaxis, ...], xybins, axis=0)
	axis_disty = np.repeat(axis_disty[..., np.newaxis], xybins, axis=1)

	return (axis_distx**2) + (axis_disty**2)

# Utilitry function
# Diag distance from axis
def generate_diag_dist(x0):
	diag_dist = np.linspace(-true_wh / 2, true_wh / 2, xybins) + x0
	diag_dist = np.diag(diag_dist)

	return diag_dist

# Generate gaussian wave discrete state
def gaussian_wave(x0, y0, px, py, sigmax=0.2, sigmay=0.2):
	distx, disty = generate_axis_dist(x0, y0)

	new_state_x = (1/((np.pi * sigmax ** 2) ** 0.25)) * np.exp(1j * px * distx) * np.exp(-(distx ** 2)/(2 * (sigmax ** 2)))
	new_state_y = (1/((np.pi * sigmay ** 2) ** 0.25)) * np.exp(1j * py * disty) * np.exp(-(disty ** 2)/(2 * (sigmay ** 2)))

	return new_state_x[np.newaxis, ...], new_state_y[np.newaxis, ...]

# At point
T = -4 * np.eye(xybins, k=0)
# Neighboring y
T += np.eye(xybins, k=1) + np.eye(xybins, k=-1)
T = np.kron(np.identity(xybins), T)
# Neighboring x
T += np.eye(xybins ** 2, k=xybins) + np.eye(xybins ** 2, k=-xybins)
# Apply coefficient
T = -(1/(2 * (delta_xy ** 2))) * T

"""
	* NOTE FOR PROGRAMMER
	* USE THE BELOW SPACE TO DEFINE PRESETS
"""
# Harmonic oscillator
# Default static potential
V = generate_point_dist(0, 0)

oscillator_strength = 300
V_oscillatorx, V_oscillatory = generate_axis_dist(0, 0)
V_oscillatorx, V_oscillatory = np.repeat((V_oscillatorx ** 2)[np.newaxis, ...], xybins, axis=0), np.repeat((V_oscillatory ** 2)[..., np.newaxis], xybins, axis=1)
V_oscillatorx *= oscillator_strength
V_oscillatory *= oscillator_strength

# Wave packet state
statex, statey = gaussian_wave(0, 0, 0, 0, 1, 1)
state = np.kron(statex, statey)[..., np.newaxis]

# Update state
def progress_state(frame):
	global T
	global V
	global V_oscillator
	global state

	"""
		* NOTE FOR PROGRAMMER
		* USE THE BELOW SPACE TO DEFINE V
		* THE KEY IS TO DEFINE V, FOR EXAMPLE:
		* V = generate_point_dist(0, 0)
		*
		* THE EXAMPLE BELOW IS AN ION TRAP
	"""
	V = -V_oscillatorx * np.cos(100 * frame * delta_t * np.pi) + V_oscillatory

	"""
		* THE FOLLOWING SHOULD NOT BE CHANGED
		* IMPLEMENTATION OF THE CRANK-NICHOLSON ALGORITHM
	"""
	H = T + np.diag(V.flatten())
	explicit_matrix = np.identity(xybins * xybins) - 1j * delta_t * H
	implicit_matrix = np.identity(xybins * xybins) + 1j * delta_t * H

	# Update state
	state = explicit_matrix @ state
	state = np.linalg.solve(implicit_matrix, state)

	return state

# Update frame
def update(frame):
	global colormap_dict
	global heatmap_img
	global field_img
	global state
	global V

	# Display
	mat_state = np.flip(np.reshape(state, (xybins, xybins)).T, axis=0)
	prob_dist = np.real(mat_state * np.conjugate(mat_state))
	heatmap = np.stack([(np.imag(np.log(mat_state)) + np.pi) / (2 * np.pi), np.ones((xybins, xybins)), prob_dist], axis=2)
	heatmap = colors.hsv_to_rgb(heatmap)

	progress_state(frame)

	heatmap_img.remove()
	heatmap_img = ax1.imshow(heatmap)

	field_img.remove()
	field_img = ax2.imshow(np.flip(V.T, axis=0) / np.max([np.max(V), -np.min(V)]), vmin=-1, vmax=1, cmap=colormap_dict)

	return heatmap_img, field_img


# Main program
if __name__ == "__main__":
	prompt = input("Save to video (y/n)? ").lower()
	if prompt == "y":
		duration = float(input("How long in seconds? "))
		print("Saving to sim.gif...")
		vid_fps = int(1 / delta_t)

		total_frames = int(vid_fps * duration)
		img_list = []

		with imageio.get_writer("sim.gif", mode="I", fps=vid_fps) as vid_writer:
			for frame in range(total_frames):
				print(f"Frame {frame}")
				mat_state = np.flip(np.reshape(state, (xybins, xybins)).T, axis=0)
				prob_dist = np.real(mat_state * np.conjugate(mat_state))

				heatmap = np.stack([(np.imag(np.log(mat_state)) + np.pi) / (2 * np.pi), np.ones((xybins, xybins)), prob_dist], axis=2)
				heatmap = 255 * colors.hsv_to_rgb(heatmap)

				fieldmap = np.flip(V.T, axis=0) / np.max([np.max(V), -np.min(V)])
				fieldmap = 255 * np.stack([np.maximum(fieldmap, 0), np.zeros((xybins, xybins)), -np.minimum(fieldmap, 0)], axis=2)

				heatmap = np.hstack((heatmap, fieldmap))

				progress_state(frame)

				vid_writer.append_data(heatmap.astype("uint8"))
	elif prompt == "n":
		print("Starting live sim...")
		fig, (ax1, ax2) = plt.subplots(1, 2)

		ax1.axis("off")
		ax2.axis("off")

		heatmap_img = plt.imshow([[0,0]])
		field_img = plt.imshow([[0, 0]])

		colormap_dict = colors.LinearSegmentedColormap.from_list("rb", ["blue", "black", "red"])

		heatmap_img, field_img = update(0)
		anime = animation.FuncAnimation(fig, update, frames=None, cache_frame_data=False)

		try:
			plt.show()
		except KeyboardInterrupt:
			print("Killed successfully!")
	else:
		print("Bye.")
