#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023-2024 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import json
import unicodedata
import re


def _normalize_string(result):
    result = unicodedata.normalize("NFC", result)

    result = result.translate(str.maketrans("\r\n\t", "   "))
    result = re.sub(
        r"\s+", " ", result
    )  # replace any successive whitespace characters with a space

    return result


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

    cmd = f"whisper-ctranslate2 --language ca --device cuda --output_dir {inference_dir} --model {model} {input_file}"
    print(cmd)
    os.system(cmd)

    _time = round((datetime.datetime.now() - start_time).total_seconds())

    with open(reference_file) as f:
        reference = _normalize_string(f.read())

    with open(prediction_file) as f:
        prediction = _normalize_string(f.read())

    _wer = load("wer")
    wer_score = _wer.compute(predictions=[prediction], references=[reference])
    wer_score = wer_score * 100
    return wer_score, _time


def main():
    print("Benchmark whisper inference")

    inference_dir = os.path.join(os.getcwd(), "inference/")
    isExist = os.path.exists(inference_dir)
    if not isExist:
        os.makedirs(inference_dir)

    models = ["small", "medium"]
    audios = [
        "samples/15GdH9-curt.mp3",
        "samples/EloiBadiaCat.mp3",
        "samples/Son_Goku_catalan_valencian_voice.ogg",
        "samples/Universal_Declaration_of_Human_Rights_-_cat_-_nv.ogg",
        "samples/Ona_catalan-balear.mp3",
    ]

    # Time in seconds of the audios for RTF metric calculation
    audios_secs = [300, 209, 83, 811, 139]

    N_BATCHES = 3
    results = []
    total_time = 0
    total_wer = 0
    total_audio_time = 0

    for model in models:
        results_model = []
        model_wer = 0
        wers = {}

        for batch in range(0, N_BATCHES):
            for idx in range(0, len(audios)):
                audio = audios[idx]
                wer_score, _time = inference(audio, model, inference_dir)
                total_wer += wer_score
                total_time += _time
                total_audio_time += audios_secs[idx]
                _wer = wers.get(audio, [])
                _wer.append(wer_score)
                wers[audio] = _wer
                model_wer += wer_score

        for audio, audio_wers in wers.items():
            wer_score = sum(audio_wers) / len(audio_wers)
            result = {"audio": audio, "wer": f"{wer_score:.2f}"}
            results_model.append(result)

        avg_wer = model_wer / len(audios) / N_BATCHES
        result = {"avg_wer": f"{avg_wer:.2f}"}
        results_model.append(result)
        results.append({model: results_model})

    processed = len(audios) * len(models) * N_BATCHES
    times_audios_processed = len(models)
    rtf = (total_time / times_audios_processed) / total_audio_time
    totals = {
        "wer": f"{total_wer / processed:.2f}",
        "rtf": f"{rtf:.2f}",
        "time": f"{total_time}",
    }

    results.append({"totals": totals})

    json_data = json.dumps(results, indent=4)
    with open("results.json", "w") as outfile:
        outfile.write(json_data)

    print(totals)


if __name__ == "__main__":
    main()
