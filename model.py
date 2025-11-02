import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset, DataLoader
import pandas as pd


file_path = r"C:\datasets\cleaned_emails.csv"

file_path = r"C:\datasets\cleaned_emails.csv" 
output_file = "sample_emails.csv"

if os.path.exists(file_path):
    # Read first 10 rows, skipping any malformed lines
    data = pd.read_csv(file_path, on_bad_lines='skip').head(10)

    # Save those rows to a new CSV file in the current directory
    data.to_csv(output_file, index=False)

    print(f"✅ First 10 emails copied to '{output_file}'")
    print(data)
else:
    print(f"❌ File not found: {file_path}")
    
class DiscordDataset(Dataset):
    def __init__(self, texts, labels, vocab, tokenizer, label_map):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.label_map = label_map

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        tokens = self.tokenizer(self.texts[idx])
        indices = [self.vocab.get(t, self.vocab["<unk>"]) for t in tokens]
        label = self.label_map[self.labels[idx]]
        return torch.tensor(indices, dtype=torch.long), torch.tensor(label, dtype=torch.long)
    

def collate_fn(batch):
    texts, labels = zip(*batch)
    texts_padded = pad_sequence(texts, batch_first=True, padding_value=0)
    labels = torch.stack(labels)
    return texts_padded, labels


class SentimentAnalysisLSTM(nn.Module):
    def __init__(
        self, vocab_size,
        embedding_dim,
        hidden_dim,
        output_dim,
        num_layers,
        dropout
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            embedding_dim, hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        embedded = self.dropout(self.embedding(x))
        lstm_out, (hidden, cell) = self.lstm(embedded)

        # Concatenate final forward and backward hidden states
        hidden = self.dropout(torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1))

        return self.fc(hidden)
    

def predict_sentiment(model, text, tokenizer, vocab, device, max_length=100):
    """
    Given a text string, return the next sequence of tokens
    """
    ...