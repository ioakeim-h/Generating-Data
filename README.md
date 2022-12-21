# Generating-Data
Python script for generating product churn and switch for a leading telecommunication provider


The goal of this program is to extract new features (churn & switch) from certain csv files. These features are used by a machine learning model which predicts revenue three years into the future. 

How it works:

From the date variable it extracts the month and the year and assigns these values to new columns. Using year and month, it then generates new features for churn for each 3, 6, 9 and 12-month period until the end date is reached. Churn is decided if the values in product_standard go missing a few months later. Similarly, switch data are classified as those where the values in product_standard change, but are not missing.

