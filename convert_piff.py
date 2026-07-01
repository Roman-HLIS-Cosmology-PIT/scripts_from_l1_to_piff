from pyimcom.utils.piffutils import piff_to_legendre_multi
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file")
    parser.add_argument("--output_file")
    args = parser.parse_args()

    piff_to_legendre_multi(args.input_file, args.output_file, "L2_2506")

if __name__ == "__main__":
    main()