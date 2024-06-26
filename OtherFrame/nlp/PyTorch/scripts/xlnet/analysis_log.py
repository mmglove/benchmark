#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf-8 vi:ts=4:sw=4:expandtab:ft=python

import re
import sys
import json


def analyze(model_name, log_file, res_log_file):
    time_pat = re.compile(r"train_samples_per_second': (.*)")
    logs = open(log_file).readlines()
    logs = ";".join(logs)
    time_res = time_pat.findall(logs)

    fail_flag = 0
    run_mode = ""
    gpu_num = 0
    ips = 0

    if time_res == []:
        fail_flag = 1
    else:
        gpu_num = log_file.split('_')[-1]
        run_mode = "sp" if gpu_num == 1 else "mp"
        ips = time_res[-1]

    info = {"log_file": log_file, "model_name": model_name, "mission_name": "语义表示",
            "direction_id": 1, "run_mode": run_mode, "index": 1, "gpu_num": gpu_num,
            "FINAL_RESULT": ips, "JOB_FAIL_FLAG": fail_flag, "UNIT": "sequences/s"}
    json_info = json.dumps(info)
    with open(res_log_file, "w") as of:
        of.write(json_info)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:" + sys.argv[0] + " model_name path/to/log/file path/to/res/log/file")
        sys.exit()

    model_name = sys.argv[1]
    log_file = sys.argv[2]
    res_log_file = sys.argv[3]

    analyze(model_name, log_file, res_log_file)
