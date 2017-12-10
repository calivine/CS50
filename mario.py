while True:
    height = int(input("Height: ")) # user inputs an integer
    if height < 24 and height >= 0:
        break
counter = height
row = 0
offset = 1
while counter > 0:
    space = 1
    while space <= height - offset:
        print(" ", end = "")
        space += 1
    row +=1
    offset += 1
    hash = 0
    for hash in range(row):
        print("#", end = "")
    print("#", end = "")
    counter -= 1
    print("\n", end = "")
    