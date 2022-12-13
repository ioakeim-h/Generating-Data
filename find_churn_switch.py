
import pandas as pd
import numpy as np
import sys
import re
import warnings
warnings.filterwarnings("ignore")


def main():
    while True:
        if "data" not in locals():
            data = get_data()
        else:
            # if program is running for the second time..
            repeat = input("More requests (yes/no)? ").strip().casefold()
            if repeat == "no":
                sys.exit("It was a pleasure doing business with you")
            different_data = input("Use different data (yes/no)? ").strip().casefold()
            
            if different_data == "yes":
                data = get_data()
        data.columns = [col.lower() for col in data.columns]
        
        # Validate dataset & adjust to date
        for col in ["circuit_id","product_standard","date"]:
            if col not in data.columns:
                sys.exit(f"Exiting: {col} not found in dataset")

        data["date"] = pd.to_datetime(data['date'])
        data["month"] = data["date"].dt.month
        data["year"] = data["date"].dt.year

        s_month, s_year, e_month, e_year, months_forward = get_date(data)
        new_data = adjust_data_to_date(data, s_month, s_year, e_month, e_year, months_forward)
    
    # Request churn or switch
        while True:
            requested_output = input("Type 'churn' or 'switch' to start looking: ").strip().casefold()
            if requested_output in ["churn","switch"]:
                break
            print("Try again")
            
        if requested_output == "churn":
            final_data = find_churn(new_data)
        elif requested_output == "switch":
            final_data = find_switch(new_data)

        # Save file
        file_name = input("Save file as (name.csv or name.xlsx): ").strip()
        print("Saving...")
        
        if ".csv" == file_name[-4:]:
            final_data.to_csv(file_name)
        elif ".xlsx" == file_name[-5:]:
            final_data.to_excel(file_name)
        else:
            final_data.to_csv(f"{file_name}.csv")
            
        print("File saved at current working directory")


def get_data():
    while True:
        import_path = input("Provide the path to the data: ").strip()
        print("Reading data...")
        
        try:
            return pd.read_csv(import_path)
        except FileNotFoundError:
            try:
                return pd.read_excel(import_path)
            except FileNotFoundError:
                print("File not found")


def get_date(data):
    # Valid dates
    min_date = data[["year","month"]].loc[(data["year"] == data["year"].min()) & (data["month"] == data["month"].min())]
    max_date = data[["year","month"]].loc[(data["year"] == data["year"].max()) & (data["month"] == data["month"].loc[data["year"]].max())]

    while True:
        start_date = input("Provide a start date (month-year): ").strip() # format example: 6-2021    
        # Validate input
        if not re.search(r"^\d?\d-\d\d\d\d$", start_date):
            print("Invalid date. Try again")
        else:
            start_month, start_year = start_date.split("-")
            # Validate date range
            below_range = (min_date["month"].unique() > int(start_month)) if start_year == min_date["year"].unique() else (min_date["year"].unique() > int(start_year))
            above_range = (12 < int(start_month)) or (max_date["year"].unique() < int(start_year))
            if not (below_range or above_range):
                break
            print("Date is out of range")

    while True:
        end_date = input("Provide an end date (month-year): ").strip()
        # Validate input
        if not re.search(r"^\d?\d-\d\d\d\d$", end_date):
            print("Invalid date. Try again")
        else:
            end_month, end_year = end_date.split("-")
            # Validate date range
            below_range = min_date["year"].unique() > int(end_year)
            above_range = (max_date["month"].unique() < int(end_month)) if end_year == max_date["year"].unique() else (max_date["year"].unique() < int(end_year)) or (12 < int(end_month))
            if not (below_range or above_range):
                break
            print("Date is out of range")

    while True:
        months_forward = input("How many months to move forward? ").strip()
        if re.search(r"^\d\d?$", months_forward):
            break
        print("Provide a single digit")

    return int(start_month), int(start_year), int(end_month), int(end_year), int(months_forward)


def adjust_data_to_date(data, s_month, s_year, e_month, e_year, months_forward):
    current_month = s_month 
    current_year = s_year 
    
    while True:
        # Execute until end_year reached
        if (current_month + months_forward) >= e_month and current_year >= e_year: 
            break
        
        # Find churn/switch from month A to month B 
        month_A = data[(data['year'] == current_year) & (data['month'] == current_month)]
        
        # For month_B, move x months forward
        if (current_month + months_forward) > 12:
            current_year += 1
            current_month = (current_month + months_forward) - 12
        else:
            current_month += months_forward
        
        month_B = data[(data['year'] == current_year) & (data['month'] == current_month)]
        
        # if new_data does not exist, create it
        if "new_data" not in locals():
            new_data = month_A.merge(month_B[["circuit_id","product_standard"]], how="left", on="circuit_id")
        else:
            # if new_data exists, add to it
            data_to_add = month_A.merge(month_B[["circuit_id","product_standard"]], how="left", on="circuit_id")
            new_data = pd.concat([new_data, data_to_add], ignore_index=True)
    
    new_data.rename(columns={"product_standard_x":"product_standard", "product_standard_y":"product_standard_in_three_months"}, inplace=True)

    return new_data


def find_churn(churn_data):
    # if product missing, then churn (1), else remainer (0)
    churn_data["churn"] = np.where(churn_data["product_standard_in_three_months"].isna(), 1, 0)
    return churn_data


def find_switch(switch_data):
    switchers = switch_data["product_standard"] == switch_data["product_standard_in_three_months"]
    switch_data["switch"] = np.where(switchers, 0, 1)

    # where product_in_three_months is NaN -> churner
    churners = switch_data["switch"].loc[(switch_data["switch"]==1) & (switch_data["product_standard_in_three_months"].isna())]
    switch_data.loc[churners.index, "switch"] = 0

    return switch_data


if __name__ == "__main__":
    main()