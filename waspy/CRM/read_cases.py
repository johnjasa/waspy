from __future__ import division, print_function
import pickle
from waspy.all_read_cases import load_all_cases, print_results, plot_thicknesses, plot_lifts, folders


read_OM_db = True

if read_OM_db:
    data = load_all_cases()
    with open('data.pkl', 'wb') as f:
        pickle.dump(data, f)
else:
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)

print_results(data)
plot_thicknesses(data, folders)
plot_lifts(data, folders)
