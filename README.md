# Tools_DeepSeekOCR
This project implements a screenshot utility based on DeepSeek-OCR, enabling the deployment of the model on the Windows platform for Optical Character Recognition (OCR) from screenshots.

[ [中文](./README_CN.md) | English ]

## Prerequisites

Before proceeding with the installation, please ensure that the following dependencies are installed:

1. Python >= 3.9
2. CUDA (Install the CUDA driver corresponding to your graphics card)

**Note:** Practical testing shows that this utility requires approximately 7 GB of VRAM during use.

## Installation

1. Clone the project repository:
   `git clone https://github.com/reuAC/Tools_DeepSeekOCR`

2. Create a virtual environment for the current project:
   `python -m venv venv`
   Activate the virtual environment:
   `venv\Scripts\activate.bat`

3. Download the DeepSeek-OCR model files into the `./model` directory within the project directory:
    3.1 Using ModelScope: `modelscope download --model deepseek-ai/DeepSeek-OCR --local_dir ./model`

4. Install the required dependencies:
```python
# Dependencies required for DeepSeek-OCR
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.46.3 tokenizers==0.20.3 einops easydict addict

# Additional dependencies for this project
pip install mss pynput screeninfo
```

5. After installation is complete, run the application using: `python main.py`

## Usage Notes

1. Upon starting the main program, the model will automatically be loaded onto the graphics card (GPU). The menu will appear once loading is complete.
2. The default screenshot hotkey is **Ctrl + Shift + X**.
3. Screenshots and configuration files will be temporarily saved in the project directory.
4. During screenshot recognition, there will be a **streamed output** from the model, followed by the **complete output** once recognition is finished.