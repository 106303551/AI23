conda create -y -n ai_hw6 python=3.10
conda activate ai_hw6

install pytorch based on your cuda version
pip install --no-deps trl peft accelerate bitsandbytes
pip install tqdm packaging wandb

based on cuda version install the correct version of unsloth (detailed information is here)
我使用的安裝方法:
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps xformers "trl<0.9.0" peft accelerate bitsandbytes

Verify if the installation was successful.:
nvcc
python -m xformers.info
python -m bitsandbytes

訓練模型:
num_epoch 設定為1

bash run.sh "ORPO" "unsloth/tinyllama-bnb-4bit" "請提供 wandb token"
bash run.sh "DPO" "unsloth/tinyllama-bnb-4bit" "請提供 wandb token"