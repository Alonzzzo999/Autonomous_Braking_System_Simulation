import time
import matplotlib.pyplot as plt
from pid_controller import PIDController


class Simulation:
    def __init__(self):
        # My car state
        self.car_position = 0.0
        self.car_velocity = 20.0
        self.car_acceleration = 0.0

        # Front car state
        self.front_car_position = 50.0
        self.front_car_velocity = 20.0

        # Simulation settings
        self.dt = 0.1
        self.safe_distance = 20.0

        # PID controller
        self.pid = PIDController(kp=0.2, ki=0.01, kd=0.05)

        # Data for graphs
        self.time_data = []
        self.distance_data = []
        self.speed_data = []
        self.front_speed_data = []
        self.brake_data = []
        self.acceleration_data = []

        # Performance tracking
        self.current_time = 0.0
        self.min_distance = float("inf")

    def update_front_car(self):
        # Front car suddenly slows down after 3 seconds
        if self.current_time >= 3.0:
            self.front_car_velocity = 12.0

        self.front_car_position += self.front_car_velocity * self.dt

    def update(self):
        # Update front car
        self.update_front_car()

        # Measure current gap and closing speed
        distance = self.front_car_position - self.car_position
        relative_velocity = self.car_velocity - self.front_car_velocity

        # Track minimum distance reached
        if distance < self.min_distance:
            self.min_distance = distance

        # More proactive error term
        error = (self.safe_distance - distance) + 1.5 * relative_velocity

        brake_force = 0.0

        # Start braking a little earlier than the safe distance
        if distance < self.safe_distance + 5:
            brake_force = self.pid.compute(error, self.dt)

            # Prevent negative braking
            if brake_force < 0:
                brake_force = 0.0

            # Limit unrealistic braking spikes
            brake_force = min(brake_force, 4.0)
        else:
            # Reset PID when not braking
            self.pid.previous_error = 0.0
            self.pid.integral = 0.0

        # Braking creates negative acceleration
        self.car_acceleration = -brake_force

        # Update my car velocity
        self.car_velocity += self.car_acceleration * self.dt
        if self.car_velocity < 0:
            self.car_velocity = 0.0

        # Update my car position
        self.car_position += self.car_velocity * self.dt

        # Save data for graphs
        self.time_data.append(self.current_time)
        self.distance_data.append(distance)
        self.speed_data.append(self.car_velocity)
        self.front_speed_data.append(self.front_car_velocity)
        self.brake_data.append(brake_force)
        self.acceleration_data.append(self.car_acceleration)

        print(
            f"Time: {self.current_time:.1f} | "
            f"Distance: {distance:.2f} | "
            f"My Speed: {self.car_velocity:.2f} | "
            f"Front Speed: {self.front_car_velocity:.2f} | "
            f"Acceleration: {self.car_acceleration:.2f} | "
            f"Brake Force: {brake_force:.2f}"
        )

        self.current_time += self.dt

    def plot_results(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.time_data, self.distance_data, label="Following Distance")
        plt.axhline(y=self.safe_distance, linestyle="--", label="Safe Distance")
        plt.xlabel("Time (s)")
        plt.ylabel("Distance (m)")
        plt.title("Following Distance Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10, 5))
        plt.plot(self.time_data, self.speed_data, label="My Car Speed")
        plt.plot(self.time_data, self.front_speed_data, label="Front Car Speed")
        plt.xlabel("Time (s)")
        plt.ylabel("Speed (m/s)")
        plt.title("Vehicle Speeds Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10, 5))
        plt.plot(self.time_data, self.brake_data, label="Brake Force")
        plt.xlabel("Time (s)")
        plt.ylabel("Brake Force")
        plt.title("Brake Force Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10, 5))
        plt.plot(self.time_data, self.acceleration_data, label="Acceleration")
        plt.xlabel("Time (s)")
        plt.ylabel("Acceleration (m/s²)")
        plt.title("Car Acceleration Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

    def run(self):
        for _ in range(120):
            self.update()
            time.sleep(self.dt)

        print(f"\nMinimum distance reached: {self.min_distance:.2f} m")
        self.plot_results()
