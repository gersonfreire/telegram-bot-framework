import pickle

# Sample data to be pickled
data_to_pickle = {'name': 'Alice', 'age': 30, 'city': 'Wonderland'}

# Write the data to a .pickle file
with open('data.pickle', 'wb') as file:
    pickle.dump(data_to_pickle, file)

# Read the data from the .pickle file
with open('data.pickle', 'rb') as file:
    data_unpickled = pickle.load(file)

# Print the data
print(data_unpickled)