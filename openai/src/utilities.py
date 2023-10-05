import pickle

def write_to_pickle(data, file_path):
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)
        print("Data successfully written to pickle file:", file_path)
    except Exception as e:
        print("Error writing data to pickle file:", e)

def read_from_pickle(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        print("Data successfully read from pickle file:", file_path)
        return data
    except Exception as e:
        print("Error reading data from pickle file:", e)
        return None
