#!/usr/bin/env bash
cd CRM
python read_cases.py
cd ..

cd Q400
python read_cases.py
cd ..

cd tiltwing
python read_cases.py
cd ..

cp CRM/*.pdf ~/Dropbox/git/jasa_aviation_2019/figures/CRM/.
cp Q400/*.pdf ~/Dropbox/git/jasa_aviation_2019/figures/Q400/.
cp tiltwing/*.pdf ~/Dropbox/git/jasa_aviation_2019/figures/tiltwing/.
