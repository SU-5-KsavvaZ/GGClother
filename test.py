import pickle
import os

user_data_dir = os.path.abspath('data\\user_data.txt')
usr_data = {'gender':{}, 'clothes':{}}
with open(user_data_dir, 'wb') as filehandle:
    pickle.dump(usr_data, filehandle)