from tlk import StatisticsPage


def main():
    pdf_link_list = StatisticsPage().scrape()
    return pdf_link_list


if __name__ == '__main__':
    main()
