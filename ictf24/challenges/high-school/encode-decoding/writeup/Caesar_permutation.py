#!/usr/bin/env python3

encrypt_table = {'a': 't', 'b': 'm', 'c': 'q', 'd': 'v', 'e': 'y', 'f': 'r', 'g': 'p', 'h': 'e', 'i': 'k', 'j': 'a', 'k': 'c', 'l': 'o', 'm': 'f', 'n': 'h', 'o': 'u', 'p': 'l', 'q': 'i', 'r': 'z', 's': 'w', 't': 'b', 'u': 'j', 'v': 'g', 'w': 'd', 'x': 'x', 'y': 'n', 'z': 's'}

dencrypt_table = {'t': 'a', 'm': 'b', 'q': 'c', 'v': 'd', 'y': 'e', 'r': 'f', 'p': 'g', 'e': 'h', 'k': 'i', 'a': 'j', 'c': 'k', 'o': 'l', 'f': 'm', 'h': 'n', 'u': 'o', 'l': 'p', 'i': 'q', 'z': 'r', 'w': 's', 'b': 't', 'j': 'u', 'g': 'v', 'd': 'w', 'x': 'x', 'n': 'y', 's': 'z'}

def caesar_encrypt(plaintext):
    result = ""
    
    for char in plaintext:
        
        if char.isalpha():  # Check if the character is a letter
            shift_base = ord('A') if char.isupper() else ord('a')
            if chr((ord(char) - shift_base ) % 26+ord('a')) in encrypt_table.keys():
                result += encrypt_table[chr((ord(char) - shift_base ) % 26 + ord('a'))]
            else:
                result += char
        else:
            result += char  # Non-alphabetic characters are not encrypted

    return result

def caesar_decrypt(ciphertext):
    result = ""
    
    for char in ciphertext:
        
        if char.isalpha():  # Check if the character is a letter
            shift_base = ord('A') if char.isupper() else ord('a')
            if chr((ord(char) - shift_base ) % 26+ord('a')) in dencrypt_table.keys():
                result += dencrypt_table[chr((ord(char) - shift_base ) % 26 + ord('a'))]
            else:
                result += char
        else:
            result += char  # Non-alphabetic characters are not encrypted

    return result

plaintext = "Now, there were two possessions of the James Dillingham Youngs in which they both took a mighty pride. One was Jim's gold watch that had been his father's and his grandfather's. The other was Della's hair. Had the Queen of Sheba lived in the flat across the airshaft, Della would have let her hair hang out the window some day to dry just to depreciate Her Majesty's jewels and gifts. Had King Solomon been the janitor, with all his treasures piled up in the basement, Jim would have pulled out his watch every time he passed, just to see him pluck at his beard from envy."


ciphertext = caesar_encrypt(plaintext)
print(f"Encrypted: {ciphertext}")  # Output: KHOOR

decrypted_text = caesar_decrypt(ciphertext)
print(f"Decrypted: {decrypted_text}")  # Output: HELLO
