import pickle

def load_user_info():
    data = dict()
    try:
        with open('user_data.pickle', 'rb') as file:
            data = pickle.load(file)
            print(data)
    except Exception as error:
        print('load_user_info: ', error)
    finally:
        return data
    

if __name__ == "__main__":
    load_user_info()