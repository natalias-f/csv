#! /usr/bin/python
import csv
import sys
import os
import argparse


def import_csv(file):
    with open(file, 'r') as data:
        data_list = []
        for line in csv.DictReader(data):
            data_list.append(line)
        return data_list


def save_filtered_data(file, filtered_data):

    dir_name = os.path.dirname(file)
    file_name = os.path.basename(file)
    new = file_name.split('.', 1)
    new.insert(-1, '_filtered.')
    new_file = ''.join(new)
    if dir_name:
        new_file_name = os.path.join(dir_name, new_file)
    else:
        new_file_name = os.path.join(new_file)
    with open(new_file_name, 'w', newline='') as csvfile:
        fieldnames = [key for key in filtered_data[0]]
        print(fieldnames)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in filtered_data:
            print(row)
            writer.writerow(row)


def check_filter(row, filters):
    condition = 1
    for f in filters:
       # print(row, f['column'], f['value'])
        if row[f['column']] == f['value']:
            condition *= 1
        else:
            condition *= 0
    return bool(condition)


def filter_parser(filter_table):
    filters = []
    for f in filter_table:
        temp = (f.split('=', 1))
        filters.append({'column': temp[0], 'value': temp[1]})

    #print(filters)
    return filters


def main(argv):
    parser = argparse.ArgumentParser('Program reads csv file from stdin and outputs csv file on stdout ')
    parser.add_argument('-i', '--input', help='file path')
    parser.add_argument('pk', help='column name with PK')
    parser.add_argument('fk', help='column name with FK')
    parser.add_argument('-f', '--filter', action='append', help='filter expression in format column=value (can be specified multiple times, logical AND is applied)')
    args = parser.parse_args(argv)

    #print(f'{args.filter}')
    filters = filter_parser(args.filter)
    data = import_csv(args.input)

    to_be_deleted = []
    for row in data:
        if check_filter(row, filters):
            to_be_deleted.append(row[args.pk])
    print(f'Rows matched by filters: {len(to_be_deleted)}', file=sys.stderr)

    filtered_data = []
    missing_references = 0
    for row in data:
        if row[args.pk] in to_be_deleted:
            pass
        else:
            if row[args.fk] == '':
                filtered_data.append(row)
            else:
                temp = row[args.fk].split(':')
                if temp[1] in to_be_deleted:
                    missing_references += 1
                else:
                    filtered_data.append(row)
    print(f'Rows with deleted parent: {missing_references}', file=sys.stderr)
    print(f'Input rows: {len(data)}', file=sys.stderr)
    print(filtered_data)
    save_filtered_data(args.input, filtered_data)


if __name__ == '__main__':
    main(sys.argv[1:])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
