# whousemydisk
这是一款用来检测U盘被哪些进程占用的程序，通过对WindowsAPI调用实现。
主要原理：接收用户需要查询的盘符，加载kernel32.dll,用于获取进程信息，打开进程句柄，使用 process_query_limited_information 权限。
获取进程能源跟踪状态，包括查询的进程，类别（该进程当前的状态），指针（接收API返回的数据），大小（传入的输出缓冲区大小）。
同时创建空列表，检测进程打开的文件并保存，检测文件是否来源于U盘，如果是则提示。
GUI是通过python的模块实现，没有采用其他方式。
同时新增对进程效率模式的检测（仅限Windows11）。

此程序目前仍然存在一些问题，包括性能（点击检测控件后Windows提示程序无响应）类，
一些尚未解决的bug（Windows也可能通过explorer.exe挂载U盘，但似乎本程序不会提示）。

未来的更新方向：解决挂载问题，优化性能，增加对进程是否读写U盘文件的检测，
增加对进程的安全性检测（是否可以通过结束进程来解决占用问题，这可能需要耗费很长时间）。

如果出现问题，请在issue中讨论，请务必注意你的语气。(暂时不开放邮箱反馈），
讨论的语言支持中文和英语，日语和俄语正在适配阶段。

正在运行的程序无响应不太可能，但是无响应的程序正在运行有点可能。
