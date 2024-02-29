# ErrorFile/Detection/ExcelInspector.py

import xlrd
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from xlrd.biffh import XLRDError


def check_excel_file(file_path):
    """检查.xlsx是否损坏"""
    try:
        # 打开Excel文件
        wb = load_workbook(filename=file_path)
        # 如果没有抛出异常，则认为文件没有损坏
        return True, "Excel文件检查通过，文件未损坏。"
    except InvalidFileException as e:
        # 如果文件格式不正确或文件损坏，将抛出InvalidFileException异常
        return False, f"Excel文件损坏或格式不正确: {str(e)}"
    except Exception as e:
        # 处理其他可能的异常
        return False, f"检测Excel文件时发生错误: {str(e)}"


def check_xls_file(file_path):
    """检查.xls是否损坏"""
    try:
        # 打开.xls文件
        wb = xlrd.open_workbook(file_path)
        # 如果没有抛出异常，则认为文件没有损坏
        return True, "Excel文件(.xls)检查通过，文件未损坏。"
    except XLRDError as e:
        # 如果文件格式不正确或文件损坏，将抛出XLRDError异常
        return False, f"Excel文件(.xls)损坏或格式不正确: {str(e)}"
    except Exception as e:
        # 处理其他可能的异常
        return False, f"检测Excel文件(.xls)时发生错误: {str(e)}"
