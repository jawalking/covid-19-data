#!/usr/bin/python3
import os
import csv

import sh
from matplotlib import pyplot as plt

state_to_filter_by = ["Arizona", "New York", "California"]
images_to_open=[]

# Get latest from git
sh.git(f"--git-dir={os.path.join(os.path.dirname(os.path.abspath(__file__)),'.git')}",f"--work-tree={os.path.dirname(os.path.abspath(__file__))}","pull")

base_path = os.path.dirname(os.path.abspath(__file__))
all_states_csv_path = os.path.join(base_path, "us-states.csv")
for state in state_to_filter_by:
    az_state_csv_path = os.path.join(base_path, f"{state}_cases_and_deaths.csv")
    new_cd_fig_path = os.path.join(base_path, f"{state}_new_cases_and_deaths_per_day.png")
    total_cd_fig_path = os.path.join(base_path, f"{state}_total_cases_and_deaths_per_day.png")

    # Calculate how many of the deaths and cases are "new" and write out the data to an Arizona only file
    plot_new_cases = []
    plot_new_deaths = []
    plot_total_cases = []
    plot_total_deaths = []
    with open(all_states_csv_path) as read_csv_file:
        daily_numbers = csv.DictReader(read_csv_file)
        
        with open(az_state_csv_path, mode='w') as write_csv_file:
            fieldnames = ['date', 'state', 'fips', 'cases', 'deaths', 'new cases', "new deaths"]
            writer = csv.DictWriter(write_csv_file, fieldnames=fieldnames)
            writer.writeheader()

            day_minus_one = None
            for day in daily_numbers:
                if day['state'] == state:
                    if day_minus_one is not None:
                        day['new cases'] = int(day['cases']) - int(day_minus_one['new cases'])
                        day['new deaths'] = int(day['deaths']) - int(day_minus_one['new deaths'])
                    else:
                        day['new cases'] = int(day['cases'])
                        day['new deaths'] = int(day['deaths'])
                        
                    plot_new_cases.append(int(day['new cases']))
                    plot_new_deaths.append(int(day['new deaths']))
                    plot_total_cases.append(int(day['cases']))
                    plot_total_deaths.append(int(day['deaths']))
                    writer.writerow(day)
                    
                    day_minus_one = day

    # Plot new instances
    fig = plt.figure(dpi = 128, figsize = (10,6))
    nc = plt.plot(plot_new_cases, c = 'blue', label='New Cases per Day')
    nd = plt.plot(plot_new_deaths, c = 'red', label='New Deaths per Day')
    plt.title(f"{state} Daily COVID-19 Progression", fontsize = 24)
    plt.xlabel('Days Since First Case',fontsize = 16)
    plt.ylabel("People", fontsize = 16)
    plt.tick_params(axis = 'both', which = 'major' , labelsize = 16)
    plt.legend(loc="upper left")
    plt.savefig(new_cd_fig_path)
    images_to_open.append(new_cd_fig_path)


    # Plot totals
    fig = plt.figure(dpi = 128, figsize = (10,6))
    plt.plot(plot_total_cases, c = 'blue', label='Total Cases as-of Day')
    plt.plot(plot_total_deaths, c = 'red', label='Total Deaths as-of Day')
    plt.title(f"{state} Daily COVID-19 Totals", fontsize = 24)
    plt.xlabel('Days Since First Case',fontsize = 16)
    plt.ylabel("People", fontsize = 16)
    plt.tick_params(axis = 'both', which = 'major' , labelsize = 16)
    plt.legend(loc="upper left")
    plt.savefig(total_cd_fig_path)
    images_to_open.append(total_cd_fig_path)

# Open plots
sh.open("-a", "Preview", images_to_open)
