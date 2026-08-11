param(
    [string]$OutputDirectory = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\native\trading_activity\build"
)
$ErrorActionPreference = "Stop"
$source = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\native\trading_activity\tsis_baseline_native_cpp.cpp"
$vsdev = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$pythonInclude = python -c "import sysconfig; print(sysconfig.get_paths()['include'])"
$pythonLib = python -c "import sysconfig; print(sysconfig.get_config_var('installed_base') + r'\libs')"
$pybindInclude = python -c "import pybind11; print(pybind11.get_include())"
$suffix = python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
$pythonLibrary = python -c "import sys; print(f'python{sys.version_info.major}{sys.version_info.minor}.lib')"
$output = Join-Path $OutputDirectory ("tsis_baseline_native_cpp" + $suffix)
$object = Join-Path $OutputDirectory "tsis_baseline_native_cpp.obj"
$importLibrary = Join-Path $OutputDirectory "tsis_baseline_native_cpp.lib"
$programDatabase = Join-Path $OutputDirectory "tsis_baseline_native_cpp.pdb"
$command = 'call "{0}" -arch=x64 && cl /nologo /O2 /GL /std:c++17 /EHsc /openmp /LD "{1}" /I"{2}" /I"{3}" /Fo:"{4}" /link /LTCG /LIBPATH:"{5}" {6} /OUT:"{7}" /IMPLIB:"{8}" /PDB:"{9}"' -f $vsdev,$source,$pythonInclude,$pybindInclude,$object,$pythonLib,$pythonLibrary,$output,$importLibrary,$programDatabase
cmd.exe /d /s /c $command
if ($LASTEXITCODE -ne 0) { throw "Native build failed: $LASTEXITCODE" }
Write-Output $output
