from tlk import DataReadMe
from workflows import parse, scrape


def main():
    pdf_link_list = scrape.main()
    parse.main()

    DataReadMe.update(
        pdf_link_list=pdf_link_list,
    )


if __name__ == '__main__':
    main()
