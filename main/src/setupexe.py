from distutils.core import setup
import py2exe

setup(
    name='IoTDeviceCtrlInstaller',
    version='',
    packages=[''],
    url='',
    license='',
    author='IBM-cuiwc',
    author_email='756661204@qq.com',
    description='',
    windows=[
        {"script": "manager.py", "icon_resources": [(1, "icon/manager.ico")]}],
    options={"py2exe": {"dll_excludes": ["MSVCP90.dll"]}},
)
