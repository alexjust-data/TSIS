$ErrorActionPreference = "Stop"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57d_resume_parallel_trades_file_acceptance_lt1b_full.py"
python $script --workers 4
