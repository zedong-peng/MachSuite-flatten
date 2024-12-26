import os
import csv
import xml.etree.ElementTree as ET

def gather_csynth_data(root_dir, output_csv):
    # 打开 CSV 文件以写入模式
    with open(output_csv, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # 写入 CSV 文件的表头
        csv_writer.writerow(['File Path', 'Part', 'TargetClockPeriod', 'Best-caseLatency', 'BRAM_18K', 'LUT', 'DSP', 'FF'])

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file == 'csynth.xml':
                    file_path = os.path.join(root, file)
                    rpt_file_path = os.path.join(root, 'csynth.rpt')
                     
                    # 检查是否存在 csynth.rpt 文件
                    if not os.path.exists(rpt_file_path):
                        print(f"[INFO] 缺少 csynth.rpt 文件，跳过: {file_path}")
                        continue
            
                    try:
                        # 解析 XML 文件
                        tree = ET.parse(file_path)
                        root = tree.getroot()

                        # 提取所需信息
                        part = root.find('.//UserAssignments/Part').text
                        target_clock_period = root.find('.//UserAssignments/TargetClockPeriod').text
                        best_case_latency = root.find('.//PerformanceEstimates/SummaryOfOverallLatency/Best-caseLatency').text
                        bram_18k = root.find('.//AreaEstimates/Resources/BRAM_18K').text
                        lut = root.find('.//AreaEstimates/Resources/LUT').text
                        dsp = root.find('.//AreaEstimates/Resources/DSP').text
                        ff = root.find('.//AreaEstimates/Resources/FF').text

                        # 写入 CSV 文件
                        csv_writer.writerow([file_path, part, target_clock_period, best_case_latency, bram_18k, lut, dsp, ff])
                        print(f"[INFO] 写入 CSV 文件: {file_path}")
                    except ET.ParseError as e:
                        print(f"XML 解析错误: {file_path}, 错误信息: {str(e)}")
                    except AttributeError as e:
                        print(f"缺少必要的 XML 元素: {file_path}, 错误信息: {str(e)}")

if __name__ == "__main__":
    gather_csynth_data('../MachSuite/', 'machsuite.csv')
