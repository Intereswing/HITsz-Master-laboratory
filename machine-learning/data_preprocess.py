import torch
import torch.nn as nn
import pandas as pd


train_data = pd.read_csv('data/train.csv')
# Get the dimension length
T = len(train_data['date'].unique())
N = len(train_data['store_nbr'].unique())
families = list(train_data['family'].unique())

# calculate the date's index
previous_date = train_data.iloc[0]['date']
date_index = 0

# traverse the raw data
train_dataset = torch.zeros(T, N, len(families), 2) # one for promotion and one for sales.
for i in range(len(train_data)):
    row_data = train_data.iloc[i]
    if row_data['date'] != previous_date:
        date_index += 1 # come to a new day
        previous_date = row_data['date']

    # the store number start from 1, but in code it will be 0.
    train_dataset[date_index , row_data['store_nbr'] - 1, families.index(row_data['family'])] = \
        torch.tensor([row_data['onpromotion'], row_data['sales']])

print(train_dataset.shape)
torch.save(train_dataset, 'data/train.pt')

