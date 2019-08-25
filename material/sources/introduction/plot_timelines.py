import sys, csv
import numpy as np
import matplotlib.pyplot as plt

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
    plt.show()





if __name__=='__main__':
    plot_timelines(*sys.argv[1:])