import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import mss
import torch
from transformers import AutoModel, AutoTokenizer
from pynput import keyboard
import io
import subprocess
import configparser
import screeninfo
import threading
import logging
import warnings

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings("ignore", category=UserWarning)

LOCAL_MODEL_PATH = './model' if getattr(sys, 'frozen', False) else 'model'
TEMP_OUTPUT_DIR = "temp_output"
DEFAULT_HOTKEY = '<ctrl>+<shift>+x'
TEMP_SCREENSHOT_PATH = "temp_screenshot.png"
CONFIG_FILE = "config.ini"

PROMPT_OPTIONS = {
    "文档（Markdown格式）": "<image>\n<|grounding|>Convert the document to markdown. ",
    "通用图片（保留布局）": "<image>\n<|grounding|>OCR this image. ",
    "通用图片（无布局）": "<image>\nFree OCR. ",
    "文档中的图表": "<image>\nParse the figure. ",
    "通用描述": "<image>\nDescribe this image in detail. "
}
DEFAULT_PROMPT_KEY = "文档（Markdown格式）"

model = None
tokenizer = None
root = None
canvas = None
start_x, start_y, rect = None, None, None
main_app_window = None
hotkey_listener = None
shutdown_event = threading.Event()

active_hotkey = DEFAULT_HOTKEY
selected_prompt = PROMPT_OPTIONS[DEFAULT_PROMPT_KEY]

screen_x_offset, screen_y_offset = 0, 0

class StreamTee:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

    def write(self, data):
        self.stream1.write(data)
        self.stream2.write(data)

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()

def load_hotkey_from_config():
    if os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config.get('Settings', 'Hotkey', fallback=DEFAULT_HOTKEY)
    return DEFAULT_HOTKEY

def save_hotkey_to_config(hotkey):
    config = configparser.ConfigParser()
    config['Settings'] = {'Hotkey': hotkey}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"\n[信息] 热键已保存到 {CONFIG_FILE}: {hotkey}")

def check_and_download_model():
    while not (os.path.isdir(LOCAL_MODEL_PATH) and os.listdir(LOCAL_MODEL_PATH)):
        print(f"\n未在 '{LOCAL_MODEL_PATH}' 目录中检测到模型文件。")
        print("请选择一个操作：")
        print("1. 使用 ModelScope 自动下载 (推荐, 需要 'pip install modelscope')")
        print("2. 从 Hugging Face 手动下载")
        print("3. 退出程序")

        choice = input("请输入选项 (1/2/3): ").strip()

        if choice == '1':
            print("正在尝试使用 ModelScope 下载模型...")
            try:
                subprocess.run(["modelscope", "--version"], check=True, capture_output=True, text=True)
                download_command = f"modelscope download --model deepseek-ai/DeepSeek-OCR --local_dir {LOCAL_MODEL_PATH}"
                subprocess.run(download_command, shell=True, check=True)
                print("模型下载完成。")
                if os.path.isdir(LOCAL_MODEL_PATH) and os.listdir(LOCAL_MODEL_PATH):
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print("\nModelScope 命令执行失败。")
                print("请确保您已通过 'pip install modelscope' 安装了 ModelScope 库，并已正确配置环境。")
                print(f"错误详情: {e}")
                input("按 Enter 键退出。")
                sys.exit(1)
            except Exception as e:
                print(f"\n下载过程中发生未知错误: {e}")
                input("按 Enter 键退出。")
                sys.exit(1)
        elif choice == '2':
            print("\n请手动从以下地址下载模型：")
            print("https://huggingface.co/deepseek-ai/DeepSeek-OCR")
            print(f"请将所有文件下载并放置在程序根目录下的 '{LOCAL_MODEL_PATH}' 文件夹中。")
            print("完成后，请重新启动此程序。")
            input("按 Enter 键退出。")
            sys.exit(0)
        elif choice == '3':
            print("程序已退出。")
            sys.exit(0)
        else:
            print("无效输入，请输入 1, 2, 或 3。")
    return True

def load_model():
    global model, tokenizer
    print("正在加载 DeepSeek-OCR 模型，请稍候...")
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA 不可用。此工具需要 NVIDIA GPU。")

        tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH, trust_remote_code=True)
        model = AutoModel.from_pretrained(LOCAL_MODEL_PATH, trust_remote_code=True, use_safetensors=True)
        model = model.eval().cuda().to(torch.bfloat16)
        print("模型已在 GPU 上成功加载。")
        return True
    except Exception as e:
        print(f"加载模型时出错：{e}")
        messagebox.showerror("模型加载错误", f"加载模型失败：{e}\n\n请确保您拥有兼容的 NVIDIA GPU 并已安装 CUDA。")
        return False

def perform_ocr(image_path):
    global selected_prompt
    if not model or not tokenizer:
        print("模型未加载。")
        return "错误：模型未加载。"

    print(f"正在对 {image_path} 执行 OCR...")
    
    original_stdout = sys.stdout
    ocr_output_buffer = io.StringIO()
    
    sys.stdout = StreamTee(original_stdout, ocr_output_buffer)
    
    try:
        prompt = selected_prompt
        model.infer(
            tokenizer,
            prompt=prompt,
            image_file=image_path,
            output_path=TEMP_OUTPUT_DIR,
            base_size=1024,
            image_size=640,
            crop_mode=True,
            save_results=False,
            test_compress=False
        )
        captured_text = ocr_output_buffer.getvalue()
        return captured_text
    except Exception as e:
        sys.stdout = original_stdout
        print(f"OCR 期间出错：{e}")
        return f"OCR 期间发生错误：{e}"
    finally:
        sys.stdout = original_stdout

def on_mouse_press(event):
    global start_x, start_y, rect
    start_x = canvas.canvasx(event.x)
    start_y = canvas.canvasy(event.y)
    rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

def on_mouse_drag(event):
    cur_x, cur_y = (canvas.canvasx(event.x), canvas.canvasy(event.y))
    canvas.coords(rect, start_x, start_y, cur_x, cur_y)

def on_mouse_release(event):
    global root, screen_x_offset, screen_y_offset
    end_x, end_y = (canvas.canvasx(event.x), canvas.canvasy(event.y))

    if root:
        root.destroy()
        root = None

    abs_start_x = start_x + screen_x_offset
    abs_start_y = start_y + screen_y_offset
    abs_end_x = end_x + screen_x_offset
    abs_end_y = end_y + screen_y_offset

    x1, y1 = min(abs_start_x, abs_end_x), min(abs_start_y, abs_end_y)
    x2, y2 = max(abs_start_x, abs_end_x), max(abs_start_y, abs_end_y)

    if x2 - x1 < 1 or y2 - y1 < 1:
        print("截图区域太小，已取消。")
        return

    def ocr_task():
        with mss.mss() as sct:
            monitor = {"top": int(y1), "left": int(x1), "width": int(x2 - x1), "height": int(y2 - y1)}
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.save(TEMP_SCREENSHOT_PATH)

        print("\n" + "=" * 40)
        print("模型流式输出开始...")
        
        final_ocr_result = perform_ocr(TEMP_SCREENSHOT_PATH)
        
        print("模型流式输出结束。")
        print("=" * 40)
        
        print("\n" + "=" * 40)
        print("模型完整输出")
        sys.stdout.write(final_ocr_result)
        sys.stdout.flush()
        print("\n模型完整输出结束")
        print("=" * 40)
        
        print("\nOCR 完成。按 Enter 键可刷新菜单。")

        if os.path.exists(TEMP_SCREENSHOT_PATH):
            os.remove(TEMP_SCREENSHOT_PATH)

    threading.Thread(target=ocr_task, daemon=True).start()

def start_screenshot():
    global root, canvas, screen_x_offset, screen_y_offset
    if root is not None and root.winfo_exists():
        return

    try:
        monitors = screeninfo.get_monitors()
        if not monitors:
            raise Exception("无法检测到显示器。")

        min_x = min(m.x for m in monitors)
        min_y = min(m.y for m in monitors)
        max_x = max(m.x + m.width for m in monitors)
        max_y = max(m.y + m.height for m in monitors)
        
        width = max_x - min_x
        height = max_y - min_y
        
        screen_x_offset = min_x
        screen_y_offset = min_y

        root = tk.Toplevel(main_app_window)
        root.overrideredirect(True)
        root.geometry(f"{width}x{height}+{min_x}+{min_y}")
        root.attributes("-alpha", 0.3)
        root.attributes('-topmost', True)

        canvas = tk.Canvas(root, cursor="cross", bg="black")
        canvas.pack(fill="both", expand=True)

        canvas.bind("<ButtonPress-1>", on_mouse_press)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_release)
        
        root.bind("<Escape>", lambda e: root.destroy())
        
        root.focus_force()

    except Exception as e:
        print(f"创建截图窗口时出错: {e}")
        messagebox.showerror("错误", f"无法启动截图功能: {e}")
        if root:
            root.destroy()
            root = None

def on_hotkey_press():
    print("\n热键已激活！正在开始截图... (按 ESC 取消)")
    if main_app_window:
        main_app_window.after(100, start_screenshot)

def restart_hotkey_listener(new_hotkey):
    global hotkey_listener, active_hotkey
    
    if hotkey_listener:
        hotkey_listener.stop()
        
    try:
        hotkey_listener = keyboard.GlobalHotKeys({new_hotkey: on_hotkey_press})
        hotkey_listener.start()
        active_hotkey = new_hotkey
        print(f"\n[信息] 热键已成功更新为: {active_hotkey}")
        save_hotkey_to_config(active_hotkey)
    except Exception as e:
        print(f"\n[错误] 无法设置热键 '{new_hotkey}'。可能是格式错误或已被其他程序占用。")
        print(f"错误详情: {e}")
        hotkey_listener = keyboard.GlobalHotKeys({active_hotkey: on_hotkey_press})
        hotkey_listener.start()
        print(f"[信息] 已恢复为之前的热键: {active_hotkey}")

def console_interaction_loop():
    global selected_prompt, active_hotkey

    while not shutdown_event.is_set():
        try:
            current_prompt_desc = next((key for key, value in PROMPT_OPTIONS.items() if value == selected_prompt), "未知")

            print("\n" + "=" * 50)
            print(" " * 10 + "DeepSeek-OCR 工具正在后台运行")
            print(f" ▸ 当前截图热键: {active_hotkey}")
            print(f" ▸ 当前识别模式: {current_prompt_desc}")
            print("-" * 50)
            print("请选择操作：")
            print("  1. 更改热键")
            print("  2. 更改识别模式 (提示词)")
            print("  3. 退出程序")
            print("=" * 50)
            
            choice = input("请输入选项 (1/2/3): ").strip()

            if choice == '1':
                print("\n请输入新的热键组合。格式示例: <ctrl>+<shift>+x 或 <alt>+q")
                new_hotkey = input("新热键: ").strip().lower()
                if '+' in new_hotkey and '<' in new_hotkey and '>' in new_hotkey:
                    main_app_window.after(0, restart_hotkey_listener, new_hotkey)
                else:
                    print("热键格式无效，请重新输入。")
            elif choice == '2':
                print("\n请选择一种识别模式：")
                options_list = list(PROMPT_OPTIONS.keys())
                for i, desc in enumerate(options_list):
                    print(f"  {i + 1}. {desc}")

                try:
                    prompt_choice_str = input(f"请输入模式编号 (1-{len(options_list)}): ").strip()
                    if not prompt_choice_str:
                        print("未作更改。")
                        continue
                    prompt_choice = int(prompt_choice_str) - 1
                    if 0 <= prompt_choice < len(options_list):
                        chosen_key = options_list[prompt_choice]
                        selected_prompt = PROMPT_OPTIONS[chosen_key]
                        print(f"\n[信息] 模式已设置为: {chosen_key}")
                    else:
                        print("无效编号，请重新输入。")
                except ValueError:
                    print("输入无效，请输入数字。")
            elif choice == '3':
                print("正在退出程序...")
                shutdown_event.set()
                main_app_window.after(100, main_app_window.quit)
                break
            else:
                print("无效输入，请输入 1, 2, 或 3。")

        except (KeyboardInterrupt, EOFError):
            print("\n检测到 Ctrl+C 或输入流结束，正在退出程序...")
            shutdown_event.set()
            main_app_window.after(100, main_app_window.quit)
            break
        except Exception as e:
            print(f"\n发生意外错误: {e}")

def main():
    global main_app_window, hotkey_listener, active_hotkey, selected_prompt
    
    if not check_and_download_model():
        return
    os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)
    active_hotkey = load_hotkey_from_config()

    main_app_window = tk.Tk()
    main_app_window.withdraw()

    if not load_model():
        main_app_window.destroy()
        return

    try:
        hotkey_listener = keyboard.GlobalHotKeys({active_hotkey: on_hotkey_press})
        hotkey_listener.start()
    except Exception as e:
        messagebox.showerror("热键错误", f"无法设置热键 '{active_hotkey}'。\n可能是格式错误或已被其他程序占用。\n\n错误详情: {e}")
        main_app_window.destroy()
        return

    console_thread = threading.Thread(target=console_interaction_loop, daemon=True)
    console_thread.start()

    try:
        main_app_window.mainloop()
    finally:
        print("正在进行最后的清理工作...")
        shutdown_event.set()
        if hotkey_listener and hotkey_listener.is_alive():
            hotkey_listener.stop()
        print("程序已完全退出。")

if __name__ == "__main__":
    main()