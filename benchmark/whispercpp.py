#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
import datetime
from evaluate import load
import sys
import json

def inference(input_file, model):

    print(f"model: {model}")
    start_time = datetime.datetime.now()
    reference_file = os.path.splitext(input_file)[0] + ".txt"
    
    output_wav = os.path.splitext(input_file)[0] + "-" + model + ".wav"
    prediction_file = output_wav + ".txt"
    
    cmd = f"ffmpeg -i {input_file} -ar 16000 -ac 1 -c:a pcm_s16le {output_wav} -y 2> /dev/null > /dev/null"
    print(cmd)
    os.system(cmd)
    
    cmd = f"../whisper.cpp/main --threads 8  -m ../whisper.cpp/sc-models/ggml-{model}.bin -f {output_wav} -l ca -otxt"
    print(cmd)    
    os.system(cmd)

    _time = datetime.datetime.now() - start_time
    
    with open(reference_file) as f:
        reference = f.read()

    with open(prediction_file) as f:
        prediction = f.read()
    
    _wer = load("wer")
    wer_score = _wer.compute(predictions=[prediction], references=[reference])
    wer_score = wer_score * 100
    return f"{wer_score:.2f}", str(_time)
    
def single_model(model):
    wer_score, time = inference("samples/15GdH9-curt.mp3", model)
    print(f"time: {time}, wer: {wer_score}, model: {model}")
                 
def main():
    print("Benchmark whisper.cpp inference")

    if len(sys.argv) > 1:
        return single_model(sys.argv[1])

    models = ["small", "sc-small", "medium", "sc-medium"]
    results = []
    for model in models:
        wer, _time = inference("samples/15GdH9-curt.mp3", model)
        result = {"wer" : wer, "time" : _time, "model": model}
        results.append(result)

    json_data = json.dumps(results, indent=4)
    with open("results.json", "w") as outfile:
        outfile.write(json_data)

    print(results)

if __name__ == "__main__":
    main()
