import argparse
import copy
import json
import time
from collections import defaultdict

from surya.input.load import load_from_folder, load_from_file
from surya.model.detection.model import load_model, load_processor
from surya.detection import batch_text_detection
from surya.postprocessing.affinity import draw_lines_on_image
from surya.postprocessing.heatmap import draw_polys_on_image
from surya.settings import settings
import os
from tqdm import tqdm


def surya_detect(
        input_path: str,
        results_dir: str = None,
        max_pages: int = None,
        images: bool = False,
        debug: bool = False
    ):
    # parser = argparse.ArgumentParser(description="Detect bboxes in an input file or folder (PDFs or image).")
    # parser.add_argument("input_path", type=str, help="Path to pdf or image file or folder to detect bboxes in.")
    # parser.add_argument("--results_dir", type=str, help="Path to JSON file with OCR results.", default=os.path.join(settings.RESULT_DIR, "surya"))
    # parser.add_argument("--max", type=int, help="Maximum number of pages to process.", default=None)
    # parser.add_argument("--images", action="store_true", help="Save images of detected bboxes.", default=False)
    # parser.add_argument("--debug", action="store_true", help="Run in debug mode.", default=False)
    # args = parser.parse_args()

    checkpoint = settings.DETECTOR_MODEL_CHECKPOINT
    model = load_model(checkpoint=checkpoint)
    processor = load_processor(checkpoint=checkpoint)

    if os.path.isdir(input_path):
        images, names = load_from_folder(input_path, max_pages)
        # folder_name = os.path.basename(input_path)
    else:
        images, names = load_from_file(input_path, max_pages)
        # folder_name = os.path.basename(input_path).split(".")[0]

    predictions = batch_text_detection(images, model, processor)
    # result_path = os.path.join(results_dir, folder_name)
    # os.makedirs(result_path, exist_ok=True)

    # if images:
    #     for idx, (image, pred, name) in enumerate(zip(images, predictions, names)):
    #         polygons = [p.polygon for p in pred.bboxes]
    #         bbox_image = draw_polys_on_image(polygons, copy.deepcopy(image))
    #         bbox_image.save(os.path.join(result_path, f"{name}_{idx}_bbox.png"))

    #         column_image = draw_lines_on_image(pred.vertical_lines, copy.deepcopy(image))
    #         column_image.save(os.path.join(result_path, f"{name}_{idx}_column.png"))

    #         if debug:
    #             heatmap = pred.heatmap
    #             heatmap.save(os.path.join(result_path, f"{name}_{idx}_heat.png"))

    #             affinity_map = pred.affinity_map
    #             affinity_map.save(os.path.join(result_path, f"{name}_{idx}_affinity.png"))

    predictions_by_page = defaultdict(list)
    for idx, (pred, name, image) in enumerate(zip(predictions, names, images)):
        out_pred = pred.model_dump(exclude=["heatmap", "affinity_map"])
        out_pred["page"] = len(predictions_by_page[name]) + 1
        predictions_by_page[name].append(out_pred)

    return predictions_by_page






