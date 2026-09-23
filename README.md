# Industrial-TSFM

面向工业时间序列的基础模型（Time-Series Foundation Model, TSFM）在线推理与可视化演示平台。

本仓库基于公开工业时间序列数据，集成 Toto 2.0 和 Chronos-2 等开源时间序列基础模型，实现多变量时间序列的零样本预测，并通过 Streamlit 构建模拟实时数据流的在线推理界面。


## Environment

推荐环境：
```
Python >= 3.12
PyTorch >= 2.5
Streamlit >= 1.51
NVIDIA GPU + CUDA
```
创建虚拟环境：
```shell
python3.12 -m venv .venv
source .venv/bin/activate
```
升级 pip：
```shell
python -m pip install --upgrade pip
```
安装依赖：
```shell
python -m pip install -r requirements.txt
```


## Supported Models

当前支持以下时间序列基础模型。

| Model | Parameters | Main Capability |
|---|---|---|
| Toto-2.0-22m | 22M | Multivariate probabilistic forecasting |
| Chronos-2-Small | 28M | Zero-shot time-series forecasting |

模型权重不包含在本 Git 仓库中，需要单独下载至 models/ 目录。

```shell
# download toto-2.0
hf download Datadog/Toto-2.0-22m \
    --local-dir models/Toto-2.0-22m

# download chronos-2
hf download amazon/chronos-2 \
    --local-dir models/Chronos-2
```

## Download ETTm1

创建数据目录：

```shell
mkdir -p data
```
可以使用 Hugging Face CLI 下载公开镜像：
```shell
hf download pkr7098/time-series-forecasting-datasets \
    ETTm1.csv \
    --repo-type dataset \
    --local-dir data
```

激活项目环境：
```shell
source .venv/bin/activate
```
启动 Streamlit：
```shell
streamlit run app.py
```
然后在浏览器访问：http://localhost:8501
