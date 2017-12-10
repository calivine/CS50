import sys

if len(sys.argv) != 2:
    print("Usage: python caesar.py key")
    exit(1)
if str.isalpha(sys.argv[1]):
    print("Key must be a number.")
    exit(2)
key = int(sys.argv[1])
plain = input("plaintext: ")
cipher = []
i = 0
for c in plain:
    if str.isalpha(c):
        if str.islower(c):
            cipher.append(chr(((((ord(c) - 97) + key) % 26) + 97)))
        elif str.isupper(c):
            cipher.append(chr(((((ord(c) - 65) + key) % 26) + 65)))
    else:
        cipher.append(c)
    i += 1
st1 = ''.join(cipher)
print("ciphertext: " + st1)
exit(0)

