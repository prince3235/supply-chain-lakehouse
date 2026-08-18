import argparse
from .run import run

def main():
    parser = argparse.ArgumentParser(description="Ingestion Pipeline")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dataset", nargs="+")
    parser.add_argument("--quality", default="clean", choices=["clean", "dirty"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", default="configs/ingestion.yaml")
    
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()
