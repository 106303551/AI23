# Homework 5

## Install Necessary Packages
conda create -n hw5 python=3.11 -y
conda activate hw5
pip install -r requirements.txt

## Training
python pacman.py
## Evaluation
python pacman.py --eval --eval_model_path ./submissions/pacma_dqn.pt