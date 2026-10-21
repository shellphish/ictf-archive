#!/usr/bin/env python3

def caesar_encrypt(plaintext, shift):
    result = ""
    
    for char in plaintext:
        if char.isalpha():  # Check if the character is a letter
            shift_base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            result += char  # Non-alphabetic characters are not encrypted

    return result

def caesar_decrypt(ciphertext, shift):
    return caesar_encrypt(ciphertext, -shift)  # Decrypt by reversing the shift

plaintext = "Then he looked behind him and saw that no land was visible. That makes no difference, he thought. I can always come in on the glow from Havana. There are two more hours before the sun sets and maybe he will come up before that. If he doesn't maybe he will come up with the moon. If he does not do that maybe he will come up with the sunrise. I have no cramps and I feel strong. It is he that has the hook in his mouth. But what a fish to pull like that. He must have his mouth shut tight on the wire. I wish I could see him. I wish I could see him only once to know what I have against me."
password = 10

ciphertext = caesar_encrypt(plaintext, password)
print(f"Encrypted: {ciphertext}")  # Output: KHOOR

decrypted_text = caesar_decrypt(ciphertext, password)
print(f"Decrypted: {decrypted_text}")  # Output: HELLO
