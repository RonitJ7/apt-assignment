# Thought Process 

## Approach
### Volume
I started by trying to find volume. I quickly observed that the column **neuronCount** had a significantly higher magnitude than every other column. It was also the only column that was **always positive** throughout the entire dataset. It also had **no decimal points** to it. These are all obviously necessary for Volume, as it must be a positive integer (since it is the count of shares or contracts traded). **All these requirements were satisfied** in every single row by the neuronCount column and so we can conclude with **confidence 1** that neuronCount is volume.

### High and Low
Now, we know High must be greater than Low, Open and Close. Since we are not provided information about how price is calculated, we cannot yet say High is greater than Price. Similarly for Low, it must be smaller than High, Open and Close. Another intuitive way to think about it is that Low must be the column that is smaller than the most amount of other columns. We can say the same about high. This is how we get candidate high and candidate low. Then, for these candidate high and low, we check how many rows it is greater and lesser respectively than every other column in the row. 

### Open and Close 

Next, I checked for the ..... values across rows using ........... logic. I found that ................

Then, I inspected `deltaX`, `flux`, and `pulse`. These showed .............

### Challenges (and how I overcame)
The data was very noisy and we were not getting values for high and low. So we decided to try and denoise it. 


### Confidence 
<columnwise confidence analysis based on some statistics of your choice>

### Summary
Overall, I combined ...................................................... to derive the mapping. I also wrote a ........................... 




