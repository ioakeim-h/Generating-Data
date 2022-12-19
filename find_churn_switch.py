
import pandas as pd
import numpy as np

business_data_path = "business_dataset_final_cv.csv"
residential_data_path = "residential_dataset_final_cv.csv"

start_month, start_year = 1, 2018
end_month, end_year = 9, 2022
months_forward_list = [3,6,9,12]


def main():

    business_data = get_data(business_data_path)
    business_data = find_churn_switch(business_data)
    
    business_data.to_csv("business_churn_switch.csv")
    del business_data

    residential_data = get_data(residential_data_path)
    residential_data = find_churn_switch(residential_data)
    
    residential_data.to_csv("residential_churn_switch.csv")
    

def get_data(path):
    data = pd.read_csv(path)

    # Lowercase columns
    data.columns = [col.lower() for col in data.columns]

    # Create month and year variables
    data["date"] = pd.to_datetime(data['date'])
    data["month"] = data["date"].dt.month
    data["year"] = data["date"].dt.year

    data = save_memory(data)

    data_updated = adjust_data_to_dates(
        data, start_month, start_year, end_month, end_year, months_forward_list
    )

    return data_updated


def save_memory(data):

    # Convert dtype object to category
    object_columns = data.select_dtypes("object").columns
    data[object_columns] = data[object_columns].astype("category")

    # Downcast numeric dtypes
    float_columns = data.select_dtypes("float").columns
    integer_columns = data.select_dtypes("integer").columns

    data[float_columns] = data[float_columns].apply(pd.to_numeric, downcast="float")
    data[integer_columns] = data[integer_columns].apply(pd.to_numeric, downcast="integer")

    return data


def adjust_data_to_dates(data, s_month, s_year, e_month, e_year, months_forward_list):
    
    # Set multi index for joins
    data["circuit_id_idx"] = data["circuit_id"]
    data["date_idx"] = data["date"]
    data.set_index(["circuit_id_idx","date_idx"], inplace=True)

    for months_forward in months_forward_list: 
        print(f"months_forward: {months_forward}")

        current_month = s_month
        current_year = s_year

        while (current_month < e_month or current_year < e_year):

            # new_month & new_year shows the months forward limits
            new_month = current_month + months_forward
            new_year = current_year

            # checks if the year has changed
            if new_month > 12:
                new_year += 1
                new_month = new_month - 12

            # checks if the end limits are reached
            if new_year >= e_year and new_month > e_month:
                new_year = e_year
                new_month = e_month

            # Find churn/switch from month A to month B
            month_A = data[["circuit_id","product_standard"]][(data['year'] == current_year) & (data['month'] == current_month)] 
            month_B = data[["circuit_id","product_standard"]][(data['year'] == new_year) & (data['month'] == new_month)] 

            # if new_data does not exist, create it
            if "new_data" not in locals():
                new_data = month_A.join(month_B, lsuffix="", rsuffix=f"_in_{months_forward}_months", how="left")
            else:
                # if new_data exists, add to it
                data_to_add = month_A.join(month_B, lsuffix="", rsuffix=f"_in_{months_forward}_months", how="left")
                new_data = pd.concat([new_data, data_to_add], ignore_index=False)

            current_month += 1
            if current_month > 12:
                current_month = current_month - 12
                current_year += 1
    
        new_data = save_memory(new_data)   
        data = data.join(new_data[f"product_standard_in_{months_forward}_months"], how="left")
        
        del new_data
    
    return data


def find_churn_switch(data):

    for months_forward in months_forward_list:

        #print(f"Finding churn for month: {months_forward}")
        # Find churn: if product missing, then churn (1), else remainer (0)
        data[f"churn_{months_forward}"] = np.where(data[f"product_standard_in_{months_forward}_months"].isna(), 1, 0)
        
        #print(f"Finding switch for month: {months_forward}")
        # Find switch
        switchers = data["product_standard"] == data[f"product_standard_in_{months_forward}_months"]
        data[f"switch_{months_forward}"] = np.where(switchers, 0, 1)

        # where product_in_x_months is NaN -> churner
        churners = data[f"switch_{months_forward}"].loc[(data[f"switch_{months_forward}"]==1) & (data[f"product_standard_in_{months_forward}_months"].isna())]
        data.loc[churners.index, f"switch_{months_forward}"] = 0
    
    #print("Churn and switch done")

    return data


if __name__ == "__main__":
    main()