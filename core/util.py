import ctypes


def ensure_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        raise Exception("需要管理员权限运行此脚本。")
