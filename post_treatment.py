from const import WORKING_DIR
from pathlib import Path
from hashlib import sha256
import cv2

def remove_hash_dup(im_dir:Path) :
    hash_duplicate_dir = im_dir.joinpath("hash_dup")
    hash_duplicate_dir.mkdir(exist_ok=True)

    total = len(list(im_dir.iterdir()))
    unique_hash = set()
    for index, file in enumerate(im_dir.iterdir()) :

        if not(file.is_file()) :
            continue

        with file.open("rb") as file_fd :
            content = file_fd.read()
        H = sha256(content).hexdigest()
        if H in unique_hash :
            file.rename(hash_duplicate_dir.joinpath(file.name))
        else : 
            unique_hash.add(H)


        if index % 10 == 0 :
            print(f"{index}/{total}")
    print(f"total={total}, unique_hash={len(unique_hash)}")

def remove_histograms_dup(im_dir:Path) :
    histograms_dup_dir = im_dir.joinpath("../histograms_dup")
    histograms_dup_dir.mkdir(exist_ok=True)

    total = len(list(im_dir.iterdir()))

    for file in im_dir.iterdir() :
        



if __name__ == "__main__" :

    im_dir = WORKING_DIR.joinpath("harvest_1015000359716003860_2026-02-07-044812/attachements/image")
    # remove_hash_dup(im_dir)
    remove_histograms_dup(im_dir)