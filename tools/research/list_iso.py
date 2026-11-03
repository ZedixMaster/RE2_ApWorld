import argparse
from collections import Counter

import pycdlib


def list_files(iso_path):
    iso = pycdlib.PyCdlib()
    iso.open(iso_path)
    try:
        files = []
        for directory, _subdirectories, filenames in iso.walk(iso_path="/"):
            for filename in filenames:
                path   = f"{directory.rstrip('/')}/{filename}"
                record = iso.get_record(iso_path=path)
                files.append((record.extent_location(), record.data_length, path))

        return files
    finally:
        iso.close()


def print_listing(files):
    for sector, size, path in sorted(files):
        print(f"{sector:>8} {size:>10} {path}")


def print_summary(files):
    extensions = Counter(path.split(";")[0].rsplit(".", 1)[-1].upper() for _, _, path in files)
    print(f"\n{len(files)} files")
    for extension, count in extensions.most_common():
        print(f"  {extension:<8} {count}")

    print("\nLargest 20 files:")
    for _, size, path in sorted(files, key=lambda file: file[1], reverse=True)[:20]:
        print(f"{size:>10} {path}")


def main():
    parser = argparse.ArgumentParser(description="List every file in an ISO with its start sector and size")
    parser.add_argument("iso_path")
    args = parser.parse_args()

    files = list_files(args.iso_path)
    print_listing(files)
    print_summary(files)


if __name__ == "__main__":
    main()