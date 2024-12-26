import os
import shutil

def add_polybench_files(root_dir, utilities_dir):
    # 定义要复制的文件
    support_h = os.path.join(utilities_dir, 'support.h')
    support_c = os.path.join(utilities_dir, 'support.c')
    
    # 遍历根目录下的所有文件夹
    for subdir, dirs, files in os.walk(root_dir):
        # 获取kernel文件夹的名称
        kernel_name = os.path.basename(subdir)
        
        # 检查是否存在{kernel}.c文件
        if not f'support.c' in files:
            # 复制support.h和support.c到目标目录
            shutil.copy(support_h, subdir)
            shutil.copy(support_c, subdir)
            print(f"Copied support.h and support.c to {subdir}")

def main():
    # 定义要遍历的根目录和utilities目录
    root_dir = '../MachSuite'
    utilities_dir = '../MachSuite/common'
    
    add_polybench_files(root_dir, utilities_dir)

if __name__ == "__main__":
    main()