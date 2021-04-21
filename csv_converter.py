import pandas as pd


def get_data(filename_read_from, unique_identifier, column_name, file_write_to):
    covid_data_frame = pd.read_csv(filename_read_from, dtype="category", sep=",")
    countries = covid_data_frame[unique_identifier]
    dynamic_data = covid_data_frame[column_name]


    final_countries = []
    final_dynamic_data = []


    for x in range(0, len(countries)):
        if countries[x] not in final_countries:
            final_countries.append(countries[x])
            final_dynamic_data.append(dynamic_data[x])
        else:
            index = final_countries.index(countries[x])
            final_dynamic_data[index] = final_dynamic_data[index] + dynamic_data[x]

    with open(file_write_to, "w") as write_to_file:
        write_to_file.write(unique_identifier + "," + column_name + "\n")
        for y in range(0, len(final_countries)):
            line_to_write = str(final_countries[y]) + "," + str(final_dynamic_data[y]) + "\n"
            write_to_file.write(line_to_write)

get_data(input("Skriv namnet på filen du vill läsa ifrån: "), input("Skriv namnet på den unika identifierare du vill använda (Ex. Country_Region): "), input("Skriv namnet på kolumnen du vill ha data från (case sensitive): "), input("Skriv namnet på filen du vill ha som resultat (inklusive .csv): "))