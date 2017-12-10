while True:
    amount = float(input("Hello, how much change are you owed?"))
    if amount > 0:
        break
# turn into pennies
value = amount * 100
# round float to get a useable integer
value = round(value, 0)
# while change is greater than the value of a quarter, subtract 25 from the value of change
quarter = 25
coin = 0
# each time value of a quarter is subtracted, add 1 to number of coins
while value >= quarter:
    value -= quarter
    coin += 1
# repeat for dimes, nickels, and pennies, counting the number of coins for each subtraction
dime = 10
while value >= dime:
    value -= dime
    coin += 1
nickel = 5
while value >= nickel:
    value -= nickel
    coin += 1
penny = 1
while value >= penny:
    value -= penny
    coin += 1
    
print(str(coin))




