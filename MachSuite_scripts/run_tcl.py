import os
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm

LOG_FILE = 'logs/design_0.log'
LOG_LOCK = threading.Lock()

def find_run_hls_tcl_files(root_dir):
    run_hls_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == 'hls.tcl':
                run_hls_files.append(os.path.join(root, file))
    return run_hls_files

def find_file_recursively(filename, base_dir='.'):
    for root, dirs, files in os.walk(base_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def should_execute(csynth_xml_path):
    try:
        # 解析 XML 文件
        tree = ET.parse(csynth_xml_path)
        root = tree.getroot()

        # 提取 Best-caseLatency
        best_case_latency = root.find('.//PerformanceEstimates/SummaryOfOverallLatency/Best-caseLatency').text

        # 检查 Best-caseLatency 是否为 'undef'
        if best_case_latency == 'undef':
            return True
        else:
            print(f"跳过执行，因为 Best-caseLatency 已定义为: {best_case_latency}")
            return False
    except ET.ParseError as e:
        print(f"XML 解析错误: {csynth_xml_path}, 错误信息: {str(e)}")
        return False
    except AttributeError as e:
        print(f"缺少必要的 XML 元素: {csynth_xml_path}, 错误信息: {str(e)}")
        return False


def execute_vitis_hls(tcl_file):
    dir_path = os.path.dirname(os.path.abspath(tcl_file))
    try:
        result = subprocess.run(['vitis_hls', '-f', 'hls.tcl'],
                                cwd=dir_path,  # 切换到 hls.tcl 所在目录
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True,
                                timeout=1800)  # 设置超时时间为30分钟（1200秒）
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except subprocess.TimeoutExpired:
        return False, "执行超时：vitis_hls 命令超过30分钟未完成。"

def process_tcl_file(tcl_file):
    dir_path = os.path.dirname(os.path.abspath(tcl_file))
    
    csynth_rpt_path = find_file_recursively('csynth.rpt', base_dir=dir_path)
    if csynth_rpt_path:
        rpt_dir = os.path.dirname(csynth_rpt_path)
        csynth_xml_path = os.path.join(rpt_dir, 'csynth.xml')
        
        if not csynth_xml_path:
            print(f"跳过执行，因为找不到 csynth.xml 文件在目录: {dir_path}")
            return

        if not should_execute(csynth_xml_path):
            return

    print(f"正在执行 vitis_hls -f run_hls.tcl 在目录: {dir_path}")
    
    success, output = execute_vitis_hls(tcl_file)
    
    if not success:
        log_message = f"执行失败: {tcl_file}\n错误信息: {output}\n"
        write_log(log_message)
        return

    write_log(f"vitis_hls 执行成功: {tcl_file}\n")
    

def write_log(message):
    with LOG_LOCK:
        with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
            log_file.write(message)

def main():
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    run_hls_files = find_run_hls_tcl_files('../MachSuite')
    total_files = len(run_hls_files) 
    print(f"找到 {total_files} 个 hls.tcl 文件。")

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_tcl_file, tcl_file) for tcl_file in run_hls_files]
        
        for future in tqdm(as_completed(futures), total=total_files, desc="处理 run_hls.tcl 文件"):
            try:
                future.result()
            except Exception as e:
                write_log(f"处理文件时发生异常: {str(e)}\n")
    
    print("所有任务已完成。")

if __name__ == '__main__':
    main()