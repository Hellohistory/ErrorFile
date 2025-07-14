# ErrorFile/Detection/ExcelInspector.py

import xlrd
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from xlrd.biffh import XLRDError

def check_excel_file(file_path):
    """检查.xlsx是否损坏"""
    try:
        load_workbook(filename=file_path)
        return True, "Excel文件(.xlsx)检查通过，文件未损坏。"
    except InvalidFileException:
        return False, "Excel文件(.xlsx)损坏或格式不正确。"
    except Exception as e:
        return False, f"检测Excel文件(.xlsx)时发生错误: {str(e)}"


def check_xls_file(file_path):
    """检查.xls是否损坏"""
    try:
        xlrd.open_workbook(file_path)
        return True, "Excel文件(.xls)检查通过，文件未损坏。"
    except XLRDError:
        return False, "Excel文件(.xls)损坏或格式不正确。"
    except Exception as e:
        return False, f"检测Excel文件(.xls)时发生错误: {str(e)}"