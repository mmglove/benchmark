#   Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common_import import *
from activation import PaddleActivation, TorchActivation


@benchmark_registry.register("relu", reuse="activation")
class ReluConfig(APIConfig):
    def __init__(self):
        super(ReluConfig, self).__init__('relu')
        self.api_name = 'relu'
        self.api_list = {
            'elu': 'elu',
            'leaky_relu': 'leaky_relu',
            'relu': 'relu',
            'relu6': 'relu6',
            'selu': 'selu',
        }
        # relu belongs to activation op series which only has one variable
        # thus relu can reuse activation parameters 
        self.alias_name = "activation"

    def disabled(self):
        if self.api_name in ["selu"] and self.x_dtype == "float16":
            print(
                "-- Warning:\n"
                "  1. This config is disabled because float16 is not supported for %s.\n"
                % (self.api_name))
            return True
        return super(ReluConfig, self).disabled()


@benchmark_registry.register("relu")
class TFRelu(TensorflowOpBenchmarkBase):
    def build_graph(self, config):
        x = self.variable(name='x', shape=config.x_shape, dtype=config.x_dtype)
        out = self.layers(config.api_name, features=x)

        self.feed_list = [x]
        self.fetch_list = [out]
        if config.backward:
            self.append_gradients(out, [x])
