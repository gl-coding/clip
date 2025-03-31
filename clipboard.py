import pyperclip

def get_clipboard_content():
    try:
        # 获取剪贴板内容
        content = pyperclip.paste()
        print("剪贴板内容：")
        print("-" * 30)
        print(content)
        print("-" * 30)
        return content
    except Exception as e:
        print(f"获取剪贴板内容时出错：{str(e)}")
        return None

if __name__ == "__main__":
    get_clipboard_content() 