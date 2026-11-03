import argparse
import os

RAW_SECTOR_SIZE        = 2352
DATA_OFFSET            = 24
DATA_SIZE              = 2048
SYNC_PATTERN           = bytes([0x00] + [0xFF] * 10 + [0x00])
ISO_SIGNATURE          = b"CD001"
ISO_DESCRIPTION_SECTOR = 16

def convert(bin_path, iso_path):
    bin_size = os.path.getsize(bin_path)
    if bin_size % RAW_SECTOR_SIZE != 0:
        raise ValueError(f"{bin_path} is {bin_size} bytes, not a multiple of {RAW_SECTOR_SIZE}")

    sector_count = 0
    with open(bin_path, "rb") as src, open(iso_path, "wb") as dst:
        while True:
            sector = src.read(RAW_SECTOR_SIZE)
            if not sector:
                break
            if sector[:len(SYNC_PATTERN)] != SYNC_PATTERN:
                raise ValueError(f"Sector {sector_count} has no sync pattern")
            dst.write(sector[DATA_OFFSET:DATA_OFFSET + DATA_SIZE])
            sector_count += 1

    return sector_count

def verify(iso_path, sector_count):
    expected_size = sector_count * DATA_SIZE
    actual_size   = os.path.getsize(iso_path)
    if actual_size != expected_size:
        raise ValueError(f"ISO is {actual_size} bytes, expected {expected_size}")

    with open(iso_path, "rb") as iso:
        iso.seek(ISO_DESCRIPTION_SECTOR * DATA_SIZE)
        descriptor = iso.read(6)

    if descriptor[1:6] != ISO_SIGNATURE:
        raise ValueError(f"No ISO signature found, got {descriptor!r}")

    print(f"OK: {sector_count} sectors, {actual_size} bytes")

def main():
    parser = argparse.ArgumentParser(description="Convert a raw MODE2/2352 PS1 .bin track to a 2048-byte .iso")
    parser.add_argument("bin_path")
    parser.add_argument("iso_path")
    args = parser.parse_args()

    sector_count = convert(args.bin_path, args.iso_path)
    verify(args.iso_path, sector_count)

if __name__ == "__main__":
    main()