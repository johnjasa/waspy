#!/usr/bin/env bash
shopt -s expand_aliases
source ~/.bashrc
cd engine_mass
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
cd engine_thrust
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
cd fuel_weight
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
cd struct_weight
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
cd viscous
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
cd wave_drag
nohup python run_aerostruct.py > out.txt 2>&1 & disown;
cd ..
