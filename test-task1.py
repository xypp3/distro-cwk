from matplotlib import pyplot as plt
import requests
import time
import os

num_of_sensors = [1, 10, 50, 100, 500, 1000, 5000, 10000]
response_times = [-1.0 for i in range(len(num_of_sensors))]

url = input("Function url: ")

for i in range(len(num_of_sensors)):
    start = time.perf_counter()
    requests.get(url + f"&num={num_of_sensors[i]}")
    end = time.perf_counter()
    response_times[i] = end - start

    print(f"Benchark on {num_of_sensors[i]} done! and it took {response_times[i] :0.3f} seconds")

plt.title("Benchmark for Task 1")
plt.xlabel("Number of sensors")
plt.ylabel("Response time in (seconds)")  # TODO: this unit
plt.plot(num_of_sensors, response_times)

# save before displaying
my_path = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(my_path, "benchmark.png"))

plt.show()
