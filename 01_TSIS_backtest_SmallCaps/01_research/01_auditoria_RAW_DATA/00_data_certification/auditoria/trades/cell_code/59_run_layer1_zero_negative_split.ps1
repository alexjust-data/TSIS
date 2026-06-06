$ErrorActionPreference = "Stop"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\59_layer1_zero_negative_split.py"
python $script --example-idx 0 --head-rows 15 --hist-bins 30
