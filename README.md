# product-churn-switch
<h3>Python script for finding product churn and switch for a leading telecommunication provider</h3>

This was for a data science project where me and my team developed the necessary machine learning model to predict revenue three years into the future. Before doing so, however, we needed to generate new features (churn and switch) that would aid learning. 

We started to do this manually. For churn, we looked at the rows that had a value for product and went NaN a few months later. Similarly, for switch we were interested in seeing if the value for product was the same after some time. Realising how time-consuming this is to do manually, I was assigned the task to automate the process.

The desired result was to generate new datasets that include churn or switch for the years specified, for each x-month period. We were interested in the years 2018 to 2022 and needed to check for churn and switch after a 3, 6, 9, and 12-month period.

The program does an excellent job of doing this. I even took this a step further so that it can run from command-line and added some useful user-input validation rules.


<u>How the program could be improved:</u>
<ul>
<li>An issue with optimization is that when the program continues running for a second time, and the user decides to use the same data as before, some lines of code that are meant to prepare the data are executed again even if the dataset is already prepared from the privous loop (lines 26 to 32).</li>

<li>Something else that could be improved is user-friendliness. For example, even if the user requires a dataset for the same dates but with a 3 and 6-month period apart for each year, the program should be repeated</li>
</ul>


Although these are no more than half a day's work, the program was more than enough for our purposes.

Thanks for reading!

