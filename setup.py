from cx_Freeze import setup, Executable

setup(
    name="PAYSLIPPRO",
    version="1.0",
    description="This app for generating payslip",
    executables=[Executable("main.py", base="Win32GUI",)],
)
