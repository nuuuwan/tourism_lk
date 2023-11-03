from tlk import DataReadMe, StatisticsPage


def main():
    pdf_link_list = StatisticsPage().scrape()
    DataReadMe.update(
        pdf_link_list=pdf_link_list,
    )


if __name__ == '__main__':
    main()
