$ErrorActionPreference = "Stop"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57b_build_trades_file_acceptance_artifacts_lt1b.py"
python $script --batch-size 50000 --sample-per-stratum 20
