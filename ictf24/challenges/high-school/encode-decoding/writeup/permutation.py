import random
import string

def generate_permutation_table():
    # Create a list of lowercase alphabet letters
    alphabet = list(string.ascii_lowercase)
    
    # Create a copy of the alphabet and shuffle it to create a permutation
    permuted_alphabet = alphabet[:]
    random.shuffle(permuted_alphabet)
    print(permuted_alphabet)
    
    # Create a dictionary (hash table) to store the mapping
    hash_table = {original: permuted for original, permuted in zip(alphabet, permuted_alphabet)}
    hash_table_2 = {original: permuted for original, permuted in zip(permuted_alphabet, alphabet)}
    
    return hash_table, hash_table_2

# Generate the 26-character permutation hash table
permutation_table,permutation_table_2 = generate_permutation_table()

# Print the resulting hash table
print(permutation_table)
print(permutation_table_2)

