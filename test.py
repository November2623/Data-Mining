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
                              names=["UserID", "MovieID", "Rating", "Timestamp"])
    all_ratings["Favorable"] = all_ratings["Rating"] > 3
    # Sample the dataset. You can try increasing the size of the sample, but the run time will be considerably longer
    ratings = all_ratings[all_ratings['UserID'].isin(range(200))]  # & ratings["UserID"].isin(range(100))]
    # We start by creating a dataset of each user's favourable reviews
    favorable_ratings = ratings[ratings["Favorable"]]
    # We are only interested in the reviewers who have more than one review
    favorable_reviews_by_users = dict((k, frozenset(v.values)) for k, v in favorable_ratings.groupby("UserID")["MovieID"])
    num_favorable_by_movie = ratings[["MovieID", "Favorable"]].groupby("MovieID").sum()
    print(num_favorable_by_movie)
    num_favorable_by_movie2 = ratings.groupby("UserID")

    print(num_favorable_by_movie2["UserID"].count)
    total_rows = num_favorable_by_movie["Favorable"].count()

    print(total_rows)
    
    frequent_itemsets = {}  # itemsets are sorted by length
    min_support = 50

    # k=1 candidates are the isbns with more than min_support favourable reviews
    frequent_itemsets[1] = dict((frozenset((movie_id,)), row["Favorable"])
                                    for movie_id, row in num_favorable_by_movie.iterrows()
                                    if (row["Favorable"]/total_rows) >= min_support/100)
    print(frequent_itemsets[1])
    print("There are {} movies with more than {} favorable reviews".format(len(frequent_itemsets[1]), min_support))
    sys.stdout.flush()
    for k in range(2, 20):
        # Generate candidates of length k, using the frequent itemsets of length k-1
        # Only store the frequent itemsets
        cur_frequent_itemsets = find_frequent_itemsets(favorable_reviews_by_users, frequent_itemsets[k-1],
                                                    min_support)
        if len(cur_frequent_itemsets) == 0:
            print("Did not find any frequent itemsets of length {}".format(k))
            sys.stdout.flush()
            break
        else:
            print("I found {} frequent itemsets of length {}".format(len(cur_frequent_itemsets), k))
            #print(cur_frequent_itemsets)
            sys.stdout.flush()
            frequent_itemsets[k] = cur_frequent_itemsets
    # We aren't interested in the itemsets of length 1, so remove those
    del frequent_itemsets[1]
    print("Found a total of {0} frequent itemsets".format(sum(len(itemsets) for itemsets in frequent_itemsets.values())))
    candidate_rules = []
    for itemset_length, itemset_counts in frequent_itemsets.items():
        for itemset in itemset_counts.keys():
            for conclusion in itemset:
                premise = itemset - set((conclusion,))
                candidate_rules.append((premise, conclusion))
    print("There are {} candidate rules".format(len(candidate_rules)))
# Now, we compute the confidence of each of these rules. This is very similar to what we did in chapter 1
    correct_counts = defaultdict(int)
    incorrect_counts = defaultdict(int)
    for user, reviews in favorable_reviews_by_users.items():
        for candidate_rule in candidate_rules:
            premise, conclusion = candidate_rule
            if premise.issubset(reviews):
                if conclusion in reviews:
                    correct_counts[candidate_rule] += 1
                else:
                    incorrect_counts[candidate_rule] += 1
    rule_confidence = {candidate_rule: correct_counts[candidate_rule] / float(correct_counts[candidate_rule] + incorrect_counts[candidate_rule])
                for candidate_rule in candidate_rules}
    
    # Choose only rules above a minimum confidence level
    min_confidence = 0.9

    # Filter out the rules with poor confidence
    rule_confidence = {rule: confidence for rule, confidence in rule_confidence.items() if confidence > min_confidence}
    print(len(rule_confidence))
    sorted_confidence = sorted(rule_confidence.items(), key=itemgetter(1), reverse=True)

    # # for index in range(5):
    # print("Rule #{0}".format(index + 1))
    # (premise, conclusion) = sorted_confidence[index][0]
    # print("Rule: If a person recommends {0} they will also recommend {1}".format(premise, conclusion))
    # print(" - Confidence: {0:.3f}".format(rule_confidence[(premise, conclusion)]))
    # print("")

if __name__ == '__main__':
    main()
