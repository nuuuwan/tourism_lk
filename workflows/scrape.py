from tlk import DataReadMe, StatisticsPage


def main():
    d = StatisticsPage().scrape()
    DataReadMe.update(
        n_pdf_links=d['n_pdf_links'],
    )


if __name__ == '__main__':
    main()
