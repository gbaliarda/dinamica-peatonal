import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 6, 8]

# Perform linear regression
coefficients = np.polyfit(x, y, 1)
slope = coefficients[0]
intercept = coefficients[1]

# Calculate the line of best fit
line = slope * np.array(x) + intercept

# Plotting
plt.scatter(x, y, color='blue', label='Data points')
plt.plot(x, line, color='red', label='Linear regression')

# Customize the plot
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Linear Regression')
plt.legend()

# Show the plot
plt.show()
