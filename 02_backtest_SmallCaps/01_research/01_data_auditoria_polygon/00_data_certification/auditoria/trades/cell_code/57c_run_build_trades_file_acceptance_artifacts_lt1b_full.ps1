$ErrorActionPreference = "Stop"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\57c_build_trades_file_acceptance_artifacts_lt1b_full.py"
python $script --batch-size 50000 --index-shard-size 100000 --metrics-shard-size 5000 --sample-per-stratum 20
