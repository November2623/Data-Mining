import argparse
import csv
import sys
import pandas as pd
from collections import defaultdict
from operator import itemgetter


def parse_option():
    parser = argparse.ArgumentParser(description='Apriori algorithm')
    parser.add_argument('-f', "--input_file", dest='filename', help="file  containing csv", required=True)
    parser.add_argument('-s', '--min_support', dest='min_support', help="min support", type=float)
    parser.add_argument('-c', '--min_confidence', dest='min_confidence', help="minium confidence", type=float)
    return parser.parse_args()

def find_frequent_itemsets(favorable_reviews_by_users, k_1_itemsets, min_support):
    counts = defaultdict(int)
    for user, reviews in favorable_reviews_by_users.items():
        for itemset in k_1_itemsets:
            if itemset.issubset(reviews):
                for other_reviewed_movie in reviews - itemset:
                    current_superset = itemset | frozenset((other_reviewed_movie,))
                    counts[current_superset] += 1
    return dict([(itemset, frequency) for itemset, frequency in counts.items() if frequency >= min_support])


def main():
    args = parse_option()
    all_ratings = pd.read_csv(args.filename, header=None,
                              names=["ID", "Object", "Rating", "Timestamp"])