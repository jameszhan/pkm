
## Update Anaconda

```bash
conda update conda
conda update anaconda

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes 

conda env list

conda install -c anaconda nb_anacondacloud
conda install --channel anaconda-nb-extensions nbbrowserpdf
```

#### Install Ruby

```bash
rvm install ruby-head-2.5 --url https://github.com/ruby/ruby.git --branch ruby_2_5
rvm use ruby-2.5-head --default


rubocop --auto-gen-config
```

#### Install iRuby

```bash
brew install zeromq
brew install czmq --HEAD
gem install cztop iruby
iruby register --force
```
    
#### TensorFlow

```bash
conda create -n tf15 python=3.6.4
source activate tensorflow

pip install tensorflow
conda install numpy scipy sympy matplotlib scikit-learn scikit-image -n tensorflow

conda deactivate
conda env remove --name tensorflow

conda clean --all --yes
```