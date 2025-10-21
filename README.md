# Tools_DeepSeekOCR
This project implements a screenshot utility based on **DeepSeek-OCR**, enabling model deployment on the Windows platform for Optical Character Recognition (OCR) directly from screen captures.

[ [中文](./README_CN.md) | English ]

## System Prerequisites
Before proceeding with the installation, please ensure the following dependencies are installed:
1. Python >= 3.9
    1.1 Python Website: [https://www.python.org/downloads/release/python-3140/](https://www.python.org/downloads/release/python-3140)  
    Scroll to the bottom of the page to find the table labeled "Files," which contains installation files for various versions. For Windows 64-bit, use the **`Windows installer (64-bit)`**.
2. CUDA (Install the CUDA driver corresponding to your graphics card)  
    2.1 CUDA Website: [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)  
    Download and install the **CUDA Toolkit Installer** based on your device's operating system version.
3. (Optional) Git  
    3.1 Git Website: [https://git-scm.com/](https://git-scm.com/)

**Note:** Empirical testing indicates that approximately **7GB of VRAM (Video RAM)** is consumed during use.

## Installation
1. Download the project code:
`git clone https://github.com/reuAC/Tools_DeepSeekOCR`  
Navigate to the project directory: `cd Tools_DeepSeekOCR`
2. Create a virtual environment for the project:
`python -m venv venv`  
Activate the virtual environment:
`venv\Scripts\activate.bat`
3. Download the DeepSeek-OCR model files into the **`model`** directory within the project folder.  
    3.1 Using ModelScope: `modelscope download --model deepseek-ai/DeepSeek-OCR --local_dir ./model`
4. Install the environment dependencies:
```python
# Dependencies required by DeepSeek-OCR
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.46.3 tokenizers==0.20.3 einops easydict addict

# Additional dependencies for this project
pip install mss pynput screeninfo
```
5. After installation is complete, run the application using: `python main.py`

## Key Usage Points
1. Upon launching the main program, the model will automatically be loaded onto the GPU. The menu will be displayed once loading is complete.
2. The default screenshot hotkey is **Ctrl + Shift + X**.
3. Screenshots and configuration settings will be temporarily saved in the project directory.
4. During screenshot recognition, the model's output will be displayed as a **stream**. The model's complete, final output will be shown once recognition is finished.