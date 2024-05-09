# Define a simple function
def add(a, b):
    return a + b

# Test the function with pytest
def test_add():
    assert add(2, 3) == 5  # Expected output is 5
    assert add(-1, 1) == 0  # Expected output is 0
    assert add(0, 0) == 0  # Expected output is 0

# Another function to test
def multiply(a, b):
    return a * b

# Test the multiply function
def test_multiply():
    assert multiply(3, 4) == 12  # Expected output is 12
    assert multiply(0, 5) == 0  # Expected output is 0
    assert multiply(2, 2) == 4  # Expected output is 4
