import sys, csv, re
import numpy as np
import matplotlib.pyplot as plt

def plot_medline_trends(*filenames):
    for filename in filenames:
        # extract data
        data = np.genfromtxt(filename, skip_header=1, skip_footer=1, dtype=np.dtype([('f1', np.int), ('f2', np.int), ('f3', np.float16)]), names=True)

        # extract meta data
        label_mapping = {'Number': 'count', 'Year': 'year', '000': 'fraction'}
        with open(filename, 'r') as f:
            label = re.sub('<[^<]+?>', '', f.readline().strip('Medline trend for ').strip()).replace('+',' ')

        # rescaling
        data['000'] = data['000'] / (10**5)

        # manual scaling
        if label == 'reproducibility':
            f = 15*5
            data['Number'] = data['Number'] / f
            data['000'] = data['000'] / f
            label += ' (downscaled x{})'.format(f)

        # manual scaling
        if label == 'repeatability':
            f = 5
            data['Number'] = data['Number'] / f
            data['000'] = data['000'] / f
            label += ' (downscaled x{})'.format(f)

        # plot bar plot with frame
        plt.bar(data['Year'], data['000'], width=1, alpha=0.3, label=label)
        names = data.dtype.names
        restructured_data = np.empty([2*len(data)], dtype=np.dtype([(names[0], np.float16), (names[1], np.float), (names[2], np.float16)]))
        restructured_data[0::2] = restructured_data[1::2] = data
        restructured_data[0::2]['Year'] = data['Year'] + 0.5
        restructured_data[1::2]['Year'] = data['Year'] - 0.5

        plt.plot(restructured_data['Year'], restructured_data['000'])
    plt.xlabel(label_mapping['Year'])
    plt.ylabel(label_mapping['000'])
    plt.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-1, 1))
    plt.tight_layout()
    plt.xlim(1970, 2018)

    plt.savefig('trends.svg', format='svg')
    # plt.show()

def plot_timelines(*filenames):
    for filename in filenames:
        with open(filename, 'r') as csvfile:
            year, count = [], []
            plot_label = ''
            x_label, y_label = '', ''
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for r, row in enumerate(spamreader):
                if not row:
                    continue
                if r == 0:
                    # extract label
                    plot_label = row[0].strip('pubmed - ')
                    continue
                if r==1:
                    x_label, y_label = row
                    continue
                year.append(row[0])
                count.append(row[1])

            year, count = np.asarray(year, dtype=int), np.asarray(count,dtype=int)

            if plot_label == 'Reproducibility':
                f = 100
                plot_label += ' (x{})'.format(f)
                count = count / f

            if plot_label == 'Repeatability':
                f = 10
                plot_label += ' (x{})'.format(f)
                count = count / f

            plt.bar(year, count, width=1, alpha=0.3, label=plot_label)
            linex, liney = [], []
            for y, c in zip(year[::-1], count[::-1]):
                linex.extend([y-0.5,y+0.5])
                liney.extend([c,c])
            linex, liney = np.asarray(linex), np.asarray(liney)
            plt.plot(linex, liney)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.legend()
            plt.xlim(1980,2020)

    plt.savefig('timelines.svg', format='svg')
    # plt.show()





if __name__=='__main__':
    plot_medline_trends(*sys.argv[1:])
    # plot_timelines(*sys.argv[1:])
