$ErrorActionPreference = "Stop"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py"
python $script --workers 4
