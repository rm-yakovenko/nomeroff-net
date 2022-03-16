import warnings
import os
from glob import glob

from _paths import nomeroff_net_dir
from nomeroff_net import pipeline

warnings.filterwarnings("ignore")
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

if __name__ == '__main__':
    number_plate_detection_and_reading = pipeline(
        "number_plate_detection_and_reading_runtime",
        image_loader="opencv"  # Try 'turbo' for faster performance.
    )

    num_run = 1
    batch_size = 1
    num_workers = 1
    images = glob(os.path.join(nomeroff_net_dir, "./data/examples/benchmark_oneline_np_images/1.jpeg"))

    number_plate_detection_and_reading.clear_stat()

    for i in range(num_run):
        print(f"pass {i}")
        outputs = number_plate_detection_and_reading(images,
                                                     batch_size=batch_size,
                                                     num_workers=num_workers)

    timer_stat = number_plate_detection_and_reading.get_timer_stat(len(images)*num_run)

    print(f"Processed {len(images)} photos")
    print(f"One photo process {timer_stat['NumberPlateDetectionAndReadingRuntime.call']} seconds")
    print()
    print(f"detect_bbox_time_all {timer_stat['NumberPlateLocalization.call']} per one photo")
    print(f"craft_time_all {timer_stat['NumberPlateKeyPointsDetection.call']} per one photo")
    print(f"classification_time_all {timer_stat['NumberPlateClassification.call']} per one photo")
    print(f"ocr_time_all {timer_stat['NumberPlateTextReading.call']} per one photo")