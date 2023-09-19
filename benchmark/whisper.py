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


def inference(input_file, model, inference_dir):
    print(f"model: {model}")
    input_file = os.path.abspath(input_file)
    start_time = datetime.datetime.now()
    reference_file = os.path.splitext(input_file)[0] + ".txt"

    _file = os.path.basename(input_file)
    _file = os.path.splitext(_file)[0]
    prediction_file = os.path.join(inference_dir, _file + ".txt")
    print(f"inference_dir: {inference_dir}")
    print(f"prediction_file: {prediction_file}")

    cmd = f"whisper-ctranslate2 --temperature_increment_on_fallback None --threads 10 --output_dir {inference_dir} --model {model} {input_file}"
    print(cmd)
    os.system(cmd)

    _time = datetime.datetime.now() - start_time

    with open(reference_file) as f:
        reference = f.read()

    with open(prediction_file) as f:
        prediction = f.read()

    # This is a very naive way to calculate WER, there is normalisation like
    # it's done in the orginal Whisper paper since the main goal here is
    # to check for regressions
    _wer = load("wer")
    wer_score = _wer.compute(predictions=[prediction], references=[reference])
    wer_score = wer_score * 100
    return wer_score, str(_time)


def main():
    print("Benchmark whisper inference")

    inference_dir = os.path.join(os.getcwd(), "inference/")
    isExist = os.path.exists(inference_dir)
    if not isExist:
        os.makedirs(inference_dir)

    models = ["small"]
    audios = ["samples/15GdH9-curt.mp3"]

    models = ["small", "medium"]
    audios = [
        "samples/15GdH9-curt.mp3",
        "samples/Ona_catalan-balear.mp3",
        "samples/Son_Goku_catalan_valencian_voice.ogg",
    ]
    results = []
    for model in models:
        results_model = []
        total_wer = 0
        for audio in audios:
            wer_score, _time = inference(audio, model, inference_dir)
            result = {"audio": audio, "wer": f"{wer_score:.2f}", "time": _time}
            results_model.append(result)
            total_wer += wer_score

        avg_wer = total_wer / len(audios)
        result = {"avg_wer": f"{avg_wer:.2f}"}
        results_model.append(result)
        results.append({model: results_model})

    json_data = json.dumps(results, indent=4)
    with open("results.json", "w") as outfile:
        outfile.write(json_data)

    print(results)


if __name__ == "__main__":
    main()
