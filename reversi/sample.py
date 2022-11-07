import time
import random
# % % time

randome_elements = random.sample(range(0, 10000000), 1000)
list_seq = list(range(100000))  # Point

counter = 0
for ele in randome_elements:
    if ele in list_seq:
        counter += 1

set_seq = set(range(100000))  # Point

print(type(list_seq))
print(type(set_seq))
