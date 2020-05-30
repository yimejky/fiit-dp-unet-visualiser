#!/bin/bash


python $1.py 
pdflatex $1.tex > /dev/null 2>&1

rm *.aux *.log *.vscodeLog
rm *.tex

if [[ "$OSTYPE" == "darwin"* ]]; then
    open $1.pdf
else
    xdg-open $1.pdf
fi
