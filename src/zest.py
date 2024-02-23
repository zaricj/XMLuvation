def nextSquare():
    i = 1
 
    # An Infinite loop to generate squares
    while True:
        yield i*i
        i += 1  # Next execution resumes
        # from this point
 
 
# Driver code to test above generator
# function
for num in nextSquare():
    if num > 1000:
        break
    print(num)