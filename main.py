import os#导入os模块，用于文件操作
import psutil#导入psutil模块，用于获取进程信息
import tkinter as tk#导入tkinter模块，用于GUI
from tkinter import messagebox, ttk#导入messagebox和ttk模块，用于GUI
import ctypes#导入ctypes模块，用于调用Windows API
from ctypes import wintypes#导入wintypes模块，用于调用Windows API
def valid_usb_drive(drive):#检查输入的盘符是否为有效的U盘路径
    if not drive.endswith('\\') or len(drive) != 3 or not drive[0].isalpha():#用于验证用户行为，确保输入的盘符格式正确
        return False#返回 False
    return os.path.exists(drive)#检查输入的盘符是否存在
def is_process_in_efficiency_mode(pid):#检查指定 PID 的进程是否处于效率模式
    process_query_limited_information = 0x1000#Windows 特有的标志，用于查询进程的 CPU 亲和性
    class process_information_class:#Windows 特有的结构，用于保存进程信息
        ProcessEnergyTrackingState = 81#Windows 特有的标志，用于查询进程的能源跟踪状态
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)#加载 kernel32.dll,用于获取进程信息
    h_process = kernel32.OpenProcess(process_query_limited_information, False, pid)#打开进程句柄，使用 process_query_limited_information 权限
    if not h_process:#如果打开失败，返回 False
        return False
    try:#获取进程信息
        energy_state = wintypes.DWORD()#用于保存进程的能源跟踪状态
        result = kernel32.GetProcessInformation(
        h_process,process_information_class.ProcessEnergyTrackingState,
        ctypes.byref(energy_state),
        ctypes.sizeof(energy_state))#获取进程能源跟踪状态，包括查询的进程，类别（该进程当前的状态），指针（接收API返回的数据），大小（传入的输出缓冲区大小）
        kernel32.CloseHandle(h_process)#关闭句柄
        if result:#判断API调用是否成功
            return energy_state.value == 2#返回进程是否处于节能状态
        else:#否则返回False
            return False
    except Exception as e:#捕获异常
        print(f"检查效率模式失败: {e}")#打印错误信息
        return False
def get_usb_holding_processes(drive):#获取占用 U 盘的进程列表
    processes = []#创建一个空列表，用于保存进程信息
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):#遍历所有进程
        try:#遍历进程的打开文件列表
            files = proc.info['open_files']#获取进程的打开文件列表
            if files:#如果进程有打开文件
                for file in files:#遍历进程的打开文件列表
                    if file.path.startswith(drive):#检查文件是否属于 U 盘
                        efficiency = is_process_in_efficiency_mode(proc.pid)#检查进程是否处于效率模式
                        processes.append({#保存进程信息
                            'pid': proc.pid,#进程ID
                            'name': proc.name(),#进程名称
                            'efficiency': efficiency#进程是否处于效率模式
                        })
                        break#跳出循环
        except (psutil.NoSuchProcess, psutil.AccessDenied):#捕获异常
            continue#继续下一次循环,跳出循环
    return processes#返回进程列表
def check_usb_usage():#检查 U 盘使用情况
    usb_drive = entry.get().strip() + '\\'#获取用户输入的 U 盘盘符
    if not valid_usb_drive(usb_drive):#检查输入的 U 盘盘符是否为有效
        messagebox.showerror("无效盘符", "请输入有效的U盘盘符（例如 G:）")#如果用户输入了错误的信息,显示错误信息
        return False#返回 False
    result_text.config(state="normal")#启用结果文本框
    result_text.delete(1.0, tk.END)#清空结果文本框
    result_text.insert(tk.END, "正在检查，请稍候...\n")#显示正在检查的提示信息
    root.update()#更新界面
    processes = get_usb_holding_processes(usb_drive)#获取占用 U 盘的进程列表
    result_text.delete(1.0, tk.END)#清空结果文本框
    if not processes:#如果没有进程占用 U 盘
        result_text.insert(tk.END, "当前没有进程占用该U盘。\n")#显示没有进程占用 U 盘的提示信息
    else:#如果有进程占用 U 盘
        for p in processes:#遍历进程列表
            if p['efficiency']:#如果进程处于效率模式
                message = f"进程 {p['name']} (PID: {p['pid']}) 正在占用 U 盘，并且处于效率模式。\n"#创建提示信息
                message += "若要弹出 U 盘，可能需要先退出该进程的效率模式或结束该进程。"#添加提示信息
                messagebox.showwarning("效率模式进程", message)#显示提示信息
            else:#如果进程没有处于效率模式
                result_text.insert(tk.END, f"进程 {p['name']} (PID: {p['pid']}) 正在占用 {usb_drive}\n")#显示进程占用 U 盘的提示信息
    result_text.config(state="disabled")#禁用结果文本框
    return True#返回 True
root = tk.Tk()#创建主窗口（即GUI界面）
root.title("U盘占用检查工具")#设置窗口标题
root.geometry("500x400")#设置窗口大小
root.resizable(False, False)#禁止窗口大小改变
style = ttk.Style()#创建样式
style.configure("TButton", padding=6, relief="flat", background="#4CAF50")#设置按钮样式，包括填充、边框和背景颜色
style.configure("TLabel", font=("微软雅黑", 10))#设置标签样式，包括字体和字体大小
label = tk.Label(root, text="请输入 U 盘盘符（例如 G:）:", font=("微软雅黑", 10))#创建标签，包括标题和字体
label.pack(pady=10)#设置标签位置
entry = tk.Entry(root, font=("微软雅黑", 10), width=15)#创建输入框，包括字体和宽度
entry.pack(pady=5)#设置输入框位置
check_button = ttk.Button(root, text="检查", command=check_usb_usage)#创建按钮，包括标题和点击事件
check_button.pack(pady=10)#设置按钮位置
result_text = tk.Text(root, height=12, width=60, state="disabled", font=("微软雅黑", 10))#创建结果文本框，包括高度、宽度、状态（
result_text.pack(pady=10)#设置结果文本框位置
root.mainloop()#启动主循环，进入GUI界面
