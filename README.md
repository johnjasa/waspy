# waspy - Wing Aerostructural Studies in Python

![WASPY](waspy.jpg)

This repo contains all the files needed to produce the results presented in Jasa et al's 2019 Aviation paper on aerostructural wing design.
We use the aerostructural design tool [OpenAeroStruct](https://github.com/mdolab/OpenAeroStruct) and the optimization framework [OpenMDAO](https://github.com/OpenMDAO/OpenMDAO) for all studies.

## How to run

Waspy requires OpenAeroStruct and OpenMDAO.
Follow the instructions for those packages for installation for your system.
After those are installed, you can install waspy by performing `pip install -e .` in the base level folder within waspy.
You should now be able to run any of the `run_aerostruct.py` files within the subfolders.

## Repo organization

The waspy package includes scripts to run and visualize the results presented in the paper.
Specifically, the repo is organized into three folders: `CRM`, `Q400`, and `tiltwing`, which correspond to the three types of aircraft studied in the paper.
Each one of these folders contains run scripts for all seven cases for each aircraft, resulting in a total of 21 run scripts.

There are some helper files to run all of the cases simultaneously.
In each aircraft folder, there's a `run_all_cases.sh` bash script that launches all seven runs for that aircraft simultaneously.

After all the cases have been run, you can use the bash script `make_and_copy_all_figures.sh` which will create all of the plots shown in the paper.
