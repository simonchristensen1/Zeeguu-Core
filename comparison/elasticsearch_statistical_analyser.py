import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from elasticsearch import Elasticsearch
from pandasticsearch import Select

for i in range(1, 6):
    df = pd.read_csv("eminem_test.csv")
    df = df.loc[(df['Difficulty'] == i)]

    data_np = df.values  # converting to numpy
    unique_classes = np.unique(data_np[:, 1])
    data_dict = {}

    for u_class in unique_classes:
        class_data = data_np[data_np[:, 1] == u_class, :] # masks out rows from class
        data_dict.update({u_class: {'x': class_data[:, 4], 'y': class_data[:, 2]}})
        plt.plot(data_dict[u_class]['x'], data_dict[u_class]['y'], label=u_class)
    plt.ylabel('Time in MS')
    plt.xlabel('Returned articles')
    plt.title('Difficulty ' + str(i))
    plt.legend()
    plt.show()

