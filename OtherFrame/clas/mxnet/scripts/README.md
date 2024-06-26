# benchmark使用说明

此目录所有shell脚本是为了测试gluon-cv中MobileNetV1模型的速度指标，如单卡训练速度指标、多卡训练速度指标等。

## 相关脚本说明

一共有4个脚本：

- `PrepareEnv.sh`: 配置环境
- `PrepareData.sh`: 下载相应的测试数据，配置好数据路径
- `run_benchmark.sh`: 执行所有训练测试的入口脚本
- `analysis_log.py`: 解析日志，计算ips, 生成json文件

## 使用说明

**注意**：执行目录为glon-cv的根目录。将上面4个脚本复制到gluon-cv根目录下

### 1.准备环境及数据

```shell
bash PrepareEnv.sh
bash PrepareData.sh
```

### 2.执行所有模型的测试

```shell
# 单卡
 CUDA_VISIBLE_DEVICES=0 bash run_benchmark.sh sp ${batch_size} fp32 500 mobilenet1.0
# 多卡
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash run_benchmark.sh mp ${batch_size} fp32 500 mobilenet1.0
bash run.sh
```

## ips计算方法

日志文件的每条日志输出中含有每个batch的`Speed`信息。计算`ips`时，去掉前1个输出，剩下的所有`Speed`求平均，得到`ips`. 
