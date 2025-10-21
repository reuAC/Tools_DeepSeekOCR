# Tools_DeepSeekOCR
该项目基于 DeepSeek-OCR 实现了一个截图程序，能够在Windows平台部署模型并用于截图OCR识别。  
[ 中文 | [English](./README.md) ]
## 系统前提
在进行安装之前，您需要确保如下依赖已安装  
1. Python >= 3.9  
    1.1 Python网址 [https://www.python.org/downloads/release/python-3140/](https://www.python.org/downloads/release/python-3140)  
    将页面划到最下方，有一名为Files的表格，其中有各个版本的安装文件，如Windows 64位使用 `Windows installer (64-bit)`
2. CUDA (安装时候自己显卡的CUDA驱动)  
    2.1 CUDA网址 [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)  
    根据设备系统版本下载 CUDA Toolkit Installer 并安装即可
  
注意：使用时实测约耗费7GB左右的显存。
## 安装
1. 下载项目代码
`git clone https://github.com/reuAC/Tools_DeepSeekOCR`
2. 创建当前项目的虚拟环境
`python -m venv venv`  
激活虚拟环境
`venv\Scripts\activate.bat`
3. 将 DeepSeek-OCR 模型文件下载到项目目录内的model目录  
    3.1 使用 ModelScope：`modelscope download --model deepseek-ai/DeepSeek-OCR --local_dir ./model`
4. 安装环境
```python
# DeepSeek-OCR 所需的依赖
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.46.3 tokenizers==0.20.3 einops easydict addict

# 本项目额外的依赖
pip install mss pynput screeninfo
```
5. 安装完成后使用 `python main.py` 即可运行
## 使用要点
1. 启动主程序后自动加载模型到显卡中，加载完成后显示菜单
2. 默认截图热键为 Ctrl + Shift + X
3. 截图、配置会暂时保存在项目目录下
4. 截图识别时会有模型的流式输出，识别完成后会有模型的完整输出
