# Tools_DeepSeekOCR

This project implements a screenshot utility based on DeepSeek-OCR, designed to deploy the model on the Windows platform for Optical Character Recognition (OCR) directly from screenshots.

[ [中文](./README_CN.md) | English ]

## System Prerequisites

Before proceeding with the installation, ensure that the following dependencies are installed:

1. Python >= 3.9  
    1.1 Python Website: [https://www.python.org/downloads/release/python-3140](https://www.python.org/downloads/release/python-3140)  
    Scroll to the bottom of the page to find the "Files" table, which contains installation files for various versions. For a 64-bit Windows system, use `Windows installer (64-bit)`.
2. CUDA (The CUDA driver corresponding to your graphics card)  
    2.1 CUDA Website: [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)  
    Download and install the CUDA Toolkit Installer that matches your device's operating system version.

**Note:** Empirical testing shows that this application requires approximately 7GB of GPU VRAM during use.

## Installation

1. Clone the project repository:
`git clone https://github.com/reuAC/Tools_DeepSeekOCR`
2. Create a virtual environment for the current project:
`python -m venv venv`  
Activate the virtual environment:
`venv\Scripts\activate.bat`
3. Download the DeepSeek-OCR model files into the `./model` directory within the project:  
    3.1 Using ModelScope: `modelscope download --model deepseek-ai/DeepSeek-OCR --local_dir ./model`
4. Install the environment dependencies:
```python
# Dependencies required for DeepSeek-OCR
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.46.3 tokenizers==0.20.3 einops easydict addict

# Additional dependencies for this project
pip install mss pynput screeninfo
```
5. After installation is complete, run the application using: `python main.py`

## Usage Highlights

1. Upon launching the main program, the model is automatically loaded onto the GPU. The menu will appear once loading is complete.
2. The default hotkey for taking a screenshot is **Ctrl + Shift + X**.
3. Screenshots and configuration settings are temporarily saved within the project directory.
4. During screenshot OCR recognition, there will be a streaming output from the model, followed by the complete, final output once recognition is finished.