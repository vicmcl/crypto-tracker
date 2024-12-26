import sys

sys.path.append("..")

from tools.get_account_info import get_account_info


def main():
    date = "2023-12-19"
    df = get_account_info(date)
    print(df)


if __name__ == "__main__":
    main()
